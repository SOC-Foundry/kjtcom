# ADR 0001 - Phase A Externalization

**Status:** Accepted (superseded by Phase B extraction in 10.68.X)
**Date:** 2026-04-08

## Context

The IAO (Iterative Agentic Orchestration) methodology produces reusable harness components: path resolution, bundle generation, registry queries, compatibility checking, pre/post-flight health checks, and a iao CLI. These components are project-agnostic and consumed by IAO-pattern projects.

## Decision

Externalize the harness components into an `iao` Python package that is:

1. Authored as its own subdirectory inside the originating project for Phase A
2. Authored in standalone-repo voice - its own README, CHANGELOG, VERSION, pyproject.toml, .gitignore, docs/adrs tree
3. Extracted to a standalone repository in Phase B
4. Versioned independently of the originating project's iteration numbers (semver starting 0.1.0)

## Consequences

**Positive:**
- Clean extraction path: Phase B extraction is mechanical, not a refactor
- `from iao import ...` works via pip install -e
- Independent versioning frees middleware iteration cadence

**Negative:**
- Two parallel ADR streams (project harness ADRs vs iao internal ADRs) - intentional scope separation
- License decision deferred until v0.2.0

## Status

Accepted. Phase B extraction underway.
