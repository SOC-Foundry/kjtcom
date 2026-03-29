# CalGold - Changelog

**v1.6 (Phase 1 - Discovery)**
- 30-video discovery batch: 30/30 acquired, 30/30 transcribed, 30/30 extracted
- 57 unique entities after normalization (0 dedup merges in this batch)
- Geocoding: 43% hit rate via Nominatim (below 60% target - niche locations)
- Enrichment: 100% match rate via Google Places API (New) after API key fix
- Thompson Schema validated at scale: all t_any_* fields populated, all lowercase
- 56 documents loaded to staging Firestore, all array-contains queries working
- 3 interventions: CUDA LD_LIBRARY_PATH, google-generativeai install, Places API key
- v0.5 artifacts archived to docs/archive/
