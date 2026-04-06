# kjtcom - Execution Plan v9.48

**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 2.5 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md saved (v9.48, verify >= 200 lines: wc -l CLAUDE.md)
- [ ] GEMINI.md saved (v9.48, verify >= 200 lines: wc -l GEMINI.md)
- [ ] docs/kjtcom-design-v9.48.md saved
- [ ] docs/kjtcom-plan-v9.48.md saved
- [ ] Clean drafts: rm -f docs/drafts/*.md
- [ ] Clean orphaned changelogs: rm -f docs/changelog-v*.md
- [ ] Ollama running, 4 models
- [ ] sudo systemctl restart kjtcom-telegram-bot
- [ ] set -gx IAO_ITERATION v9.48

---

## STEP 1: File Management Cleanup (W1) - 20 min

1. Create scripts/cleanup_docs.py (see design doc)
2. Run it:

```fish
python3 scripts/cleanup_docs.py
```

3. Delete orphaned changelog-v*.md files in docs/:

```fish
rm -f docs/changelog-v*.md
```

4. Update scripts/generate_artifacts.py:
   - Changelog generation: read existing kjtcom-changelog.md, prepend new entry, write back
   - Do NOT create changelog-v{X}.md
   - Do NOT create docs/drafts/changelog-v{X}.md

5. Verify:

```fish
ls docs/changelog-v*.md 2>/dev/null  # Should show nothing
ls docs/drafts/  # Should be empty
```

---

## STEP 2: Qwen Structural Enforcement (W2) - 30 min

1. Add parse_workstream_count() to scripts/run_evaluator.py
2. Add validate_qwen_output() with re-prompt logic (max 2 retries)
3. Add evidence file existence check
4. Test with current iteration:

```fish
python3 -u scripts/run_evaluator.py --iteration v9.48 --workstreams
```

5. Verify output has exactly 4 workstream rows (W1-W4)
6. If Qwen returns != 4, the re-prompt logic should fire and correct it

---

## STEP 3: Verify Harness Line Counts (W3) - 5 min

```fish
wc -l CLAUDE.md GEMINI.md
# Both must be >= 200
```

If either is under 200, the pre-staged files from this session should already exceed 200. Verify and confirm.

---

## STEP 4: Post-Flight + Phase 9 Close (W4) - 20 min

1. Run post_flight.py
2. Verify claw3d.html: curl -s -o /dev/null -w "%{http_code}" https://kylejeromethompson.com/claw3d.html
3. Run cleanup_docs.py
4. Build + deploy:

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze
flutter test
flutter build web
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

5. Phase 9 close checklist (from design doc W4)

---

## STEP 5: Artifacts - 15 min

```fish
python3 -u scripts/run_evaluator.py --iteration v9.48 --workstreams
python3 -u scripts/generate_artifacts.py
python3 -u scripts/generate_artifacts.py --validate-only
python3 -u scripts/generate_artifacts.py --promote
```

Verify: exactly 4 workstream rows, no hallucinated extras, changelog appended to main file (not separate).

Artifacts:
- [ ] docs/kjtcom-design-v9.48.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.48.md (pre-staged)
- [ ] docs/kjtcom-build-v9.48.md (promoted from drafts)
- [ ] docs/kjtcom-report-v9.48.md (4 rows, promoted)
- [ ] docs/kjtcom-changelog.md (APPENDED, not new file)
- [ ] scripts/cleanup_docs.py (NEW)
- [ ] scripts/run_evaluator.py (MODIFIED - structural enforcement)
- [ ] scripts/generate_artifacts.py (MODIFIED - single changelog)
- [ ] CLAUDE.md (v9.48, >= 200 lines)
- [ ] GEMINI.md (v9.48, >= 200 lines)

---

## INTERVENTIONS

Target: 0.

---

*Plan v9.48, April 5, 2026.*
