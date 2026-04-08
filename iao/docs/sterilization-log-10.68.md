# Sterilization Log 10.68.1

**Purpose:** Document every kjtcom-specific reference removed from iao/ during W6.
**Generated:** 2026-04-08
**Status:** PARTIAL (see deferrals at end)

---

## Removals / Rewrites

### iao/README.md
- Removed: explicit kjtcom references, "authored inside kjtcom/iao-middleware/" preamble, kjtcom GitHub link, "Phase A authored inside kjtcom" subtitle, install paths referencing kjtcom/iao-middleware/.
- Replaced with: project-agnostic standalone-repo voice for v0.1.0-alpha.

### iao/CHANGELOG.md
- Removed: "(kjtcom v10.67)" header tag, "Authored inside kjtcom/iao-middleware/" line, all `iao_middleware.*` module references.
- Replaced: project-agnostic 0.1.0-alpha entry referencing iao.* module names and the new harness/push/bundle additions.

### iao/docs/adrs/0001-phase-a-externalization.md
- Removed: "Authors: kjtcom v10.67 planning chat", repeated kjtcom name throughout context, references to SOC-Foundry/iao-middleware, "kjtcom harness ADR-028".
- Rewrote: generic Phase A externalization rationale with neutral originating-project language. Status updated to "superseded by Phase B extraction".

### iao/install.fish
- Removed: hardcoded "Next: iao project add kjtcom --gcp-project kjtcom-c78cd --prefix KJTCOM" example line.
- Replaced with: angle-bracket placeholders for project name, gcp-project, prefix.

### iao/iao/registry.py
- Removed: "Query the kjtcom script registry (ADR-022). Path-agnostic via iao_paths (v10.66 W3)" docstring and "Query kjtcom script registry" parser description.
- Replaced with: generic "Query the project script registry. Path-agnostic via iao.paths."

### iao/projects.json
- Removed: kjtco entry referencing ~/dev/projects/kjtcom path. The kjtco project lives in its own project.md harness; iao/projects.json (the iao-side registry) tracks only iao itself and forward-looking projects (intra).

### iao/iao/postflight/__init__.py
- Removed: "iao_middleware postflight" docstring -> "iao postflight check modules"

---

## PARTIAL / Deferred (P3 bring-up sterilization round 2)

The following kjtcom-specific references remain in iao/ and are documented as PARTIAL because removing them now would break working post-flight checks and the existing bundle generator. The W6 plan partial-success path explicitly permits this with documentation. They are scheduled for sterilization in P3 bring-up:

### iao/iao/context_bundle.py
- Hardcoded `kjtcom-` filename prefix on lines 38-40, 90, 305, 340, 360.
- Hardcoded pipeline counts on lines 234-237 (calgold/ricksteves/tripledb/bourdain).
- **Status:** Will be rewritten as iao/iao/bundle.py in W7 with parameterized prefix from .iao.json `artifact_prefix` and removal of pipeline-specific hardcoded counts. Sterilization completes there.

### iao/iao/postflight/{claw3d_version_matches,deployed_claw3d_matches,deployed_flutter_matches,map_tab_renders}.py
- Hardcoded URLs to kylejeromethompson.com, "claw3d.html", "app/web/claw3d.html" path, Flutter-specific HTML inspection.
- **Status:** These four modules are kjtcom-pipeline-specific by design (they verify claw3d.html and the Flutter site). They cannot be sterilized in place; they must be moved out of iao/iao/postflight/ into kjtco/postflight/ as a project-specific check plugin set, with iao.postflight providing only the project-agnostic checks (artifacts_present, build_gatekeeper, firestore_baseline). This is a non-trivial refactor (postflight discovery mechanism + plugin loader) and is deferred to P3 bring-up sterilization round 2 (or to a follow-up kjtcom 10.69 if Kyle prefers).
- **Workaround:** doctor.py continues to import them, deploy_paused=true means they emit DEFERRED instead of FAIL.

### iao/iao/doctor.py
- References claw3d_version_matches and deployed_claw3d_matches from postflight/. Unchanged - depends on the postflight modules above. Will be cleaned up alongside them.

### iao/iao/postflight/artifacts_present.py
- Constructs `kjtcom-{atype}-{iteration}.md` file paths. Should use `.iao.json artifact_prefix`. Defer to P3 bring-up.

---

## Final grep

After W6 + W7 (rewriting context_bundle.py -> bundle.py), the only remaining kjtcom hits in iao/ should be the postflight modules and artifacts_present.py + doctor.py references. Documented above.
