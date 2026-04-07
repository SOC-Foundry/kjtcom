from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = context.new_page()
    try:
        page.goto('https://kylejeromethompson.com', wait_until='domcontentloaded', timeout=60000)
        time.sleep(10)
        page.screenshot(path='data/postflight-baselines/root.png')
        print('DONE: data/postflight-baselines/root.png')
    except Exception as e:
        print(f'FAILED: {e}')
    finally:
        browser.close()
