import argparse
import json
import subprocess
import time
import urllib.request


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True)
    parser.add_argument("--namespace", default="mlops-students")
    parser.add_argument("--port", type=int, default=18090)
    args = parser.parse_args()

    process = subprocess.Popen([
        "kubectl", "-n", args.namespace, "port-forward", f"service/{args.release}-mlops-search", f"{args.port}:80"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(20):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{args.port}/readyz", timeout=2) as response:
                    if response.status == 200:
                        break
            except Exception:
                time.sleep(0.5)
        payload = json.dumps({"query": "как вернуть предыдущую модель после плохого релиза", "limit": 3}).encode()
        request = urllib.request.Request(
            f"http://127.0.0.1:{args.port}/v1/search", data=payload, headers={"content-type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            result = json.load(response)
        assert result["results"][0]["id"] == "doc-rollback", result
        print(json.dumps(result, ensure_ascii=False))
    finally:
        process.terminate()
        process.wait(timeout=5)


if __name__ == "__main__":
    main()
