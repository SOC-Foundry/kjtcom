# kjtcom - Build v6.19 (Phase 6e - Deploy)

**Pipeline:** kjtcom (cross-pipeline Flutter app)
**Phase:** 6e (Deploy)
**Iteration:** 19 (global counter)
**Executor:** Claude Code (Opus)
**Machine:** tsP3-cos (ThinkStation P3 Ultra SFF G2)
**Date:** March 2026

## Implementation Log

### Step 1: Pre-Flight Verification

- Flutter 3.41.6 (stable, Dart 3.11.4) - confirmed
- Firebase CLI 15.12.0 - confirmed
- Firebase project: kjtcom-c78cd
- Root firebase.json hosting config: `app/build/web` as public directory
- Domain: kylejeromethompson.com (A record + TXT record pre-verified in Firebase Console)

### Step 2: Flutter Web Release Build

- Command: `flutter build web --release` (from app/ directory)
- Build time: 16.9s
- Output: `app/build/web/` (39 files)
- CanvasKit WASM rendering engine (default)
- Font tree-shaking: MaterialIcons reduced from 1.6MB to 7.7KB (99.5%)
- Warnings: cupertino_icons font not bundled (unused, cosmetic warning only)

### Step 3: Firebase Hosting Deploy (First Pass)

- Command: `firebase deploy --only hosting --project kjtcom-c78cd`
- 39 files uploaded
- Hosting URL: https://kjtcom-c78cd.web.app
- Custom domain: https://kylejeromethompson.com

### Step 4: Deployment Verification

- Navigated to https://kylejeromethompson.com via Playwright MCP (Chromium)
- Page title: "kjtcom - Location Intelligence" - PASS
- SIEM UI rendered correctly: dark background (#0D1117), query editor with line numbers, NoSQL/Logs tabs, green Search button, Results/Map/Globe tabs, results table with NAME/CITY/SHOW columns
- Screenshot captured: `docs/deploy-desktop-verification.png`

### Step 5: Google Analytics (GA4) Integration

- Measurement ID: G-JMVEJLW9PC (already provisioned in firebase_options.dart)
- Added gtag.js snippet to `app/web/index.html`:
  - `<script async src="https://www.googletagmanager.com/gtag/js?id=G-JMVEJLW9PC">`
  - `gtag('config', 'G-JMVEJLW9PC')`
- Verified: 2 occurrences of G-JMVEJLW9PC in built `index.html`

### Step 6: Rebuild + Redeploy (With GA4)

- Rebuild: 17.3s
- Redeploy: 2 new files uploaded (index.html updated)
- Hosting URL: https://kjtcom-c78cd.web.app - live

### Step 7: Cross-Browser Smoke Test

**Chrome (Chromium via Playwright MCP):**
- Page loaded: PASS
- Title: "kjtcom - Location Intelligence" - PASS
- Console errors: 0 - PASS
- SIEM UI fully rendered on canvas - PASS
- Screenshot: `docs/smoke-chrome-1440x900.png`

**Firefox (Playwright headless Firefox):**
- Page loaded: PASS
- Title: "kjtcom - Location Intelligence" - PASS
- Console errors: 0 - PASS
- Canvas screenshot: blank (known CanvasKit WebGL + headless Firefox limitation - same behavior observed in Phase 6d QA)
- Screenshot: `docs/smoke-firefox-1440x900.png`

### Step 8: Security Scan

- `grep -rnI "AIzaSy" .` - all matches are:
  - `app/lib/firebase_options.dart` - public Firebase Web API key (expected, restricted by Firestore Rules)
  - `app/build/web/main.dart.js` - compiled build output (expected)
  - `app/.dart_tool/` - build cache (expected)
  - `docs/` - grep command references in prior artifacts
- GOOGLE_PLACES_API_KEY: NOT SET
- GEMINI_API_KEY: NOT SET
- ANTHROPIC_API_KEY: NOT SET

## Technical Notes

- Firebase Hosting serves from `app/build/web` (configured in root `firebase.json`)
- CanvasKit is the default Flutter Web renderer - renders to `<canvas>` via WebGL
- GA4 is loaded via gtag.js in the HTML head, independent of the Flutter app lifecycle
- The Firebase Web API key is intentionally public - Firestore Security Rules enforce access control

## Verification

- [x] flutter build web --release: SUCCESS (16.9s)
- [x] firebase deploy --only hosting: SUCCESS (39 files)
- [x] Site live at https://kylejeromethompson.com
- [x] GA4 (G-JMVEJLW9PC) integrated via gtag.js
- [x] Chrome smoke test: PASS (full render, 0 errors)
- [x] Firefox smoke test: PASS (page loads, 0 errors; canvas blank in headless - known)
- [x] Security: grep -rnI "AIzaSy" . -> Firebase Web key only (expected)
- [x] 4 mandatory artifacts produced
