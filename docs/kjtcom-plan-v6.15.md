# kjtcom - Plan v6.15 (Phase 6a - Discovery)

**Pipeline:** kjtcom (cross-pipeline Flutter app)
**Phase:** 6a (Discovery - Playwright competitor scraping)
**Iteration:** 15 (global counter)
**Machine:** tsP3-cos (ThinkStation P3 Ultra SFF G2) - FIRST RUN
**Date:** March 2026

---

## Section A: P3 Environment Setup (One-Time)

This section runs BEFORE the Gemini CLI agent launches. Human executes all steps manually.

### A1: System Packages

```fish
# Verify base packages
sudo pacman -S --needed git nodejs npm python chromium base-devel

# Verify versions
git --version
node --version
npm --version
python3 --version
chromium --version
```

### A2: SSH Key + GitHub

```fish
# Generate SSH key (if not already present)
ssh-keygen -t ed25519 -C "kthompson@tsP3-cos" -f ~/.ssh/id_ed25519

# Start ssh-agent
eval (ssh-agent -c)
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
# -> Add to GitHub: github.com/settings/keys (or as deploy key on SOC-Foundry/kjtcom)

# Verify
ssh -T git@github.com
```

### A3: Clone Repo

```fish
mkdir -p ~/dev/projects
cd ~/dev/projects
git clone git@github.com:SOC-Foundry/kjtcom.git
cd kjtcom
git status
```

### A4: API Keys in config.fish

```fish
# Edit config.fish to add env vars
# Use your preferred editor - DO NOT paste keys into terminal history
nano ~/.config/fish/config.fish

# Add these lines (replace with actual values):
# set -gx GEMINI_API_KEY "your-key-here"
# set -gx GOOGLE_PLACES_API_KEY "your-key-here"
# set -gx GOOGLE_APPLICATION_CREDENTIALS "$HOME/.config/gcloud/kjtcom-sa.json"
# set -gx ANTHROPIC_API_KEY "your-key-here"

# Reload
source ~/.config/fish/config.fish

# Verify (SET/NOT SET only - NEVER cat config.fish - G20)
test -n "$GEMINI_API_KEY" && echo "GEMINI: SET" || echo "GEMINI: NOT SET"
test -n "$GOOGLE_PLACES_API_KEY" && echo "PLACES: SET" || echo "PLACES: NOT SET"
test -n "$GOOGLE_APPLICATION_CREDENTIALS" && echo "FIREBASE SA: SET" || echo "FIREBASE SA: NOT SET"
test -n "$ANTHROPIC_API_KEY" && echo "ANTHROPIC: SET" || echo "ANTHROPIC: NOT SET"
```

### A5: Firebase Service Account

```fish
# Copy the SA JSON from NZXTcos or download from GCP Console
# Project: kjtcom-c78cd, under socfoundry.com org
mkdir -p ~/.config/gcloud
# scp from NZXTcos:
scp kthompson@nzxtcos:~/.config/gcloud/kjtcom-sa.json ~/.config/gcloud/

# Verify
test -f "$GOOGLE_APPLICATION_CREDENTIALS" && echo "SA file exists" || echo "SA file MISSING"
```

### A6: Install Gemini CLI

```fish
# Install globally
npm install -g @anthropic-ai/gemini-cli
# NOTE: Verify the actual package name. It may be:
#   npm install -g @anthropic-ai/gemini-cli
#   npm install -g @anthropic/gemini-cli
#   npm install -g gemini-cli
# Check https://www.npmjs.com/search?q=gemini%20cli for current package name.

# If the package is not on npm, install from source:
# git clone https://github.com/anthropics/gemini-cli.git
# cd gemini-cli && npm install && npm link

# Verify
gemini --version
```

### A7: Install Claude Code

```fish
npm install -g @anthropic-ai/claude-code
# Same note: verify actual package name on npm

# Verify
claude --version

# Set preferred shell (one-time)
claude config set preferredShell fish
```

### A8: Install Flutter (for Phase 6c+, optional now but recommended)

