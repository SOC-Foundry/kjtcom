# ADR 0001 — Phase A Externalization

**Status:** Accepted
**Date:** 2026-04-08
**Authors:** kjtcom v10.67 planning chat

## Context

The IAO (Iterative Agentic Orchestration) methodology, developed in kjtcom, produces reusable harness components: path resolution, context bundle generation, registry queries, compatibility checking, pre/post-flight health checks, and a iao CLI. These components are project-agnostic and will be consumed by other IAO-pattern projects within SOC-Foundry and TachTech Engineering.

Continuing to develop these components as first-class members of the kjtcom repo creates several problems:

1. Engineers consuming the components would have to vendor or submodule kjtcom in full
2. Versioning is conflated between kjtcom iterations and middleware capability
3. Extraction to a dedicated repo becomes harder the longer it is deferred

## Decision

Externalize the harness components into an iao_middleware Python package that is:

1. **Currently staged at kjtcom/iao-middleware/** as a subdirectory for Phase A authoring (v10.66 scaffold, v10.67 hardening)
2. **Authored in standalone-repo voice** — its own README, CHANGELOG, VERSION, pyproject.toml, .gitignore, and docs/adrs tree
3. **Extracted to SOC-Foundry/iao-middleware as its own repo in v10.68** via git subtree split --prefix=iao-middleware/
4. **Versioned independently** of kjtcom iteration numbers (semver starting 0.1.0)

## Consequences

**Positive:**
- Clean extraction path: v10.68 Phase B is a mechanical operation, not a refactor
- Python engineers can from iao_middleware import ... today (via pip install -e)
- Independent versioning allows middleware to iterate without kjtcom iteration overhead
- Standalone-repo voice forces documentation discipline from day one

**Negative:**
- Dash/underscore naming asymmetry (iao-middleware repo, iao_middleware package) — documented in kjtcom harness ADR-028
- Two parallel ADR streams (kjtcom harness ADRs vs iao_middleware internal ADRs) — intentional scope separation
- License decision deferred until v0.2.0 (before v10.68 extraction)

## Status

Accepted and under implementation in kjtcom v10.67. Extraction planned for kjtcom v10.68.
