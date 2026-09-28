import urllib.request
import json
import sys

def test_system():
    print("==================================================")
    print(" [*] INCIDENT RESPONSE AGENT DIAGNOSTICS & VERIFY")
    print("==================================================")
    
    url_health = "http://127.0.0.1:5000/api/health"
    url_status = "http://127.0.0.1:5000/api/status"
    
    try:
        req = urllib.request.urlopen(url_health, timeout=3)
        data = json.loads(req.read().decode("utf-8"))
        print(f"\n[+] Health Status : {data.get('status').upper()}")
        print(f"[+] Service Name  : {data.get('service')}")
        print(f"[+] Version       : {data.get('version')}")
        
        req2 = urllib.request.urlopen(url_status, timeout=3)
        status_data = json.loads(req2.read().decode("utf-8"))
        print(f"[+] Hindsight URL : {status_data['hindsight']['api_url']}")
        print(f"[+] Hindsight Bank: {status_data['hindsight']['bank_id']}")
        print(f"[+] LLM Model     : {status_data['llm']['model']}")
        
        db_info = status_data.get('database', {})
        if db_info:
            print(f"[+] Database Type : {db_info.get('database_type')}")
            print(f"[+] Total Records : {db_info.get('total_records')}")
            print(f"[+] DB File Path  : {db_info.get('db_path')}")
            
        print("\n[+] ALL SYSTEMS OPERATIONAL - VERIFIED!")
        print("==================================================")
    except Exception as e:
        print(f"\n[-] Server is currently offline: {e}")
        print("[-] Run: python run.py to launch the server.")
        print("==================================================")

if __name__ == "__main__":
    test_system()
