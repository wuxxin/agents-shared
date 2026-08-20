import json
import os
import socket
import subprocess
import time

# Test cases definition
TEST_CASES = [
    # 1. dGPU (ROCm0) parameter variations
    {"device": "ROCm0", "cache_type": "q4_0", "ctx_size": 4096},
    # 2. dGPU (Vulkan1) parameter variations
    {"device": "Vulkan1", "cache_type": "q4_0", "ctx_size": 4096},
    # 3. iGPU (Vulkan0) parameter variations
    {"device": "Vulkan0", "cache_type": "q4_0", "ctx_size": 4096},
    # 4. cpu
    {"device": "cpu", "cache_type": "q4_0", "ctx_size": 4096},
    {"device": "blas", "cache_type": "q4_0", "ctx_size": 4096},
]

PORT = 20095
MODEL_PATH = "/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
CONTEXT_FILE = "/data/public/machine-learning/models/completion/test_fim.py"


def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_vram_usage_mb(card_name):
    try:
        res = subprocess.run(
            ["/opt/rocm/bin/rocm-smi", "--showmeminfo", "vram", "--json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        json_str = ""
        for line in res.stdout.splitlines():
            if line.strip().startswith("{"):
                json_str = line
                break
        if json_str:
            data = json.loads(json_str)
            if card_name in data and "VRAM Total Used Memory (B)" in data[card_name]:
                return float(data[card_name]["VRAM Total Used Memory (B)"]) / (
                    1024 * 1024
                )
    except Exception:
        pass
    return 0.0


def run_test(case):
    device = case["device"]
    cache_type = case["cache_type"]
    ctx_size = case["ctx_size"]

    print("\n==================================================")
    print(f"Testing Device: {device} | Cache: {cache_type} | Ctx: {ctx_size}")
    print("==================================================")

    # Determine card name for VRAM querying
    card_name = (
        "card0"
        if "0" in device or "ROCm0" in device or "Vulkan1" in device
        else "card1"
    )
    if "ROCm1" in device or "Vulkan0" in device:
        card_name = "card1"

    baseline_vram = get_vram_usage_mb(card_name)
    print(f"Baseline VRAM: {baseline_vram:.2f} MB")

    cmd = [
        "/usr/bin/llama-server",
        "--model",
        MODEL_PATH,
        "--alias",
        "qwen-coder-fim",
        "--port",
        str(PORT),
        "--host",
        "127.0.0.1",
        "--ctx-size",
        str(ctx_size),
        "--cache-type-k",
        cache_type,
        "--cache-type-v",
        cache_type,
        "--n-gpu-layers",
        "999",
        "--flash-attn",
        "on",
        "--device",
        device,
        "--threads",
        "4",
    ]

    # Run server
    env = os.environ.copy()
    if "ROCm0" in device:
        env["HIP_VISIBLE_DEVICES"] = "0"
    elif "ROCm1" in device:
        env["HIP_VISIBLE_DEVICES"] = "1"

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
    )

    # Wait for port readiness
    ready = False
    for _ in range(15):
        if is_port_open(PORT):
            ready = True
            break
        if proc.poll() is not None:
            break
        time.sleep(1)

    if not ready:
        print("Server failed to start!")
        proc.kill()
        return None

    # Let the model load fully and query VRAM
    time.sleep(2)
    peak_vram = get_vram_usage_mb(card_name)
    print(f"Peak VRAM: {peak_vram:.2f} MB")
    vram_used = peak_vram - baseline_vram
    if vram_used < 0:
        vram_used = 0.0

    # Run completions benchmark
    bench_cmd = [
        "python3",
        "scripts/benchmark-helper.py",
        "--mode",
        "completion",
        "--url",
        f"http://127.0.0.1:{PORT}",
        "--model",
        "qwen-coder-fim",
        "--context",
        CONTEXT_FILE,
        "--repeat",
        "5",
        "--format",
        "json",
    ]

    bench_res = subprocess.run(bench_cmd, capture_output=True, text=True)

    # Kill server
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    # Parse JSON output from benchmark-helper
    output = bench_res.stdout
    idx = output.find("{")
    data = None
    if idx != -1:
        jdx = output.rfind("}")
        if jdx > idx:
            try:
                data = json.loads(output[idx : jdx + 1])
            except Exception:
                pass

    if data is None or "comp_avg_gen" not in data:
        print("Benchmark failed to return JSON metrics!")
        print(f"Stdout: {output}")
        print(f"Stderr: {bench_res.stderr}")
        return None

    res = {
        "device": device,
        "cache_type": cache_type,
        "ctx_size": ctx_size,
        "ttft_ms": float(data.get("comp_avg_ttft", 0.0)),
        "prefill_tps": float(data.get("comp_avg_prefill", 0.0)),
        "gen_tps": float(data.get("comp_avg_gen", 0.0)),
        "vram_used_mb": vram_used,
    }
    print(
        f"Metrics: TTFT={res['ttft_ms']:.2f}ms, Prefill={res['prefill_tps']:.2f} t/s, Gen={res['gen_tps']:.2f} t/s, VRAM={res['vram_used_mb']:.2f} MB"
    )
    return res


results = []
for case in TEST_CASES:
    res = run_test(case)
    if res:
        results.append(res)

# Print markdown comparison table
print("\n\n### FIM Completions Benchmark Performance Comparison")
print(
    "| Device | Cache Type | Context Size | Avg TTFT | Prefill Speed | Generation Speed | GPU VRAM Used |"
)
print("|---|---|---|---|---|---|---|")
for r in results:
    print(
        f"| {r['device']} | {r['cache_type']} | {r['ctx_size']} | {r['ttft_ms']:.2f} ms | {r['prefill_tps']:.2f} t/s | {r['gen_tps']:.2f} t/s | {r['vram_used_mb']:.1f} MB |"
    )
