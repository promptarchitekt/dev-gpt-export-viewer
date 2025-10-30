# Sicherheit & Datenschutz

- Verarbeitung findet vollständig lokal im Browser statt. Es werden keine Daten an Server übertragen.
- Der Dateizugriff erfolgt nur nach expliziter Bestätigung über den Browser (File System Access API).
- CSV‑Dateien werden in UTF‑8 mit BOM erstellt (Excel‑kompatibel). Umlaute bleiben erhalten.
- „Ungewöhnliche Zeilentrenner“ (U+2028/U+2029) in JSON‑Teil‑Dateien werden maskiert, um Editor‑Warnungen zu vermeiden.
- Export erfolgt per „Speichern unter“‑Dialog. Bei nicht verfügbarer API wird ein Download‑Fallback genutzt.

Hinweis: In Firefox/Safari sind Schreibrechte eingeschränkt – Export funktioniert dort über Download‑Fallback.

