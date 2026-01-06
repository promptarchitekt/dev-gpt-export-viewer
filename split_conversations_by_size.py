#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Split a huge ChatGPT `conversations.json` into manageable parts without loading
the whole file into memory. Creates:
- conversations_part_XXX.json  (arrays of conversation objects)
- index.csv  (conversation_id, title, messages, first_ts, last_ts, part_file)
- messages.csv  (conversation_id, title, ts, role, text)  [optional with --csv]

Usage:
  python split_conversations_by_size.py -i conversations.json --max-convs 200 --max-bytes 50MB --csv
"""
import argparse, csv, datetime as dt, io, json, os, re, sys
from typing import Iterator, Dict, Any, Optional, Tuple

def parse_size(s: str) -> int:
    m = re.match(r"^\s*(\d+)([kKmMgG][bB]?)?\s*$", s or "")
    if not m:
        raise argparse.ArgumentTypeError("Ungültige Größe: %r" % s)
    n = int(m.group(1))
    suffix = (m.group(2) or "").lower()
    mult = 1
    if suffix.startswith("k"): mult = 1024
    elif suffix.startswith("m"): mult = 1024**2
    elif suffix.startswith("g"): mult = 1024**3
    return n * mult

def iter_top_level_objects(path: str) -> Iterator[Dict[str, Any]]:
    """Stream parser for a JSON array of objects without loading entire file."""
    with open(path, "r", encoding="utf-8") as f:
        # Seek first '['
        ch = f.read(1)
        while ch and ch != '[':
            ch = f.read(1)
        if ch != '[':
            raise ValueError("Datei ist kein JSON-Array.")
        # Consume until first non-space or closing bracket
        while True:
            ch = f.read(1)
            if not ch:
                return
            if ch.isspace():
                continue
            if ch == ']':
                return
            break
        # Now ch should be '{' (start of an object)
        while True:
            buf = io.StringIO()
            depth = 0
            in_str = False
            esc = False

            # We are at first char of the object ('{')
            while True:
                if not ch:
                    break
                buf.write(ch)
                if in_str:
                    if esc:
                        esc = False
                    elif ch == "\\":
                        esc = True
                    elif ch == '"':
                        in_str = False
                else:
                    if ch == '"':
                        in_str = True
                    elif ch == '{':
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            break
                ch = f.read(1)

            obj_text = buf.getvalue()
            if obj_text.strip():
                try:
                    yield json.loads(obj_text)
                except Exception as e:
                    # Write context to help debugging
                    raise RuntimeError(f"JSON-Fehler: {e}\nAusschnitt: {obj_text[:200]}...") from e

            # Move to the start of the next object (or end ']')
            while True:
                ch = f.read(1)
                if not ch:
                    return
                if ch.isspace():
                    continue
                if ch == ',':
                    # move to next non-space
                    while True:
                        ch = f.read(1)
                        if not ch:
                            return
                        if ch.isspace():
                            continue
                        break
                    # ch is next object's first char or ']'
                    if ch == ']':
                        return
                    break
                elif ch == ']':
                    return
                else:
                    # ch is next object's first char
                    break

def clean_text_from_message_content(content: Any) -> str:
    # Export formats vary: sometimes {"parts": ["text"...]}, sometimes arrays of dicts, tools, images, etc.
    if content is None:
        return ""
    if isinstance(content, dict) and "parts" in content:
        parts = content.get("parts", [])
        texts = []
        for p in parts:
            if isinstance(p, str):
                texts.append(p)
            elif isinstance(p, dict):
                # OpenAI often uses {"text": "..."} for structured content
                if "text" in p and isinstance(p["text"], str):
                    texts.append(p["text"])
        return "\n".join(texts)
    if isinstance(content, list):
        texts = []
        for p in content:
            if isinstance(p, str):
                texts.append(p)
            elif isinstance(p, dict):
                if "text" in p and isinstance(p["text"], str):
                    texts.append(p["text"])
        return "\n".join(texts)
    if isinstance(content, str):
        return content
    return ""

def summarize_conversation(conv: Dict[str, Any]) -> Tuple[int, Optional[float], Optional[float]]:
    mapping = conv.get("mapping") or {}
    first_ts = last_ts = None
    msg_count = 0
    for node in mapping.values():
        msg = (node or {}).get("message") or {}
        role = (msg.get("author") or {}).get("role")
        if role in ("user", "assistant"):
            msg_count += 1
        ts = msg.get("create_time")
        if isinstance(ts, (int, float)):
            first_ts = ts if first_ts is None else min(first_ts, ts)
            last_ts = ts if last_ts is None else max(last_ts, ts)
    return msg_count, first_ts, last_ts

def iso_from_ts(ts: Optional[float]) -> Optional[str]:
    if ts is None:
        return None
    try:
        return dt.datetime.fromtimestamp(ts).isoformat()
    except Exception:
        return None

def write_part(part_idx: int, objs: list, out_dir: str) -> str:
    fn = os.path.join(out_dir, f"conversations_part_{part_idx:03d}.json")
    # Schreibe mit beibehaltener Unicode-Darstellung, ersetze jedoch
    # die seltenen Unicode-Zeilenseparatoren U+2028/U+2029 durch
    # \u-Escapes, damit Editoren keine Warnung zu "unusual line terminators" zeigen.
    text = json.dumps(objs, ensure_ascii=False)
    text = text.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    with open(fn, "w", encoding="utf-8") as w:
        w.write(text)
    return fn

def main():
    ap = argparse.ArgumentParser(description="Split ChatGPT conversations.json in Teile.")
    ap.add_argument("-i", "--input", default="conversations.json", help="Pfad zu conversations.json")
    ap.add_argument("-o", "--out-dir", default="parts", help="Zielordner")
    ap.add_argument("--max-convs", type=int, default=200, help="max. Unterhaltungen pro Teil")
    ap.add_argument("--max-bytes", type=parse_size, default=parse_size("50MB"), help="max. Dateigröße pro Teil, z.B. 50MB")
    ap.add_argument("--csv", action="store_true", help="auch eine messages.csv erzeugen")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    index_path = os.path.join(args.out_dir, "index.csv")
    # UTF-8 mit BOM (utf-8-sig), damit Excel unter Windows Umlaute sicher korrekt erkennt
    idx_f = open(index_path, "w", newline="", encoding="utf-8-sig")
    idx_writer = csv.writer(idx_f)
    idx_writer.writerow(["conversation_id","title","messages","first_time","last_time","part_file"])

    msg_writer = None
    if args.csv:
        # Auch hier utf-8-sig für bessere Excel-Kompatibilität
        msg_f = open(os.path.join(args.out_dir, "messages.csv"), "w", newline="", encoding="utf-8-sig")
        msg_writer = csv.writer(msg_f)
        msg_writer.writerow(["conversation_id","title","time","role","text"])

    buf, part_idx, cur_bytes = [], 1, 0

    def flush():
        nonlocal buf, part_idx, cur_bytes
        if not buf:
            return None
        fn = write_part(part_idx, buf, args.out_dir)
        part_idx += 1
        cur_bytes = 0
        buf = []
        return fn

    for conv in iter_top_level_objects(args.input):
        # Prepare stats for index
        conv_id = conv.get("id")
        title = conv.get("title")
        msgs, first_ts, last_ts = summarize_conversation(conv)

        # If CSV requested, stream messages out
        if msg_writer is not None:
            mapping = conv.get("mapping") or {}
            for node in mapping.values():
                msg = (node or {}).get("message") or {}
                role = (msg.get("author") or {}).get("role")
                if role not in ("user","assistant"):
                    continue
                ts = msg.get("create_time")
                txt = clean_text_from_message_content((msg.get("content") or {}))
                msg_writer.writerow([conv_id, title, iso_from_ts(ts), role, txt])

        # Calculate conversation size
        conv_bytes = len(json.dumps(conv, ensure_ascii=False).encode("utf-8"))
        
        # ✅ FIX 1+2: Flush BEFORE adding if would exceed limit (handles edge case: single conv > max_bytes)
        if buf and (len(buf) >= args.max_convs or cur_bytes + conv_bytes > args.max_bytes):
            flush()
        
        # Add to buffer
        buf.append(conv)
        cur_bytes += conv_bytes
        
        # ✅ FIX 3: Warn if single conversation exceeds max_bytes
        if conv_bytes > args.max_bytes:
            print(f"⚠️  Warning: Conversation {conv_id[:8] if conv_id else 'unknown'} "
                  f"({conv_bytes/1024/1024:.1f}MB) exceeds max_bytes limit", file=sys.stderr)

        # ✅ FIX 4: Determine part_file AFTER potential flush (ensures correct part index)
        part_name = f"conversations_part_{part_idx:03d}.json"
        idx_writer.writerow([conv_id, title, msgs, iso_from_ts(first_ts), iso_from_ts(last_ts), part_name])

    # flush remainder
    flushed = flush()
    if msg_writer is not None:
        msg_f.close()
    idx_f.close()

    print("Fertig. Teile liegen in:", os.path.abspath(args.out_dir))
    print("  - index.csv (Übersicht)")
    if os.path.exists(os.path.join(args.out_dir, "messages.csv")):
        print("  - messages.csv (alle Nachrichten tabellarisch)")
    for name in sorted(os.listdir(args.out_dir)):
        if name.startswith("conversations_part_") and name.endswith(".json"):
            print("  -", name)

if __name__ == "__main__":
    main()
