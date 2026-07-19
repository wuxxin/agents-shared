#!/usr/bin/env python3
import sys
import argparse
import time
import asyncio
from hindsight_client import Hindsight

async def run_test(base_url: str, bank_id: str):
    print(f"Connecting to Hindsight server at: {base_url} ...")
    client = Hindsight(base_url=base_url)
    
    # Check version first to verify connectivity
    try:
        ver = await client.aget_version()
        print(f"Connected successfully. Hindsight server version: {ver.api_version}")
    except Exception as e:
        print(f"Error: Failed to connect to Hindsight server version endpoint: {e}", file=sys.stderr)
        return 1

    # 1. Test retain_batch (Storing facts)
    print("\n1. Testing retain (storing test memory)...")
    test_doc_id = f"test-session-{int(time.time())}"
    item = {
        "document_id": test_doc_id,
        "mode": "append",
        "content": "My primary programming language is Python and I am developing a memory feature."
    }
    
    try:
        await client.aretain_batch(bank_id=bank_id, items=[item])
        print("Success: Memory stored successfully.")
    except Exception as e:
        print(f"Error: Failed to retain memory: {e}", file=sys.stderr)
        await client.aclose()
        return 1

    # Give a tiny buffer for background workers / DB indexing
    print("Waiting 1s for memory indexing...")
    await asyncio.sleep(1.0)

    # 2. Test recall (Retrieving facts)
    print("\n2. Testing recall (retrieving facts)...")
    try:
        resp = await client.arecall(bank_id=bank_id, query="What is my primary programming language?")
        results = resp.results or []
        print(f"Success: Recall returned {len(results)} results:")
        for idx, res in enumerate(results, 1):
            print(f"  {idx}. {res.text}")
        if not results:
            print("Warning: Recall succeeded but returned 0 results.", file=sys.stderr)
    except Exception as e:
        print(f"Error: Failed to recall memories: {e}", file=sys.stderr)
        await client.aclose()
        return 1

    # 3. Test reflect (Synthesizing memories)
    print("\n3. Testing reflect (reflecting/synthesizing memories)...")
    try:
        resp = await client.areflect(bank_id=bank_id, query="Summarize what you know about my development context.")
        text = resp.text or ""
        print("Success: Reflect output:")
        print(text)
        if not text:
            print("Warning: Reflect succeeded but returned empty text.", file=sys.stderr)
    except Exception as e:
        print(f"Error: Failed to reflect: {e}", file=sys.stderr)
        await client.aclose()
        return 1

    await client.aclose()
    print("\nAll Hindsight memory verification tests completed successfully!")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Hindsight Memory API integration tests")
    parser.add_argument("--host", default="127.0.0.1", help="Hindsight service host")
    parser.add_argument("--port", type=int, default=8888, help="Hindsight service port")
    parser.add_argument("--bank", default="hermes-test-bank", help="Test bank identifier")
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    sys.exit(asyncio.run(run_test(base_url, args.bank)))

if __name__ == "__main__":
    main()