```fish
# AUR install via yay
yay -S flutter

# If yay not installed:
# sudo pacman -S --needed git base-devel
# git clone https://aur.archlinux.org/yay.git /tmp/yay && cd /tmp/yay && makepkg -si

# If AUR install fails (webkit2gtk dep issue noted on NZXTcos):
# Manual install:
# cd ~/dev
# git clone https://github.com/flutter/flutter.git -b stable
# fish_add_path ~/dev/flutter/bin
# flutter doctor

# Accept Android licenses (not needed for web-only but flutter doctor complains)
flutter doctor --android-licenses 2>/dev/null || true

# Verify
flutter --version
flutter doctor
```

### A9: Install Firebase CLI

```fish
npm install -g firebase-tools

# Login
firebase login

# Verify project access
firebase projects:list | grep kjtcom
```

### A10: Verify Complete Setup

```fish
cd ~/dev/projects/kjtcom

echo "=== P3 SETUP VERIFICATION ==="
echo "Git:" (git --version | head -1)
echo "Node:" (node --version)
echo "npm:" (npm --version)
echo "Python:" (python3 --version)
echo "Chromium:" (chromium --version 2>/dev/null || echo "NOT FOUND")
echo "Gemini CLI:" (gemini --version 2>/dev/null || echo "NOT FOUND")
echo "Claude Code:" (claude --version 2>/dev/null || echo "NOT FOUND")
echo "Flutter:" (flutter --version 2>/dev/null | head -1 || echo "NOT FOUND")
echo "Firebase:" (firebase --version 2>/dev/null || echo "NOT FOUND")
echo ""
echo "API Keys:"
test -n "$GEMINI_API_KEY" && echo "  GEMINI: SET" || echo "  GEMINI: NOT SET"
test -n "$GOOGLE_PLACES_API_KEY" && echo "  PLACES: SET" || echo "  PLACES: NOT SET"
test -n "$GOOGLE_APPLICATION_CREDENTIALS" && echo "  FIREBASE SA: SET" || echo "  FIREBASE SA: NOT SET"
test -n "$ANTHROPIC_API_KEY" && echo "  ANTHROPIC: SET" || echo "  ANTHROPIC: NOT SET"
echo ""
echo "Repo:"
git remote -v
git log --oneline -3
echo ""
echo "SSH:"
ssh -T git@github.com 2>&1 | head -1
```

**All items must show SET/OK/version before proceeding to Section B.**

---

## Section B: Panther Design Reference (Human, Pre-Agent)

Stage the Panther screenshots and HTML mockup into the design-brief folder before launching the agent. These are the PRIMARY design reference - Panther is the site kjtcom's query UX should mimic.

Panther is behind Okta MFA with short session timeouts. Even with successful authentication, Playwright would land on the Okta redirect, not the specific saved PantherFlow search page. The correct page requires manual navigation through Panther's Investigate -> Search UI to a saved query. Scraping is not viable.

```fish
cd ~/dev/projects/kjtcom
mkdir -p app/design-brief/panther

# Copy the 3 Panther screenshots from wherever they were saved
cp ~/Downloads/panther-search-results.png app/design-brief/panther/
cp ~/Downloads/panther-json-detail.png app/design-brief/panther/
cp ~/Downloads/panther-filter-by-value.png app/design-brief/panther/

# Copy the HTML mockup (kjtcom query interface translated from Panther patterns)
cp ~/Downloads/kjtcom-query-mockup.html app/design-brief/panther/

# Verify
echo "Panther design-brief contents:"
ls -la app/design-brief/panther/
```

Expected contents of `app/design-brief/panther/`:

| File | Description |
|------|-------------|
| panther-search-results.png | PantherFlow query editor + results table |
| panther-json-detail.png | Expanded JSON payload with nested fields, filter-by-value tooltip |
| panther-filter-by-value.png | Filter-by-value adding new query line |
| kjtcom-query-mockup.html | HTML mockup translating Panther patterns to kjtcom NoSQL + Thompson Indicator Fields |

---

## Section C: Gemini CLI Execution (Playwright Scraping)

**Launch:** `gemini --yolo`
**First message:** "Read GEMINI.md, then execute Section C of docs/kjtcom-plan-v6.15.md. This is Phase 6a Discovery - scrape 8 public sites via Playwright MCP. The primary design reference (Panther) is pre-staged in app/design-brief/panther/ - review it first, then scrape the 8 public sites. Start with Step 0."

### Step 0: Pre-Flight Verification

