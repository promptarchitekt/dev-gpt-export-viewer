# Changelog

Alle relevanten Änderungen an diesem Projekt.

## 0.2.1 – 2025-01-15 (P0 Bugfix Release)

### 🐛 Critical Bugfixes
- **Index-Part-Bug**: Fixed `split_conversations_by_size.py` flushing timing – index.csv now correctly points to the right part file when conversations are split at boundaries
- **Feedback API Validation**: Backend now accepts string ratings (e.g., `"5"`) in addition to numbers, fixing submission failures from frontend
- **Rating Scale Correction**: Changed GitHub Issue body from `/10` to `/5` scale to match frontend UI
- **Helpful Field**: Added `helpful` field to feedback submission body (was missing in v0.2.0)
- **hitNav Reference**: Fixed undefined `hitNav` variable in frontend by adding proper local declaration

### ✨ Improvements
- **Defensive Validation**: Added `toNum()` and `isRating()` helpers for robust type conversion and validation
- **Comment Sanitization**: Feedback comments now truncated to 5000 chars and control characters removed
- **Edge-Case Handling**: Python script now handles single conversations exceeding `max_bytes` with warning instead of infinite loop
- **Fallback File Picker**: Added `input[type="file"]` fallback for browsers without File System Access API support
- **NaN-Safety**: `toLocalIso()` now checks `isFinite()` before formatting timestamps

### 🧪 Testing
- Added `test_split_conversations_by_size.py` with 5 test cases:
  - Boundary case (index.csv correctness)
  - Single conversation > max_bytes
  - Empty input handling
  - Corrupt JSON error handling
  - Unicode line separator edge case

### 📚 Documentation
- Added migration guide: `docs/releases/v0.2.1-migration.md`
- Updated README with testing instructions

## 0.1.0 – Initial Release

- Lokale HTML‑App zum Aufbereiten und Anzeigen eines ChatGPT‑Exports (`conversations.json`).
- Streaming‑Parser, Teil‑Dateien (10/20/50 MB), `index.csv` und `messages.csv`.
- Chat‑Ansicht mit Suche, Markierung, Treffer‑Navigation (◀ ▶ / Enter).
- Einzelexporte: HTML/Markdown/TXT via „Speichern unter“. Dateiname `yymmdd_hhmm_Chatname`.
- Datenschutz: rein lokal, kein Upload. CSVs UTF‑8 mit BOM (Excel‑freundlich).

