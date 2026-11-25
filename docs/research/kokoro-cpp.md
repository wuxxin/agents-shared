# kokoro.cpp: Standalone C++ & Vulkan GGML Engine Guide

This document preserves the architecture, build procedure, benchmarking data, and packaging specifications for **`kokoro.cpp`** ([simonfxr/kokoro.cpp](https://github.com/simonfxr/kokoro.cpp)).

---

## 1. Overview & Capabilities

`kokoro.cpp` is a zero-Python C/C++ inference runtime for the 82M-parameter Kokoro TTS architecture, powered by **`ggml`** and **Google Highway** portable SIMD:

* **Hardware Acceleration**:
  - **Vulkan Backend**: Custom compute shaders running on AMD integrated APUs (e.g. Renoir gfx90c) and discrete GPUs (e.g. RX 7900 XTX Navi31).
  - **CPU Backend**: Vectorized matrix multiplication via Google Highway SIMD (AVX2 on x86_64).
* **Memory Efficiency**:
  - Requires only **~205 MB** host RAM when running on Vulkan.
  - Consumes **0 MB discrete GPU VRAM** when targeted at `Vulkan0` (integrated APU with UMA unified memory).
* **Format**: Consumes models in GGUF format (`kokoro-82m-q8_0.gguf`, `kokoro-de-hui-base-q8_0.gguf`, and `kokoro-voice-*.gguf`).

---

## 2. Compilation from Source

`kokoro.cpp` requires CMake 3.14+, GCC/Clang with C++17 support, the Vulkan SDK loader, and `glslc` (from `shaderc`):

```bash
# Clone with recursive submodules (ggml and highway)
git clone --recurse-submodules https://github.com/simonfxr/kokoro.cpp scratch/kokoro-cpp
cd scratch/kokoro-cpp

# Configure with Vulkan compute shader generation enabled
cmake -B build -S . \
    -DCMAKE_BUILD_TYPE=Release \
    -DKOKORO_VULKAN=ON \
    -DKOKORO_BUILD_CLI=ON

# Build in parallel
cmake --build build -j$(nproc)
```

The build produces:
* `build/kokoro-cli`: Standalone CLI executable.
* `build/libkokoro.a`: Static C/C++ inference library with C ABI (`include/kokoro.h`).
* `build/ggml/src/ggml-vulkan/libggml-vulkan.a`: Compiled Vulkan compute shaders.

---

## 3. Benchmarked Performance (Ryzen 7 PRO 5750G + RX 7900 XTX)

Tested on a 21-word German utterance (3.22 s audio):

| Backend & Device | Synthesis Wall Time | Real-Time Factor (RTF) | Realtime Multiplier | CPU Load | Host RAM (RSS) | dGPU VRAM |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Vulkan1 (RX 7900 XTX dGPU)** | **0.79 s** | **0.249** | **4.01× RT** | 147% | 209 MB | ~120 MB |
| **Vulkan0 (Renoir APU iGPU)**  | **1.05 s** | **0.325** | **3.08× RT** | **111%** | **205 MB** | **0 MB** |
| **CPU (Highway SIMD AVX2)**    | 1.86 s | 0.577 | 1.73× RT | 592% | 601 MB | 0 MB |

---

## 4. Arch Linux Packaging Strategy

### Option A: Submodule Integration in `aur-packages/libggml-git-hip`
`kokoro.cpp` can be integrated directly alongside `qwen3-tts` in `../aur-packages/libggml-git-hip/`:
1. Vendor `kokoro.cpp` in `src/kokoro-cpp`.
2. Apply a patch redirecting `ggml` linkage to system `/usr/lib/libggml.so` (`-DKOKORO_GGML_DIR=/usr/include/ggml`).
3. Install the resulting binary as `/usr/bin/kokoro-cli`.

### Option B: Standalone AUR PKGBUILD (`kokoro.cpp-git`)
A separate package definition:
* **Package Name**: `kokoro.cpp-git`
* **Depends**: `glibc`, `gcc-libs`, `vulkan-icd-loader`, `espeak-ng`
* **Makedepends**: `git`, `cmake`, `shaderc` (provides `glslc`), `vulkan-headers`
* **Build Command**: `cmake -B build -S . -DCMAKE_BUILD_TYPE=Release -DKOKORO_VULKAN=ON`
* **Output Binary**: `/usr/bin/kokoro-cli`

---

## 5. CLI Invocation Reference

```bash
# English speech on Vulkan APU (Device 0)
kokoro-cli \
    -m models/kokoro-82m-q8_0.gguf \
    -v models/voices/kokoro-voice-af_heart.gguf \
    -l en-us --backend vulkan --device 0 \
    -o output_en.wav \
    "Good day! Speech synthesis runs completely offline on your local machine."

# Native German speech on Vulkan APU (Device 0)
kokoro-cli \
    -m models/kokoro-de-hui-base-q8_0.gguf \
    -v models/voices/kokoro-voice-dm_martin.gguf \
    -l de --backend vulkan --device 0 \
    -o output_de.wav \
    "Guten Tag! Die künstliche Intelligenz ermöglicht natürliche deutsche Sprachsynthese."
```
