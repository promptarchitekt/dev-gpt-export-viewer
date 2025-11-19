# GPT Export Viewer (Local, Privacy-First)

Ein leichtgewichtiges, reines HTML‑Tool zum lokalen Aufbereiten und Anzeigen eines ChatGPT‑Exports (`conversations.json`).

Fokus:

- Kein Upload – die Verarbeitung läuft vollständig im Browser (Chrome/Edge).
- Große Exporte werden speicherschonend gestreamt und in handliche Teile zerlegt.
- Übersicht und Suche: Index‑Ansicht, Chat‑Ansicht, Treffer‑Navigation (◀ ▶, Enter).
- Exporte (HTML/Markdown/TXT) via „Speichern unter“ Dialog.

## Features

- Aufbereitung
  - Zerlegt `conversations.json` in `Aufbereitung/Teile_XXMB` (10/20/50 MB).
  - Erstellt `Aufbereitung/Übersichten/index.csv` und `messages.csv` (UTF‑8 mit BOM).
  - Legt `Aufbereitung/Exporte/README.txt` an und speichert Einzelexporte dort.
- Anzeige
  - Liste (Titel/ID) + Chat mit Suche, Markierung, Treffer‑Sprung (◀ ▶ / Enter).
  - „Technische Einträge“ (z. B. Tool‑Calls) optional ein-/ausblendbar.
- Export
  - Einzeln als `HTML`, `Markdown (.md)` oder `Text (.txt)` – Dateiname `yymmdd_hhmm_Chatname`.

## Quick Start

1. Öffne die Datei `GPT-Export-Aufbereiter/chat_aufbereiten.html` im Chrome oder Edge.
2. Schritt 1 (aufklappbar)
   - Quelle: „Quelle wählen“ → `conversations.json` wählen (aus entzipptem Export).
   - Ziel: „Zielordner wählen“ → App legt dort `Aufbereitung/…` an.
   - „Aufbereitung starten“ → danach „Aufbereitungsordner öffnen“.
3. Schritt 2
   - Links: Liste (Suche nach Titel/ID).
   - Rechts: Chat‑Ansicht (Suche, Treffer‑Navigation, Export).

Browser‑Hinweise:

- Chrome/Edge empfohlen (File System Access API). Firefox/Safari funktionieren mit Export‑Download‑Fallback.

## Datenschutz & Sicherheit

- Verarbeitung ausschließlich lokal im Browser, keine Übertragung an Server.
- Schreib-/Lesezugriff erfolgt nur nach expliziter Freigabe über den Browserdialog.
- CSVs sind UTF‑8 mit BOM (Excel‑kompatibel). Umlaute bleiben korrekt.

## Ordnerstruktur (Ausgabe)

```
Aufbereitung/
  Exporte/
    README.txt
    <yymmdd_hhmm_Chatname>.{html|md|txt}
  Übersichten/
    index.csv
    messages.csv
  Teile_20MB/
    conversations_part_001.json
    conversations_part_002.json
    …
```

## Entwicklung

- Dieses Repo enthält eine eigenständige HTML‑App. Keine Build‑Schritte notwendig.
- Änderungen an UI‑Farben/CI sind lokal kapsuliert – keine externen Abhängigkeiten.

## Lizenz & Hinweise

- Ohne Lizenzdatei – bitte vor öffentlicher Wiederverwendung klären.

## Warum dieses Tool? (Pain‑Points)

- ChatGPT‑Exporte kommen als eine große `conversations.json` (teils >500 MB) – Editor/Excel stürzen ab oder frieren ein.
- Es gibt kaum GUI‑Werkzeuge für Nicht‑Techniker, die große Exporte lokal und datenschutzfreundlich aufbereiten.
- Viele Skripte erwarten Terminal‑Know‑how oder laden Daten in die Cloud – beides ist hier nicht nötig.
- Dieses Tool läuft rein lokal im Browser (Chrome/Edge) und führt dich in 3 Klicks von der Quelle zur Ansicht, inkl. Suche und Einzelexport.
- Ergebnis ist strukturiert und weiterverwendbar: handliche JSON‑Teile, `index.csv`, `messages.csv`, plus HTML/MD/TXT‑Export.

## Live‑Demo

- Vercel (static): Root leitet auf `GPT-Export-Aufbereiter/chat_aufbereiten.html`.
- Browser‑Hinweis: Chrome/Edge empfohlen (FS‑API). In Firefox/Safari ist Export per Download‑Fallback verfügbar.

## Lokales Starten (Windows `pwsh.exe`)

Die App ist eine rein statische HTML‑Anwendung. Es gibt keinen Build‑Schritt — du kannst die Dateien direkt im Browser öffnen oder einen kleinen HTTP‑Server starten.

- Schnell (Python, port 8000):

```powershell
cd 'C:\pa\07-dev-play\07_gpt_export_manager'
python -m http.server 8000
# öffne http://localhost:8000
```

- Mit Node/NPM (npx http-server, port 3000):

```powershell
cd 'C:\pa\07-dev-play\07_gpt_export_manager'
npx http-server . -p 3000
# öffne http://localhost:3000
```

- Oder per Doppelklick: `index.html` öffnen (leitet direkt zu `GPT-Export-Aufbereiter/chat_aufbereiten.html`).

Hinweis: Für die Aufbereitung großer Exporte empfiehlt sich Chrome oder Microsoft Edge (File System Access API).
