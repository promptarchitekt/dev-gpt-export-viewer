# Schnelle Hilfe: Riesige ChatGPT-Exporte verarbeiten

## Was ist das?
Ein kleines Python-Skript, das `conversations.json` **streamend** einliest (kein voller RAM‑Load)
und in mehrere handliche Dateien aufteilt. Optional erzeugt es außerdem eine `messages.csv`
zum Durchsuchen in Excel/Numbers.

## Nutzung
1) Lege `split_conversations_by_size.py` und deine `conversations.json` in denselben Ordner.
2) Öffne ein Terminal (PowerShell, cmd oder macOS/Linux Terminal).
3) Führe aus:

```bash
python split_conversations_by_size.py -i conversations.json --max-convs 200 --max-bytes 50MB --csv
```

Danach findest du im Ordner `parts/`:
- `conversations_part_001.json`, `..._002.json`, … (kleine Häppchen)
- `index.csv` (Übersicht über alle Unterhaltungen)
- `messages.csv` (alle Nachrichten zeilenweise – ideal zum Suchen/Filtern)

> Tipp: Passe `--max-convs` oder `--max-bytes` an, bis die Teile bequem zu öffnen/hochzuladen sind
  (z. B. 20MB oder 100 Unterhaltungen pro Datei).
