#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfacher Such- und Anzeige-Helfer für deinen ChatGPT-Export.

Nutzung (Beispiele):
  1) Suchen nach Titeln/IDs in messages.csv
     python chat_search_and_view.py -m parts_small_utf8/messages.csv --find "mein suchwort"

  2) Eine bestimmte Unterhaltung als HTML anzeigen (nach ID)
     python chat_search_and_view.py -m parts_small_utf8/messages.csv --export <conversation_id> -o chat_view.html

Hinweise:
- Die Datei messages.csv entsteht durch dein vorhandenes Skript.
- Umlaute werden korrekt angezeigt.
"""
import argparse, csv, html, os, sys

# Sehr lange Textfelder zulassen (große Antworten). Unter Windows kann sys.maxsize
# zu groß für das zugrunde liegende C-Long sein. Wir probieren fallend.
for limit in (2**31 - 1, 10**9, 10**8):
    try:
        csv.field_size_limit(limit)
        break
    except Exception:
        continue
from typing import List, Dict, Any


def read_messages_csv(messages_csv: str):
    with open(messages_csv, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            # Erwartete Spalten: conversation_id,title,time,role,text
            yield {
                "conversation_id": row.get("conversation_id"),
                "title": row.get("title"),
                "time": row.get("time"),
                "role": row.get("role"),
                "text": row.get("text", ""),
            }


def find_conversations(messages_csv: str, query: str, limit: int = 50):
    query_l = (query or "").lower()
    seen = {}
    results = []
    for msg in read_messages_csv(messages_csv):
        cid = msg["conversation_id"] or ""
        if cid in seen:
            continue
        title = msg["title"] or ""
        if query_l in cid.lower() or query_l in title.lower():
            seen[cid] = True
            results.append((cid, title))
            if len(results) >= limit:
                break
    return results


def collect_conversation(messages_csv: str, conv_id: str) -> List[Dict[str, Any]]:
    items = []
    for msg in read_messages_csv(messages_csv):
        if (msg.get("conversation_id") or "") == conv_id:
            items.append(msg)
    # Sortierung: nach Zeit (falls vorhanden), sonst Reihenfolge aus CSV
    items.sort(key=lambda x: (x.get("time") or ""))
    return items


def render_html(conversation: List[Dict[str, Any]], title: str, conv_id: str) -> str:
    def esc(s: str) -> str:
        return html.escape(s or "")

    # Sehr leichtes CSS für Chat-Ansicht
    css = """
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;background:#f6f7f9}
    header{position:sticky;top:0;background:#fff;border-bottom:1px solid #e3e6ea;padding:12px 16px}
    h1{font-size:18px;margin:0}
    .meta{color:#666;font-size:12px;margin-top:4px}
    .wrap{max-width:960px;margin:0 auto;padding:16px}
    .msg{margin:10px 0;display:flex}
    .role{width:120px;flex:0 0 120px;color:#555;font-weight:600}
    .bubble{flex:1;background:#fff;border:1px solid #e3e6ea;border-radius:8px;padding:10px;white-space:pre-wrap}
    .assistant .bubble{background:#f0f7ff;border-color:#cfe3ff}
    .time{color:#888;font-size:11px;margin-bottom:6px}
    footer{color:#888;font-size:12px;text-align:center;padding:12px}
    """

    parts = [
        "<!doctype html>",
        "<meta charset=\"utf-8\">",
        f"<title>{esc(title)} — {esc(conv_id)}</title>",
        f"<style>{css}</style>",
        "<header>",
        f"  <h1>{esc(title) if title else 'Unterhaltung'}</h1>",
        f"  <div class=\"meta\">ID: {esc(conv_id)}</div>",
        "</header>",
        "<div class=\"wrap\">",
    ]

    for m in conversation:
        role = (m.get("role") or "").lower()
        time = m.get("time") or ""
        text = m.get("text") or ""
        cls = "assistant" if role == "assistant" else "user" if role == "user" else "other"
        parts.append(f"  <div class=\"msg {cls}\">")
        parts.append(f"    <div class=\"role\">{esc(role)}</div>")
        parts.append("    <div class=\"bubble\">")
        if time:
            parts.append(f"      <div class=\"time\">{esc(time)}</div>")
        parts.append(f"      {esc(text)}")
        parts.append("    </div>")
        parts.append("  </div>")

    parts.append("</div>")
    parts.append("<footer>Erstellt aus messages.csv – Umlaute bleiben erhalten (UTF‑8).</footer>")
    return "\n".join(parts)


def autodetect_messages_csv() -> str:
    """Suche automatisch nach der besten messages.csv im Projektordner."""
    candidates = [
        os.path.join("parts_small_utf8", "messages.csv"),
        os.path.join("parts_small", "messages.csv"),
        os.path.join("parts", "messages.csv"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return ""


def main():
    ap = argparse.ArgumentParser(description="Suche & Anzeige für ChatGPT-Export (nutzt messages.csv)")
    ap.add_argument("-m", "--messages", required=False, default=None, help="Pfad zu messages.csv")
    ap.add_argument("--find", help="Suchwort für Titel oder ID (gibt Trefferliste aus)")
    ap.add_argument("--export", help="Conversation-ID, die als HTML ausgegeben werden soll")
    ap.add_argument("-o", "--output", default="chat_view.html", help="Ziel-HTML-Datei")
    args = ap.parse_args()

    messages_csv = args.messages or autodetect_messages_csv()
    if not messages_csv:
        print("Konnte messages.csv nicht finden. Bitte mit -m angeben (z. B. parts_small_utf8/messages.csv).")
        return 2
    if not os.path.exists(messages_csv):
        print(f"Datei nicht gefunden: {messages_csv}")
        return 2

    if args.find:
        hits = find_conversations(messages_csv, args.find)
        if not hits:
            print("Keine Treffer.")
            return
        print("Treffer (ID — Titel):")
        for cid, title in hits:
            print(f"{cid} — {title}")
        return

    if args.export:
        conv = collect_conversation(messages_csv, args.export)
        if not conv:
            print("Keine Nachrichten für diese ID gefunden.")
            return
        title = conv[0].get("title") or "Unterhaltung"
        html_text = render_html(conv, title, args.export)
        with open(args.output, "w", encoding="utf-8") as w:
            w.write(html_text)
        print(f"Fertig. Datei gespeichert: {os.path.abspath(args.output)}")
        return

    ap.print_help()


if __name__ == "__main__":
    main()
