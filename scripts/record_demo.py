import os
import shutil
import time
from playwright.sync_api import sync_playwright

def record_demo():
    os.makedirs("docs", exist_ok=True)
    os.makedirs("tmp_video", exist_ok=True)

    url = "https://investment-copilot-708768009414.us-east1.run.app/dev-ui/?app=app"

    turn1 = (
        "Create a fictional investor profile for Alex: "
        "32 years old, ₹150,000 monthly income, ₹70,000 monthly expenses, "
        "₹800,000 savings, ₹40,000 monthly investment, "
        "7-year horizon, moderate risk tolerance, low liquidity needs."
    )
    turn2 = (
        "Analyze Alex's financial health, generate the illustrative portfolio allocation, "
        "and explain the allocation using the knowledge base."
    )
    turn3 = (
        "Create a scenario where Alex increases monthly investment from ₹40,000 to ₹60,000 "
        "and compare it with the original baseline."
    )

    turns = [turn1, turn2, turn3]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir="tmp_video/",
            record_video_size={"width": 1280, "height": 720}
        )
        page = context.new_page()

        print("Navigating to deployed Cloud Run ADK Web UI...")
        page.goto(url, wait_until="networkidle")
        time.sleep(3)

        for idx, prompt_text in enumerate(turns, start=1):
            print(f"--- Executing Turn {idx} ---")
            # Wait for textarea to be visible and enabled (not disabled)
            textarea = page.locator("textarea:not([disabled])")
            textarea.wait_for(state="visible", timeout=60000)
            time.sleep(1)
            textarea.fill(prompt_text)
            time.sleep(1.5)
            
            # Press Enter to send message
            page.keyboard.press("Enter")
            
            # Wait for agent response to complete (textarea becomes enabled again)
            print(f"Waiting for agent response streaming in Turn {idx}...")
            time.sleep(3)
            page.locator("textarea:not([disabled])").wait_for(state="visible", timeout=90000)
            time.sleep(2)
            print(f"Turn {idx} complete.")

        print("Finished all 3 turns. Final pause for recording...")
        time.sleep(3)

        # Get video path before closing page
        video_path = page.video.path()
        context.close()
        browser.close()

        # Copy recorded file to docs/demo_recording.webm
        target_path = "docs/demo_recording.webm"
        if os.path.exists(video_path):
            shutil.copy(video_path, target_path)
            shutil.rmtree("tmp_video", ignore_errors=True)
            print(f"SUCCESS: Video saved to {target_path}")
            return target_path
        else:
            raise FileNotFoundError(f"Video file not found at {video_path}")

if __name__ == "__main__":
    record_demo()
