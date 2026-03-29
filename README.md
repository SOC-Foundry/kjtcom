# kjtcom - kylejeromethompson.com

Multi-pipeline location intelligence platform. Each pipeline processes YouTube playlists through a 7-stage IAO pipeline (acquire -> transcribe -> extract -> normalize -> geocode -> enrich -> load) into Cloud Firestore, served via Flutter Web.

## Pipelines

| Pipeline | Source | Entity Type | Videos |
|----------|--------|-------------|--------|
| calgold | California's Gold (Huell Howser) | landmark | 431 |

## Thompson Schema

Universal indicator fields (`t_any_*`) enable cross-dataset queries without knowing source schemas. Mirrors Panther SIEM's `p_any_*` pattern.

## Stack

- **Frontend:** Flutter Web
- **Database:** Cloud Firestore (Firebase Blaze)
- **Search:** Cloud Functions + native Firestore queries
- **Extraction:** Gemini 2.5 Flash API
- **Transcription:** faster-whisper (CUDA)
- **Geocoding:** Nominatim (OSM)
- **Enrichment:** Google Places API (New)

## Docs

- `docs/calgold-design-v0.5.md` - Architecture + Thompson Schema
- `docs/calgold-plan-v0.5.md` - Execution plan
