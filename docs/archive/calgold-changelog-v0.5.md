# CalGold - Changelog

**v0.5 (Phase 0 - Scaffold)**
- Repo: git@github.com:SOC-Foundry/kjtcom.git
- Firebase: kjtcom (kjtcom-c78cd) under socfoundry.com, Blaze billing
- Monorepo scaffolded: app/, pipeline/, functions/, docs/
- Multi-database configured: (default) + staging, both us-central1
- Firestore security rules deployed (public read, admin-only write)
- 4 composite indexes deployed for cross-dataset queries
- Thompson Schema (t_any_*) designed and validated with test entity
- CalGold pipeline config: schema.json (14 indicator mappings), extraction_prompt.md
- Cloud Functions search endpoint deployed (https://search-rse3bxwgqa-uc.a.run.app)
- 7 pipeline stage scripts created with --pipeline and --database arguments
- 431 CalGold playlist URLs validated via yt-dlp
- Test entity (Watts Towers) loaded to staging Firestore, all t_any fields verified
- 5 interventions resolved (Firebase auth, API enablement, IAM permissions)
