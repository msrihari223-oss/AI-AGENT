import os
import sys
import time
import socket
import subprocess
import webbrowser
import threading
import uvicorn

PORT = 5000
HOST = "127.0.0.1"

def free_port(port):
    """Automatically clears any old process holding the port so Errno 10048 never happens."""
    try:
        # Check port in Windows netstat
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True
        )
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                pid = parts[-1]
                if pid and pid != "0" and pid != str(os.getpid()):
                    print(f"[!] Freeing port {port} from old process (PID {pid})...")
                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                    time.sleep(0.5)
    except Exception as e:
        pass

def open_browser():
    time.sleep(1.2)
    print("\n" + "="*60)
    print(" [>] INCIDENT RESPONSE AGENT - SOC AI PLATFORM IS LIVE!")
    print("="*60)
    print(f" [*] Dashboard        : http://{HOST}:{PORT}/dashboard")
    print(f" [*] New Incident     : http://{HOST}:{PORT}/incident")
    print(f" [*] Security Memory  : http://{HOST}:{PORT}/memory")
    print(f" [*] Incident Reports : http://{HOST}:{PORT}/reports")
    print(f" [*] API Docs         : http://{HOST}:{PORT}/api/docs")
    print("="*60)
    print(" Opening browser...\n")
    try:
        webbrowser.open(f"http://{HOST}:{PORT}/dashboard")
    except Exception:
        pass

if __name__ == "__main__":
    # 1. Automatically clear port 5000 if occupied
    free_port(PORT)
    
    # 2. Open browser automatically in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 3. Start Uvicorn Server with hot reload
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