```
CHECKLIST:
[ ] docs/kjtcom-design-v6.15.md exists
[ ] docs/kjtcom-plan-v6.15.md exists
[ ] GEMINI.md updated with v6.15 references
[ ] app/design-brief/panther/ contains 3 screenshots + 1 HTML mockup
[ ] API keys (SET/NOT SET only):
    - fish -c "test -n \$GEMINI_API_KEY && echo SET || echo NOT SET"
[ ] Chromium installed: fish -c "which chromium"
[ ] Git status clean: fish -c "cd ~/dev/projects/kjtcom && git status"
[ ] Disk space: fish -c "df -h / | tail -1" (need >10GB free)
```

### Step 0.5: Review Panther Reference

Before scraping public sites, review the Panther design reference:

```
Open and review app/design-brief/panther/kjtcom-query-mockup.html in Playwright.
Open and review each of the 3 Panther screenshots.

Note the following patterns that ALL public site scrapes should be compared against:
- Dark query editor with syntax highlighting
- Results as single-line rows with colored badges
- Click-to-expand JSON detail panel on right
- Filter-by-value interaction from detail panel back to query
- Green CTA button, dark surface background, mono font for data
```

### Step 1: Create Scrape Archive Structure

```fish
cd ~/dev/projects/kjtcom
mkdir -p app/scrape-archive/{monad,scanner-dev,greynoise,palantir,maltego,cribl,black-tomato,abercrombie-kent}
```

### Step 2: Scrape Category 1 - Pipeline / SIEM Platforms

For EACH of the 4 sites, use Playwright MCP to:

1. Navigate to URL at desktop viewport (1440x900)
2. Wait for page load (networkidle or 10s timeout)
3. Capture full-page screenshot -> `desktop.png`
4. Scroll through key sections, capture scrolled screenshots if hero/product sections are below fold
5. Switch to mobile viewport (375x812)
6. Capture full-page screenshot -> `mobile.png`
7. Capture accessibility snapshot -> `accessibility.json`
8. Write `scrape.md` with analysis (see template in design doc)

