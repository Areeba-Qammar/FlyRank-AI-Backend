import json
import requests

BASE_URL = "http://127.0.0.1:8000"

def run():
    with open("evals/cases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)
    
    correct = 0
    for case in cases:
        res = requests.post(f"{BASE_URL}/enrich", json={"text": case["text"]})
        got = res.json().get("category") if res.status_code == 200 else f"HTTP {res.status_code}"
        ok = got == case["expected_category"]
        correct += ok
        print(f"{'PASS' if ok else 'FAIL'}: expected {case['expected_category']}, got {got} — {case['text'][:50]!r}")
    
    print(f"\n{correct}/{len(cases)} correct")

if __name__ == "__main__":
    run()