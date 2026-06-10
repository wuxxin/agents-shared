import json
import os
import time
import urllib.request

target_path = "./DevToolsActivePort"

print(f"Starting DevToolsActivePort syncer targeting: {target_path}")

while True:
    try:
        with urllib.request.urlopen(
            "http://localhost:9222/json/version", timeout=2
        ) as response:
            data = json.loads(response.read().decode())
            ws_url = data.get("webSocketDebuggerUrl", "")
            if "devtools/browser/" in ws_url:
                uuid_path = "/devtools/browser/" + ws_url.split("devtools/browser/")[-1]
                content = f"9222\n{uuid_path}\n"

                # Check if it changed before writing to prevent file wear
                current = ""
                if os.path.exists(target_path):
                    with open(target_path, "r", encoding="utf-8") as f:
                        current = f.read()

                if current != content:
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Updated DevToolsActivePort with UUID: {uuid_path}")
    except Exception:
        # If port 9222 is closed or not responding, we just wait
        pass
    time.sleep(2)
