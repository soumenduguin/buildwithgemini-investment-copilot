import os
import shutil
import subprocess
import time

from playwright.sync_api import sync_playwright


def ensure_local_server():
    import urllib.request

    try:
        urllib.request.urlopen("http://127.0.0.1:8000/dev-ui/?app=app", timeout=2)
        print("Local server is already running.")
        return None
    except Exception:
        print("Starting local FastAPI server...")
        proc = subprocess.Popen(
            [
                "uv",
                "run",
                "python",
                "-m",
                "uvicorn",
                "app.fast_api_app:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for _ in range(30):
            time.sleep(1)
            try:
                urllib.request.urlopen(
                    "http://127.0.0.1:8000/dev-ui/?app=app", timeout=2
                )
                print("Local FastAPI server ready!")
                return proc
            except Exception:
                pass
        raise RuntimeError("Local server failed to start in 30 seconds.") from None


def convert_webm_to_gif(input_webm, output_gif):
    print(f"Converting {input_webm} to optimized looping GIF: {output_gif}...")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_webm,
        "-vf",
        "fps=10,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        output_gif,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(output_gif):
        print(f"SUCCESS: Generated GIF at {output_gif}")
    else:
        print(f"Warning: ffmpeg conversion returned {res.returncode}: {res.stderr}")


def record_demo():
    os.makedirs("docs", exist_ok=True)
    os.makedirs("tmp_video", exist_ok=True)

    server_proc = ensure_local_server()
    url = "http://127.0.0.1:8000/dev-ui/?app=app"

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

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path="/usr/bin/google-chrome",
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                record_video_dir="tmp_video/",
                record_video_size={"width": 1280, "height": 720},
            )
            page = context.new_page()

            print(f"Navigating to {url}...")
            page.goto(url, wait_until="networkidle")
            time.sleep(3)

            for idx, prompt_text in enumerate(turns, start=1):
                print(f"--- Executing Turn {idx} ---")
                textarea = page.locator("textarea").first
                textarea.wait_for(state="visible", timeout=30000)
                time.sleep(1)
                textarea.fill(prompt_text)
                time.sleep(1)

                page.keyboard.press("Enter")

                print(f"Streaming Turn {idx} response...")
                time.sleep(10)
                print(f"Turn {idx} complete.")

            print("Finished all 3 turns. Final pause for recording...")
            time.sleep(3)

            video_path = page.video.path()
            context.close()
            browser.close()

            target_webm = "docs/demo_recording.webm"
            target_gif = "docs/demo.gif"
            if os.path.exists(video_path):
                shutil.copy(video_path, target_webm)
                shutil.rmtree("tmp_video", ignore_errors=True)
                print(f"SUCCESS: Video saved to {target_webm}")
                convert_webm_to_gif(target_webm, target_gif)
                return target_webm
            else:
                raise FileNotFoundError(f"Video file not found at {video_path}")
    finally:
        if server_proc:
            print("Stopping background FastAPI server...")
            server_proc.terminate()
            server_proc.wait()


if __name__ == "__main__":
    record_demo()
