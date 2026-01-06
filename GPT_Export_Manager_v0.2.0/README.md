# GPT Export Manager v0.1.0 — Paket für Deployment

Dieses Paket enthält eine statische, privacy‑freundliche Viewer‑App zum lokalen Anzeigen und Aufbereiten von ChatGPT‑Exporten (`conversations.json`). Die App läuft komplett clientseitig im Browser; Server‑funktionen sind optional (Feedback‑Endpoint).

Kurz: Die Bereitstellung läuft automatisch via Vercel (GitHub → Vercel). Live‑Deploy (staging/preview + production) ist konfiguriert für das Repo.

Automatisches Deployment (bereits eingerichtet)

- Vercel Live: https://vercel.com/promptarchitekts-projects/dev-gpt-export-viewer
- Quell-Repository: https://github.com/promptarchitekt/dev-gpt-export-viewer/tree/main

Was in diesem Ordner liegt

- `index.html` — Root‑Landing (leitet auf die UI weiter)
- `GPT-Export-Aufbereiter/chat_aufbereiten.html` — die komplette, statische App (HTML + JS + CSS)
- `api/feedback.js` — optionaler Serverless‑Handler (nur aktiv, wenn auf Serverless deployed und `GH_TOKEN` + `GH_REPO` gesetzt)
- `vercel.json` — Vercel‑Konfiguration (Redirects / Einstellungen)
- `package.json` — Hilfs‑Scripts zum lokalen Testen (`start`, `serve-python`)

Schnellstart (lokal, PowerShell)

Python (kein Node erforderlich):

```powershell
cd 'C:\pa\07-dev-play\07_gpt_export_manager\GPT_Export_Manager_v0.1.0'
python -m http.server 8000
# öffne http://localhost:8000
```

Node (npx http-server):

```powershell
cd 'C:\pa\07-dev-play\07_gpt_export_manager\GPT_Export_Manager_v0.1.0'
npx http-server . -p 3000
# öffne http://localhost:3000
```

Hinweis zu Deployment & Feedback‑Endpoint

- Deploy auf Vercel: Pushs in `main` (bzw. in Branches) werden automatisch als Previews deployed; Production‑Deploys werden durch das GitHub‑→‑Vercel Setup ausgelöst. Die oben genannten Links zeigen das eingerichtete Vercel‑Projekt und das Quell‑Repo.
- `api/feedback.js` ist für Serverless Umgebungen vorbereitet. Wenn du GitHub‑Issues automatisch erstellen lassen willst, setzte `GH_TOKEN` und `GH_REPO` in den Vercel Environment Variables. Andernfalls bleibt der Endpoint inert (er gibt `ok: true, stored: false`).

Privacy & Hinweise

- Die App verarbeitet Exporte lokal im Browser — standardmäßig wird nichts an externe Server gesendet.
- Wenn du das Feedback‑Feature aktiv nutzt und `GH_TOKEN` konfigurierst, werden Feedback‑Daten an das konfigurierte GitHub‑Repo als Issues weitergeleitet.

Weiteres

- Wenn du möchtest, kann ich eine kurze `start.ps1` hinzufügen, die das lokale Starten automatisiert, oder einen minimalen Deploy‑Guide ergänzen (z. B. env vars für Vercel).

Lizenz: Dieses Paket enthält Teile der internen App; prüfe Lizenz/Datenschutz bevor du öffentlich hostest.
