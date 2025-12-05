#!/usr/bin/env python3
"""Capture screenshots of all generated HTML files using Playwright."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Application dimensions (width x height) - matching input screenshots
APP_DIMENSIONS = {
    "google_sheets": (2404, 1126),
    "jira": (2048, 1062),
    "microsoft_word": (2400, 1206),
    "spotify": (2404, 1840),
    "vs_code": (2404, 1202),
}

BASE_URL = "http://localhost:4141"
OUTPUTS_DIR = Path("outputs")


async def capture_screenshot(page, app_name: str, model_name: str):
    """Capture a screenshot for a specific app/model combination."""
    html_file = OUTPUTS_DIR / app_name / f"{model_name}.html"
    png_file = OUTPUTS_DIR / app_name / f"{model_name}.png"

    if not html_file.exists():
        print(f"  Skipping {app_name}/{model_name} - HTML file not found")
        return False

    if png_file.exists():
        print(f"  Skipping {app_name}/{model_name} - PNG already exists")
        return True

    url = f"{BASE_URL}/outputs/{app_name}/{model_name}.html"
    width, height = APP_DIMENSIONS.get(app_name, (1920, 1080))

    try:
        await page.set_viewport_size({"width": width, "height": height})
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.screenshot(path=str(png_file))
        print(f"  Captured {app_name}/{model_name}")
        return True
    except Exception as e:
        print(f"  Error capturing {app_name}/{model_name}: {e}")
        return False


async def main():
    # Get all HTML files (excluding old directory)
    combinations = []
    for app_name in APP_DIMENSIONS.keys():
        app_dir = OUTPUTS_DIR / app_name
        if app_dir.exists():
            for html_file in app_dir.glob("*.html"):
                model_name = html_file.stem
                combinations.append((app_name, model_name))

    print(f"Found {len(combinations)} HTML files to screenshot")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        success_count = 0
        for app_name, model_name in sorted(combinations):
            if await capture_screenshot(page, app_name, model_name):
                success_count += 1

        await browser.close()

    print(f"\nCompleted: {success_count}/{len(combinations)} screenshots captured")


if __name__ == "__main__":
    asyncio.run(main())
