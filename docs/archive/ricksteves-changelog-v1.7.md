# RickSteves - Changelog

**v1.7 (RickSteves Phase 1 - Discovery)**
- 30-video discovery batch: 30/30 acquired, 30/30 transcribed, 30/30 extracted
- 200 unique destinations across 23 countries
- Thompson Schema v2 validated: t_any_countries (100%), t_any_regions (46%) populated
- Geocoding: 98% (68% Nominatim + 66 backfilled from Google Places)
- Enrichment: 98% via Google Places (197/200, 3 misses are artworks not places)
- Cross-pipeline queries validated: keyword "church" returns results from both CalGold and RickSteves; country "us" returns CalGold, country "italy"/"france" returns RickSteves
- CalGold entities backfilled to schema v2 (56/56, t_any_countries: ["us"])
- Migrated phase3_extract.py from google.generativeai to google.genai (v1.69.0)
- Updated phase5_geocode.py and phase6_enrich.py for international locations (country in query)
- Updated phase6_enrich.py with Google Places coordinate backfill (places.location field)
- Updated phase7_load.py: pipeline registry reads from pipeline.json (no longer hardcoded)
- Added 4 new composite indexes for t_any_countries and t_any_regions queries
- 1 intervention: LD_LIBRARY_PATH for CUDA
- Security: zero API keys in repo (verified)
