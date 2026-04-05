#!/usr/bin/env python3
"""Panther SIEM UI scrape via Playwright CDP.
Captures UI structure ONLY - no customer alert/detection data.
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

OUTPUT_DIR = 'docs/panther-reference'

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with async_playwright() as p:
        print("[1] Connecting to Chrome via CDP on port 9222...")
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        contexts = browser.contexts
        print(f"    Found {len(contexts)} browser contexts")

        # Find Panther tab
        panther_page = None
        for ctx in contexts:
            for page in ctx.pages:
                print(f"    Tab: {page.url}")
                if 'panther' in page.url.lower() or 'runpanther' in page.url.lower():
                    panther_page = page
                    print(f"    -> Selected Panther tab: {page.url}")

        if not panther_page:
            print("[ERROR] No Panther tab found. Available tabs listed above.")
            return

        # Wait for page to be fully loaded
        await panther_page.wait_for_load_state('networkidle')

        # 4a. Full page screenshot
        print("[2] Taking full page screenshot...")
        await panther_page.screenshot(
            path=f'{OUTPUT_DIR}/panther-search-full.png',
            full_page=True
        )
        print("    Saved panther-search-full.png")

        # 4b. Query editor DOM - try multiple selectors (Qwen recommended)
        print("[3] Capturing query editor DOM...")
        editor_selectors = [
            '[data-testid*="query"]',
            '[data-testid*="search"]',
            '[data-testid*="editor"]',
            '[aria-label*="Search"]',
            '[aria-label*="Query"]',
            '[aria-label*="query"]',
            '[class*="search-input"]',
            '[class*="query-editor"]',
            '[class*="CodeMirror"]',
            '[class*="monaco"]',
            'textarea',
            '[contenteditable="true"]',
            '[role="textbox"]',
        ]
        editor_html = None
        for sel in editor_selectors:
            el = await panther_page.query_selector(sel)
            if el:
                editor_html = await el.evaluate('el => el.outerHTML')
                print(f"    Found editor with selector: {sel}")
                break
        if editor_html:
            with open(f'{OUTPUT_DIR}/panther-query-editor.html', 'w') as f:
                f.write(editor_html)
            print("    Saved panther-query-editor.html")
        else:
            print("    No editor found with known selectors")

        # 4c. Field sidebar - try selectors
        print("[4] Capturing field sidebar...")
        sidebar_selectors = [
            '[class*="sidebar"]',
            '[class*="field"]',
            '[data-testid*="field"]',
            '[role="list"]',
            '[class*="panel"]',
            'aside',
            'nav',
        ]
        sidebar_html = None
        for sel in sidebar_selectors:
            els = await panther_page.query_selector_all(sel)
            for el in els:
                text = await el.text_content()
                if text and ('field' in text.lower() or 'selected' in text.lower() or 'available' in text.lower()):
                    sidebar_html = await el.evaluate('el => el.outerHTML')
                    print(f"    Found sidebar with selector: {sel}")
                    break
            if sidebar_html:
                break
        if sidebar_html:
            with open(f'{OUTPUT_DIR}/panther-field-sidebar.html', 'w') as f:
                f.write(sidebar_html[:50000])  # Cap size
            print("    Saved panther-field-sidebar.html")
        else:
            print("    No field sidebar found with known selectors")

        # 4d. CSS custom properties
        print("[5] Capturing CSS custom properties...")
        css_tokens = await panther_page.evaluate('''() => {
            const styles = getComputedStyle(document.documentElement);
            const result = {};
            for (let i = 0; i < styles.length; i++) {
                const prop = styles[i];
                if (prop.startsWith('--')) {
                    result[prop] = styles.getPropertyValue(prop).trim();
                }
            }
            return result;
        }''')
        with open(f'{OUTPUT_DIR}/panther-css-tokens.json', 'w') as f:
            json.dump(css_tokens, f, indent=2)
        print(f"    Saved {len(css_tokens)} CSS custom properties")

        # 4e. Full DOM snapshot of main content area
        print("[6] Capturing main content DOM structure...")
        # Get a structural snapshot - tag names, classes, roles, data-testids
        dom_structure = await panther_page.evaluate('''() => {
            function walkDOM(node, depth) {
                if (depth > 6) return null;
                const result = {
                    tag: node.tagName,
                    id: node.id || undefined,
                    class: node.className || undefined,
                    role: node.getAttribute && node.getAttribute('role') || undefined,
                    testid: node.getAttribute && node.getAttribute('data-testid') || undefined,
                    ariaLabel: node.getAttribute && node.getAttribute('aria-label') || undefined,
                };
                // Remove undefined keys
                Object.keys(result).forEach(k => result[k] === undefined && delete result[k]);
                if (node.children && node.children.length > 0 && node.children.length < 50) {
                    result.children = Array.from(node.children).map(c => walkDOM(c, depth + 1)).filter(Boolean);
                }
                return result;
            }
            return walkDOM(document.body, 0);
        }''')
        with open(f'{OUTPUT_DIR}/panther-dom-structure.json', 'w') as f:
            json.dump(dom_structure, f, indent=2)
        print("    Saved panther-dom-structure.json")

        # Viewport screenshot (current view, not full page)
        print("[7] Taking viewport screenshot...")
        await panther_page.screenshot(
            path=f'{OUTPUT_DIR}/panther-search-viewport.png'
        )
        print("    Saved panther-search-viewport.png")

        print("\n[DONE] All captures saved to docs/panther-reference/")
        print("[SECURITY] Review screenshots for customer data before committing.")

asyncio.run(main())