**Site 1: Monad (https://www.monad.com/)**
```
Navigate to https://www.monad.com/
Capture desktop (1440x900) and mobile (375x812) screenshots.
Capture accessibility snapshot.
Save to app/scrape-archive/monad/
Write scrape.md analyzing: fonts, colors, spacing, card layouts, hero treatment, navigation.
Tag as [PIPELINE]. This is the highest priority peer.
Compare to Panther reference: what dark surface / query patterns does Monad share?
```

**Site 2: Scanner.dev (https://scanner.dev/)**
```
Navigate to https://scanner.dev/
Capture desktop (1440x900) and mobile (375x812) screenshots.
Capture accessibility snapshot.
Save to app/scrape-archive/scanner-dev/
Write scrape.md analyzing: Geist font usage (Sans + Mono), color tokens, query-first UX, product sections.
Tag as [PIPELINE]. Font reference site - Geist is the defining typographic choice for kjtcom.
```

**Site 3: GreyNoise Viz (https://viz.greynoise.io/)**
```
Navigate to https://viz.greynoise.io/
Capture desktop (1440x900) and mobile (375x812) screenshots.
Capture accessibility snapshot.
Save to app/scrape-archive/greynoise/
Write scrape.md analyzing: globe visualization, green-on-dark aesthetic, font treatment, data density patterns.
Tag as [PIPELINE]. Globe and color reference site.
NOTE: May require login or show limited content. Capture what's available.
```

**Site 4: Palantir Foundry (https://www.palantir.com/platforms/foundry/)**
```
Navigate to https://www.palantir.com/platforms/foundry/
Capture desktop (1440x900) and mobile (375x812) screenshots.
Capture accessibility snapshot.
Save to app/scrape-archive/palantir/
Write scrape.md analyzing: enterprise platform aesthetic, map overlays, entity relationship hints, authority positioning.
Tag as [PIPELINE].
NOTE: Marketing page only. Actual product UI is auth-gated.
```

### Step 3: Scrape Category 2 - Investigation Tools

**Site 5: Maltego (https://www.maltego.com/)**
```
Navigate to https://www.maltego.com/
Capture desktop (1440x900) and mobile (375x812) screenshots.
Capture accessibility snapshot.
Save to app/scrape-archive/maltego/
Write scrape.md analyzing: entity graph visualization, connection lines, investigation UX patterns.
Tag as [INVESTIGATION].
```

**Site 6: Cribl (https://cribl.io/)**
```
Navigate to https://cribl.io/
Capture desktop (1440x900) and mobile (375x812) screenshots.
Capture accessibility snapshot.
Save to app/scrape-archive/cribl/
Write scrape.md analyzing: observability pipeline viz, data routing UX, pipeline-as-product presentation.
Tag as [INVESTIGATION].
```

### Step 4: Scrape Category 3 - Boutique Travel

**Site 7: Black Tomato (https://www.blacktomato.com/)**
```
Navigate to https://www.blacktomato.com/
Capture desktop (1440x900) and mobile (375x812) screenshots.
Capture accessibility snapshot.
Save to app/scrape-archive/black-tomato/
Write scrape.md analyzing: cinematic hero imagery, editorial storytelling, card layouts, destination presentation.
Tag as [CONCIERGE].
```

**Site 8: Abercrombie & Kent (https://www.abercrombiekent.com/)**
```
Navigate to https://www.abercrombiekent.com/
Capture desktop (1440x900) and mobile (375x812) screenshots.
Capture accessibility snapshot.
Save to app/scrape-archive/abercrombie-kent/
Write scrape.md analyzing: expedition-grade aesthetic, guide profiles, curated collection presentation.
Tag as [CONCIERGE].
```

### Step 5: Handle Failures

If any site blocks Playwright (bot detection, Cloudflare challenge, login wall):

1. Document the failure in that site's scrape.md
2. Attempt with a different user-agent string
3. If still blocked, capture whatever partial content is available
4. Note "BLOCKED" status in the site's scrape.md
5. Do NOT spend more than 3 minutes on any single blocked site

### Step 6: Produce UX Analysis Synthesis

After all 8 sites are scraped, produce `app/scrape-archive/ux-analysis.md`:

```
Read ALL 8 public site scrape.md files.
Review the Panther reference materials in app/design-brief/panther/ (3 screenshots + mockup).

Synthesize into ux-analysis.md with these sections:

1. Panther (PRIMARY reference - the site kjtcom should mimic):
   - NoSQL query editor layout specification derived from screenshots
   - Results table format and row interaction pattern
   - JSON detail panel with hierarchical field display
   - Filter-by-value interaction (detail panel -> query clause)
   - How the kjtcom-query-mockup.html adapts these patterns
   - Specific adaptations: NoSQL syntax, entity columns, pipeline colors, +filter/-exclude

2. Layer 1 (Pipeline tools - Monad, Scanner, GreyNoise, Palantir):
   - Common dark surface patterns (background colors, border colors)
   - Typography choices (font families, sizes, weights, mono usage)
   - How these SUPPORT or REFINE the Panther-derived query patterns
   - Data confidence/density indicators

3. Layer 2 (Investigation tools - Maltego, Cribl):
   - Entity relationship visualization patterns
   - Data routing / pipeline flow UX
   - Connection line styles and node layouts

4. Layer 3 (Travel concierge - Black Tomato, A&K):
   - Editorial card layouts (image sizing, text hierarchy, spacing)
   - Cinematic imagery treatment (overlay, blur, gradient)
   - Destination authority patterns ("expert knows best" UX)

5. Convergence Points:
   - Where 2+ categories agree and kjtcom should follow

6. Conflicts:
   - Where categories diverge and which direction kjtcom should take

7. Preliminary Token Recommendations:
   - Font stacks (LOCKED: Geist Sans, Geist Mono, Inter fallback)
   - Color palette direction (dark surface #0D1117, green accent #4ADE80, pipeline colors)
   - Spacing scale (observed patterns)
   - Border/radius conventions
   - Card layout dimensions

Save to app/scrape-archive/ux-analysis.md
```

### Step 7: Post-Flight

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only doc references
[ ] 8 site directories in app/scrape-archive/
[ ] Each site has: desktop.png, mobile.png, accessibility.json, scrape.md
[ ] Panther directory in app/design-brief/panther/ has: 3 screenshots + 1 mockup
[ ] ux-analysis.md produced with Panther as primary reference in section 1
[ ] No API keys in any file
```

### Step 8: Produce Artifacts

**All 4 mandatory artifacts:**

1. **docs/kjtcom-build-v6.15.md** - Session transcript: environment setup notes, per-site scrape status (success/partial/blocked), timing, any Playwright issues encountered, Panther reference review notes
2. **docs/kjtcom-report-v6.15.md** - Scrape results summary, key findings per category, Panther as primary pattern, top 5 design patterns identified, blocked sites (if any), recommendation for Phase 6b (Design Contract)
3. **docs/kjtcom-changelog.md** - Append v6.15 at top
4. **README.md** - Update Phase 6a status to DONE, add iteration v6.15. Use this phase structure:

```
| Phase | Name                                | Status              | Iteration    |
|-------|-------------------------------------|---------------------|--------------|
| 0     | Scaffold & Environment              | DONE                | v0.5         |
| 1     | Discovery (30 videos)               | DONE                | v1.6, v1.7   |
| 2     | Calibration (60 videos)             | DONE                | v2.8, v2.9   |
| 3     | Stress Test (90 videos)             | DONE                | v3.10, v3.11 |
| 4     | Validation + Schema v3 (120 videos) | DONE                | v4.12, v4.13 |
| 5     | Production Run (full datasets)      | CalGold IN PROGRESS | v5.14        |
| 6a    | Flutter App - Discovery             | DONE                | v6.15        |
| 6b    | Flutter App - Design Contract       | Pending             | -            |
| 6c    | Flutter App - Implementation        | Pending             | -            |
| 6d    | Flutter App - QA                    | Pending             | -            |
| 6e    | Flutter App - Deploy                | Pending             | -            |
| 7     | Firestore Load                      | Pending             | -            |
| 8     | Enrichment Hardening                | Pending             | -            |
| 9     | App Optimization                    | Pending             | -            |
| 10    | Retrospective + Template            | Pending             | -            |
```

Do NOT git commit or push.

---

## GEMINI.md for v6.15

```markdown
# kjtcom - Agent Instructions (Gemini CLI)

## Read Order

1. docs/kjtcom-design-v6.15.md
2. docs/kjtcom-plan-v6.15.md (execute Section C)

## Context

Phase 6a Discovery. Scrape 8 public competitor sites via Playwright MCP.

PRIMARY DESIGN REFERENCE: Panther SIEM (tachtech.runpanther.net).
Pre-staged in app/design-brief/panther/ with 3 screenshots + 1 HTML mockup.
Do NOT attempt to scrape Panther (Okta MFA, wrong landing page). Review the
pre-staged materials and use them as the #1 comparison point for all scrapes.

This is the first kjtcom run on tsP3-cos (P3 Ultra).

## Shell - MANDATORY

- All commands in fish shell via fish -c wrappers
- NEVER cat config.fish (G20)

## Security

- grep -rnI "AIzaSy" . before completion
- Print only SET/NOT SET for key checks

## MCP Tools

- Playwright: screenshots + accessibility snapshots
- Do NOT use Firecrawl (cert issues - G28)
- Do NOT scrape Panther (G29)

## Scraping Parameters

- Desktop: 1440x900 viewport
- Mobile: 375x812 viewport
- Timeout: 10s per page (networkidle)
- Max 3 min per blocked site before moving on

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v6.15.md
2. docs/kjtcom-report-v6.15.md
3. docs/kjtcom-changelog.md (append v6.15)
4. README.md (Phase 6a DONE)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Section A (P3 setup) | ~30 min (human, one-time) |
| Section B (Panther reference staging) | ~5 min (human) |
| Step 0 (pre-flight) | ~2 min |
| Step 0.5 (review Panther reference) | ~5 min |
| Steps 1-4 (scrape 8 sites) | ~20-30 min |
| Step 5 (handle failures) | ~5-10 min |
| Step 6 (UX synthesis with Panther primary) | ~10-15 min |
| Steps 7-8 (post-flight + artifacts) | ~10 min |
| **Total** | **~1-1.5 hours** |

---

## After v6.15

1. Review ux-analysis.md and scrape archive
2. Commit: `git add app/ docs/ && git commit -m "KT 6.15 Phase 6a Discovery complete" && git push`
3. Proceed to Phase 6b Design Contract (Claude chat session, not agent execution)
4. Continue monitoring v5.14 on NZXTcos in parallel
