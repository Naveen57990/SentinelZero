"""
Automated Screen Recording of SentinelZero Web Dashboard using Playwright
Records live user interaction with the production dashboard.
"""
import os
import time
from playwright.sync_api import sync_playwright

REC_DIR = os.path.abspath("demo/recordings")
os.makedirs(REC_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=REC_DIR,
        record_video_size={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    
    print("Navigating to live production dashboard...")
    page.goto("https://web-theta-tawny-78.vercel.app", wait_until="networkidle")
    time.sleep(1.5)

    # 1. Show initial vulnerable state
    print("Auditing vulnerable state...")
    page.click("button:has-text('Run Zero-Trust Audit')")
    time.sleep(3.0)

    # 2. Switch to MCP Agent
    print("Loading MCP Agent schema...")
    page.click("button:has-text('Load MCP Agent')")
    time.sleep(2.0)
    page.click("button:has-text('Run Zero-Trust Audit')")
    time.sleep(3.0)

    # 3. Switch to Zero-Trust Secure state
    print("Loading Zero-Trust Secure state...")
    page.click("button:has-text('Load Zero-Trust')")
    time.sleep(2.0)
    page.click("button:has-text('Run Zero-Trust Audit')")
    time.sleep(3.5)

    context.close()
    browser.close()
    print("Live screen recording complete.")
