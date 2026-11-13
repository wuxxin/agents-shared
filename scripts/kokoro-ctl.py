#!/usr/bin/env python3
"""Unified High-Performance Engine, Server & CLI for Kokoro ONNX TTS (kokoro-ctl.py).

Pure Python & ONNX Runtime implementation with zero subshell dependencies.

Usage:
1. CLI Speech Synthesis:
     ./scripts/kokoro-ctl.py -v af_heart -p "Hello world"
     ./scripts/kokoro-ctl.py -v dm_martin -p "Guten Tag, das ist die deutsche Martin Stimme."
     ./scripts/kokoro-ctl.py -v df_victoria -p "Guten Tag, hier spricht Victoria."
     echo "Piped text" | ./scripts/kokoro-ctl.py -v am_adam -p

2. OpenAI-Compatible HTTP Server Mode:
     ./scripts/kokoro-ctl.py --server --port 20095

3. Voice Management & Diagnostics:
     ./scripts/kokoro-ctl.py --check-deps
     ./scripts/kokoro-ctl.py --list-voices
     ./scripts/kokoro-ctl.py --convert-voice <source.gguf|safetensors|npz> [destination.bin]

Features:
- Pure CPU execution via system ONNX Runtime (CPUExecutionProvider with AVX2 MLAS, 4.6x real-time).
- C API libespeak-ng IPC phonemization with Kokoro ligature mapping (dʒ -> ʤ, tʃ -> ʧ, r -> ɹ, ʏ -> y).
- Token-length indexed style vector selection (voice[L-1]) ensuring natural duration and untruncated speech.
- Voice blending / linear style combinations: e.g. "df_kerstin(0.6)+dm_martin(0.4)".
- Multi-speaker inline dialogue switching: e.g. "[voice:af_heart] Hello! [voice:dm_martin] Guten Tag!".
- Inline pause and break tags: e.g. "[pause:500ms]" or "[pause:1.5s]".
- Output formats: WAV (audio/wav), raw PCM (audio/pcm), and compressed OGG/Opus (audio/ogg).
- In-process audio playback via python-sounddevice (PortAudio/PipeWire) with 0 subprocess exec spawning.
"""

import argparse
import ctypes
import ctypes.util
import io
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import AsyncGenerator, Dict, Generator, List, Optional, Tuple

# ------------------------------------------------------------------------------
# Dependency Diagnostic & Arch Linux / AUR Package Mapping
# ------------------------------------------------------------------------------
ARCH_DEPS = {
    "numpy": ("python-numpy", "pacman", "Arch official repo", "Vector operations"),
    "onnxruntime": (
        "python-onnxruntime",
        "pacman",
        "Arch official repo",
        "AVX2 MLAS neural inference",
    ),
    "soundfile": (
        "python-soundfile",
        "pacman",
        "Arch official repo",
        "Audio encoding (WAV/OGG/Opus)",
    ),
    "fastapi": ("python-fastapi", "pacman", "Arch official repo", "OpenAI HTTP API server"),
    "uvicorn": ("python-uvicorn", "pacman", "Arch official repo", "ASGI production server"),
    "sounddevice": (
        "python-sounddevice",
        "pacman",
        "Arch official repo",
        "In-process audio playback (0 exec spawn)",
    ),
}

OPTIONAL_ARCH_DEPS = {
    "gguf": ("python-gguf", "yay", "AUR", "GGUF voicepack conversion"),
    "safetensors": (
        "python-safetensors",
        "pacman",
        "Arch official repo",
        "Safetensors voicepack conversion",
    ),
}


def check_and_print_deps():
    print("=" * 76)
    print(" Kokoro TTS Dependency Status (Arch Linux / Manjaro)")
    print("=" * 76)
    print(f"{'Component':<18} {'Status':<12} {'Arch/AUR Package':<24} {'Source'}")
    print("-" * 76)

    missing_pacman = []
    missing_aur = []

    for mod, (pkg, mgr, src, _desc) in ARCH_DEPS.items():
        installed = False
        try:
            __import__(mod)
            installed = True
        except ImportError:
            pass
        status_str = "Installed" if installed else "MISSING"
        print(f"{mod:<18} {status_str:<12} {pkg:<24} {src}")
        if not installed:
            if mgr == "pacman":
                missing_pacman.append(pkg)
            else:
                missing_aur.append(pkg)

    for mod, (pkg, mgr, src, _desc) in OPTIONAL_ARCH_DEPS.items():
        installed = False
        try:
            __import__(mod)
            installed = True
        except ImportError:
            pass
        status_str = "Installed" if installed else "Optional"
        print(f"{mod + ' (conv)':<18} {status_str:<12} {pkg:<24} {src}")
        if not installed:
            if mgr == "pacman":
                missing_pacman.append(pkg)
            else:
                missing_aur.append(pkg)

    espeak_installed = os.path.exists("/usr/lib/libespeak-ng.so") or bool(
        ctypes.util.find_library("espeak-ng")
    )
    status_str = "Installed" if espeak_installed else "MISSING"
    print(f"{'libespeak-ng.so':<18} {status_str:<12} {'espeak-ng':<24} Arch official repo")
    if not espeak_installed:
        missing_pacman.append("espeak-ng")

    print("-" * 76)
    if not missing_pacman and not missing_aur:
        print("All required and optional dependencies are installed!")
    else:
        if missing_pacman:
            print(f"To install missing Arch packages:  sudo pacman -S {' '.join(missing_pacman)}")
        if missing_aur:
            print(f"To install missing AUR packages:   yay -S {' '.join(missing_aur)}")
    print("=" * 76)


if "--check-deps" in sys.argv:
    check_and_print_deps()
    sys.exit(0)

# Verify required dependencies before importing
_missing = []
for _mod, (_pkg, _mgr, _src, _desc) in ARCH_DEPS.items():
    try:
        __import__(_mod)
    except ImportError:
        _missing.append((_mod, _pkg, _mgr, _src))

if _missing:
    print("=" * 72, file=sys.stderr)
    print(" Kokoro TTS Error: Missing required Python dependencies", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    for _mod, _pkg, _mgr, _src in _missing:
        print(f"  • Module '{_mod}' missing -> Arch Package: {_pkg} ({_src})", file=sys.stderr)
    print("\nTo install missing packages on Arch Linux / Manjaro:", file=sys.stderr)
    _pacman_pkgs = " ".join([_pkg for _, _pkg, _mgr, _ in _missing if _mgr == "pacman"])
    if _pacman_pkgs:
        print(f"  sudo pacman -S {_pacman_pkgs}", file=sys.stderr)
    _aur_pkgs = " ".join([_pkg for _, _pkg, _mgr, _ in _missing if _mgr == "yay"])
    if _aur_pkgs:
        print(f"  yay -S {_aur_pkgs}", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    sys.exit(1)

import fastapi  # noqa: E402
import numpy as np  # noqa: E402
import onnxruntime as ort  # noqa: E402
import soundfile as sf  # noqa: E402
import uvicorn  # noqa: E402
from fastapi.responses import Response, StreamingResponse  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("kokoro-ctl")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

# Search paths for models
MODEL_EN_SEARCH_PATHS = [
    "/data/public/machine-learning/models/text-to-speech/kokoro-onnx/model.onnx",
    "/data/public/machine-learning/models/text-to-speech/kokoro-onnx/onnx/model.onnx",
    os.path.expanduser("~/.cache/kokoro/multilingual-onnx/onnx/model.onnx"),
    os.path.expanduser("~/.cache/kokoro/Kokoro-82M-v1.0-ONNX/onnx/model.onnx"),
    "/data/public/machine-learning/models/text-to-speech/Kokoro-82M-ONNX/onnx/model.onnx",
]

MODEL_DE_SEARCH_PATHS = [
    "/data/public/machine-learning/models/text-to-speech/kokoro-onnx/model-de.onnx",
    "/data/public/machine-learning/models/text-to-speech/kokoro-onnx/kokoro-martin.onnx",
    os.path.expanduser("~/.cache/kokoro/german-martin-onnx/kokoro-martin.onnx"),
    "/data/public/machine-learning/models/text-to-speech/Kokoro-82M-German-Martin-ONNX/kokoro-martin.onnx",
    "/data/public/machine-learning/models/text-to-speech/Kokoro-82M-v1.0-German-ONNX/onnx/model.onnx",
]

TOKENIZER_SEARCH_PATHS = [
    "/data/public/machine-learning/models/text-to-speech/kokoro-onnx/tokenizer.json",
    "/data/public/machine-learning/models/text-to-speech/Kokoro-82M-v1.0-German-ONNX/tokenizer.json",
    os.path.expanduser("~/.cache/kokoro/multilingual-onnx/tokenizer.json"),
]

VOICE_SEARCH_DIRS = [
    "/data/public/machine-learning/models/text-to-speech/kokoro-onnx/voices",
    os.path.expanduser("~/.cache/kokoro/voices"),
    os.path.expanduser("~/.cache/kokoro/german-martin-onnx"),
    os.path.expanduser("~/.cache/kokoro/german-victoria-onnx/voices"),
    "/data/public/machine-learning/models/text-to-speech/Kokoro-82M-v1.0-German-ONNX/voices",
    os.path.join(REPO_ROOT, "scratch/kokoro-cpp/models/voices"),
]


def parse_pause_tag(duration_str: str) -> float:
    """Parses pause strings like '500ms', '1.5s', '2s' to seconds."""
    duration_str = duration_str.strip().lower()
    if duration_str.endswith("ms"):
        return max(0.0, float(duration_str[:-2]) / 1000.0)
    elif duration_str.endswith("s"):
        return max(0.0, float(duration_str[:-1]))
    else:
        try:
            return max(0.0, float(duration_str))
        except ValueError:
            return 0.3


class EspeakPhonemizer:
    """Direct, robust wrapper around libespeak-ng.so via ctypes."""

    def __init__(self):
        import atexit

        try:
            self.lib = ctypes.cdll.LoadLibrary("libespeak-ng.so")
        except OSError:
            print("=" * 72, file=sys.stderr)
            print(" Kokoro TTS Error: 'libespeak-ng.so' not found on system", file=sys.stderr)
            print("=" * 72, file=sys.stderr)
            print(" Arch Linux package required: espeak-ng (Arch official repo)", file=sys.stderr)
            print(" Install via pacman:", file=sys.stderr)
            print("   sudo pacman -S espeak-ng", file=sys.stderr)
            print("=" * 72, file=sys.stderr)
            sys.exit(1)
        # Initialize with synchronous audio output, IPA phonemes, and don't exit
        self.lib.espeak_Initialize(2, 0, None, 2 | 4)
        self.fcn = self.lib.espeak_TextToPhonemes
        self.fcn.restype = ctypes.c_char_p
        self.fcn.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_int, ctypes.c_int]
        self.current_voice = ""
        atexit.register(self._cleanup)

    def _cleanup(self):
        try:
            self.lib.espeak_Terminate()
        except Exception:
            pass

    def set_voice(self, voice_code: str):
        if self.current_voice != voice_code:
            ret = self.lib.espeak_SetVoiceByName(voice_code.encode("utf-8"))
            if ret != 0:
                self.lib.espeak_SetVoiceByName(b"en")
            self.current_voice = voice_code

    def phonemize(self, text: str, lang: str = "en-us") -> str:
        self.set_voice(lang)
        text_p = ctypes.c_char_p(text.encode("utf-8"))
        res = []
        while text_p.value:
            chunk = self.fcn(ctypes.byref(text_p), 1, 2)
            if chunk:
                res.append(chunk.decode("utf-8"))
        ipa = " ".join(res)
        # Apply standard Kokoro IPA ligature & phoneme substitutions
        ipa = (
            ipa.replace("dʒ", "ʤ")
            .replace("tʃ", "ʧ")
            .replace("r", "ɹ")
            .replace("ʏ", "y")
            .replace("kəkˈoːɹoʊ", "kˈoʊkəɹoʊ")
            .replace("ʲ", "j")
            .replace("x", "k")
            .replace("ɬ", "l")
        )
        return ipa.strip()


def convert_voice_file(src_path: str, dst_path: Optional[str] = None) -> str:
    """Converts a voice embedding from GGUF, Safetensors, or NPZ to standard Kokoro ONNX .bin format."""
    src = Path(src_path)
    if not src.is_file():
        raise FileNotFoundError(f"Source voice file not found: {src_path}")

    if not dst_path:
        stem = src.stem
        if stem.startswith("kokoro-voice-"):
            stem = stem.replace("kokoro-voice-", "")
        if stem.lower() == "heinrich":
            stem = "dm_heinrich"
        elif stem.lower() == "anna":
            stem = "df_anna"
        elif stem.lower() == "voices-martin":
            stem = "dm_martin"

        voices_dir = Path(os.path.expanduser("~/.cache/kokoro/voices"))
        voices_dir.mkdir(parents=True, exist_ok=True)
        dst_path = str(voices_dir / f"{stem}.bin")

    ext = src.suffix.lower()
    mat: Optional[np.ndarray] = None

    if ext == ".gguf":
        try:
            import gguf
        except ImportError:
            print("=" * 72, file=sys.stderr)
            print(" Error: Converting GGUF voicepacks requires 'python-gguf'", file=sys.stderr)
            print("=" * 72, file=sys.stderr)
            print(" Arch Linux / AUR Package required: python-gguf", file=sys.stderr)
            print(" Install via AUR:", file=sys.stderr)
            print("   yay -S python-gguf  (or paru -S python-gguf)", file=sys.stderr)
            print("=" * 72, file=sys.stderr)
            sys.exit(1)

        reader = gguf.GGUFReader(str(src))
        tensor = None
        for t in reader.tensors:
            if t.name == "voice.pack":
                tensor = t
                break
        if tensor is None and len(reader.tensors) > 0:
            tensor = reader.tensors[0]

        if tensor is None:
            raise ValueError(f"No valid tensor found in GGUF file {src}")

        mat = tensor.data.astype(np.float32).reshape(-1, 256)

    elif ext == ".safetensors":
        try:
            from safetensors.numpy import load_file
        except ImportError:
            print("=" * 72, file=sys.stderr)
            print(
                " Error: Converting Safetensors voicepacks requires 'python-safetensors'",
                file=sys.stderr,
            )
            print("=" * 72, file=sys.stderr)
            print(
                " Arch Linux Package required: python-safetensors (Arch official repo)",
                file=sys.stderr,
            )
            print(" Install via pacman:", file=sys.stderr)
            print("   sudo pacman -S python-safetensors", file=sys.stderr)
            print("=" * 72, file=sys.stderr)
            sys.exit(1)

        data = load_file(str(src))
        val = next(iter(data.values())).astype(np.float32)
        if val.ndim == 1 and val.shape[0] == 256:
            mat = np.tile(val, (510, 1))
        else:
            mat = val.reshape(-1, 256)

    elif ext == ".npz":
        npz_data = np.load(str(src))
        val = next(iter(npz_data.values())).astype(np.float32)
        mat = val.reshape(-1, 256)

    elif ext == ".bin":
        mat = np.fromfile(str(src), dtype=np.float32).reshape(-1, 256)
    else:
        raise ValueError(
            f"Unsupported file format '{ext}'. Supported: .gguf, .safetensors, .npz, .bin"
        )

    if mat is None or mat.shape[1] != 256:
        raise ValueError(f"Failed to extract valid (N, 256) float32 matrix from {src}")

    if mat.shape[0] == 1:
        mat = np.tile(mat, (510, 1))

    dst = Path(dst_path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    mat.astype(np.float32).tofile(str(dst))
    return str(dst)


class KokoroPureEngine:
    """Pure Python ONNX Runtime Engine for Kokoro-82M."""

    VOICE_LANG_MAP = {
        "d": "de",
        "a": "en-us",
        "b": "en",
        "e": "es",
        "f": "fr-fr",
        "i": "it",
        "p": "pt-br",
        "h": "hi",
        "j": "ja",
        "z": "cmn",
    }

    def __init__(self, model_path: Optional[str] = None, num_threads: int = 8):
        self.num_threads = num_threads

        # Load vocabulary
        tok_file = self._find_tokenizer()
        with open(tok_file, "r", encoding="utf-8") as f:
            tok_data = json.load(f)
        if "model" in tok_data and "vocab" in tok_data["model"]:
            self.vocab = tok_data["model"]["vocab"]
        elif "vocab" in tok_data:
            self.vocab = tok_data["vocab"]
        else:
            raise ValueError(f"Could not parse vocabulary from {tok_file}")

        # Initialize ONNX Runtime session options
        sess_opts = ort.SessionOptions()
        sess_opts.intra_op_num_threads = self.num_threads
        sess_opts.inter_op_num_threads = 1
        sess_opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        sess_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        # Model paths resolution
        if model_path and os.path.isdir(model_path):
            en_candidates = [
                os.path.join(model_path, "model.onnx"),
                os.path.join(model_path, "onnx", "model.onnx"),
            ]
            self.model_en_path = None
            for c in en_candidates:
                if os.path.isfile(c):
                    self.model_en_path = c
                    break
            if not self.model_en_path:
                self.model_en_path = self._find_first(MODEL_EN_SEARCH_PATHS)

            de_candidates = [
                os.path.join(model_path, "model-de.onnx"),
                os.path.join(model_path, "kokoro-martin.onnx"),
            ]
            self.model_de_path = None
            for c in de_candidates:
                if os.path.isfile(c):
                    self.model_de_path = c
                    break
            if not self.model_de_path:
                self.model_de_path = self._find_first(MODEL_DE_SEARCH_PATHS)

            v_dir = os.path.join(model_path, "voices")
            if os.path.isdir(v_dir) and v_dir not in VOICE_SEARCH_DIRS:
                VOICE_SEARCH_DIRS.insert(0, v_dir)
        else:
            self.model_en_path = model_path or self._find_first(MODEL_EN_SEARCH_PATHS)
            self.model_de_path = self._find_first(MODEL_DE_SEARCH_PATHS)

        if not self.model_en_path or not os.path.isfile(self.model_en_path):
            raise FileNotFoundError("Multilingual Kokoro ONNX model not found.")
        logger.info("Loading English/Multilingual ONNX model: %s", self.model_en_path)
        self.session_en = ort.InferenceSession(
            self.model_en_path, sess_opts, providers=["CPUExecutionProvider"]
        )

        # German session
        if self.model_de_path and os.path.isfile(self.model_de_path):
            logger.info("Loading Native German ONNX model: %s", self.model_de_path)
            self.session_de = ort.InferenceSession(
                self.model_de_path, sess_opts, providers=["CPUExecutionProvider"]
            )
            self.input_de_name = self.session_de.get_inputs()[0].name  # 'tokens' or 'input_ids'
        else:
            self.session_de = self.session_en
            self.input_de_name = "input_ids"

        self.phonemizer = EspeakPhonemizer()
        self.voice_raw_cache: Dict[str, np.ndarray] = {}

    def _find_first(self, paths: List[str]) -> Optional[str]:
        for p in paths:
            if os.path.isfile(p):
                return p
        return None

    def _find_tokenizer(self) -> str:
        for p in TOKENIZER_SEARCH_PATHS:
            if os.path.isfile(p):
                return p
        raise FileNotFoundError("tokenizer.json not found in search paths.")

    def _load_voice_matrix(self, voice_name: str) -> np.ndarray:
        """Loads (510, 256) float32 style matrix from disk."""
        v_clean = voice_name.strip()
        v_clean = re.sub(r"^kokoro-voice-", "", v_clean)
        v_clean = re.sub(r"\.(bin|gguf|pt)$", "", v_clean)

        if v_clean in self.voice_raw_cache:
            return self.voice_raw_cache[v_clean]

        for v_dir in VOICE_SEARCH_DIRS:
            if not os.path.isdir(v_dir):
                continue
            # Check .bin
            bin_cand = os.path.join(v_dir, f"{v_clean}.bin")
            if os.path.isfile(bin_cand):
                arr = np.fromfile(bin_cand, dtype=np.float32).reshape(-1, 256)
                self.voice_raw_cache[v_clean] = arr
                return arr
            # Check .npz
            for npz_name in ["voices-martin.npz", f"{v_clean}.npz"]:
                npz_cand = os.path.join(v_dir, npz_name)
                if os.path.isfile(npz_cand):
                    data = np.load(npz_cand)
                    for k in [v_clean, "martin", list(data.keys())[0]]:
                        if k in data:
                            arr = data[k].astype(np.float32).reshape(-1, 256)
                            self.voice_raw_cache[v_clean] = arr
                            return arr
            # Check .gguf
            for gguf_name in [f"kokoro-voice-{v_clean}.gguf", f"{v_clean}.gguf"]:
                gguf_cand = os.path.join(v_dir, gguf_name)
                if os.path.isfile(gguf_cand):
                    import gguf

                    reader = gguf.GGUFReader(gguf_cand)
                    for tensor in reader.tensors:
                        if tensor.name == "voice.pack":
                            t_data = tensor.data.astype(np.float32)
                            arr = t_data.reshape(-1, 256)
                            self.voice_raw_cache[v_clean] = arr
                            return arr
        available = list_available_voices()
        if available:
            fallback = available[0]
            logger.warning("Voice '%s' not found. Falling back to '%s'", voice_name, fallback)
            return self._load_voice_matrix(fallback)
        raise FileNotFoundError(f"Voice file for '{voice_name}' not found.")

    def has_voice(self, voice_name: str) -> bool:
        """Checks if a voice exists as a .bin file or in cache."""
        if not voice_name:
            return False
        v_clean = voice_name.strip()
        v_clean = re.sub(r"^kokoro-voice-", "", v_clean)
        v_clean = re.sub(r"\.(bin|gguf|pt|npz|safetensors)$", "", v_clean)
        if v_clean in self.voice_raw_cache:
            return True
        for v_dir in VOICE_SEARCH_DIRS:
            if os.path.isdir(v_dir) and os.path.isfile(os.path.join(v_dir, f"{v_clean}.bin")):
                return True
        return False

    def get_style_for_tokens(self, voice_expr: str, token_count: int) -> np.ndarray:
        """Retrieves style vector indexed by token length: voice[L-1]. Supports blends."""
        voice_expr = voice_expr.strip()
        row_idx = min(max(0, token_count - 1), 509)

        if "+" not in voice_expr:
            clean = re.sub(r"\([^)]*\)", "", voice_expr).strip()
            matrix = self._load_voice_matrix(clean)
            idx = min(row_idx, matrix.shape[0] - 1)
            return matrix[idx : idx + 1]

        # Voice blend: e.g. "df_kerstin(0.6)+dm_martin(0.4)"
        parts = voice_expr.split("+")
        names: List[str] = []
        weights: List[float] = []
        for p in parts:
            p = p.strip()
            m = re.match(r"^([a-zA-Z0-9_-]+)(?:\(([0-9.]+)\))?$", p)
            if m:
                names.append(m.group(1))
                w = float(m.group(2)) if m.group(2) else 1.0
                weights.append(max(0.0, w))

        if not names:
            names = ["af_heart"]
            weights = [1.0]

        total_w = sum(weights)
        if total_w > 0:
            weights = [w / total_w for w in weights]

        combined = np.zeros((1, 256), dtype=np.float32)
        for name, w in zip(names, weights):
            mat = self._load_voice_matrix(name)
            idx = min(row_idx, mat.shape[0] - 1)
            combined += mat[idx : idx + 1] * w

        return combined

    def get_language(self, voice_expr: str) -> str:
        clean = voice_expr.split("+")[0].strip()
        clean = re.sub(r"\([^)]*\)", "", clean).strip()
        prefix = clean[0].lower() if clean else "d"
        return self.VOICE_LANG_MAP.get(prefix, "de")

    def tokens_from_ipa(self, ipa: str) -> List[int]:
        tokens = [0]  # BOS
        for char in ipa:
            if char in self.vocab:
                tokens.append(self.vocab[char])
        if "." in self.vocab and (len(tokens) <= 1 or tokens[-1] != self.vocab["."]):
            tokens.append(self.vocab["."])
        tokens.append(0)  # EOS
        return tokens

    def synthesize_chunk(
        self, tokens: List[int], style_vector: np.ndarray, speed: float = 1.0, lang: str = "en-us"
    ) -> np.ndarray:
        if len(tokens) <= 2:
            return np.zeros((0,), dtype=np.float32)
        if len(tokens) > 510:
            tokens = tokens[:510]

        input_arr = np.array([tokens], dtype=np.int64)

        if lang == "de" and self.session_de is not None:
            sess = self.session_de
            in_name = self.input_de_name
            speed_val = speed if speed != 1.0 else 1.125
        else:
            sess = self.session_en
            in_name = "input_ids"
            speed_val = speed

        speed_tensor = np.array([speed_val], dtype=np.float32)
        outputs = sess.run(
            None,
            {
                in_name: input_arr,
                "style": style_vector,
                "speed": speed_tensor,
            },
        )
        return outputs[0].flatten()

    def parse_utterance(self, text: str, default_voice: str) -> List[Tuple[str, str, str]]:
        tag_pattern = re.compile(r"\[(voice|pause):([^\]]+)\]", re.IGNORECASE)
        segments: List[Tuple[str, str, str]] = []
        current_voice = default_voice
        last_idx = 0

        for m in tag_pattern.finditer(text):
            start, end = m.span()
            if start > last_idx:
                preceding = text[last_idx:start].strip()
                if preceding:
                    segments.append(("text", preceding, current_voice))

            tag_type = m.group(1).lower()
            tag_val = m.group(2).strip()

            if tag_type == "voice":
                current_voice = tag_val
            elif tag_type == "pause":
                segments.append(("pause", tag_val, current_voice))

            last_idx = end

        if last_idx < len(text):
            remainder = text[last_idx:].strip()
            if remainder:
                segments.append(("text", remainder, current_voice))

        return segments

    def stream_synthesize(
        self, text: str, voice: str = "af_heart", speed: float = 1.0
    ) -> Generator[np.ndarray, None, None]:
        segments = self.parse_utterance(text, voice)
        if not segments:
            segments = [("text", text.strip(), voice)]

        default_pause = np.zeros(int(24000 * 0.15), dtype=np.float32)

        for kind, content, active_voice in segments:
            if kind == "pause":
                pause_sec = parse_pause_tag(content)
                if pause_sec > 0:
                    yield np.zeros(int(24000 * pause_sec), dtype=np.float32)
                continue

            lang = self.get_language(active_voice)
            sentences = re.split(r"(?<=[.!?;\n])\s+", content)
            sentences = [s.strip() for s in sentences if s.strip()]
            if not sentences:
                sentences = [content]

            for s in sentences:
                ipa = self.phonemizer.phonemize(s, lang)
                tokens = self.tokens_from_ipa(ipa)
                style_vec = self.get_style_for_tokens(active_voice, len(tokens))

                if len(tokens) > 450:
                    sub_tokens = [tokens[i : i + 400] for i in range(0, len(tokens), 400)]
                    for st in sub_tokens:
                        if st[0] != 0:
                            st.insert(0, 0)
                        if st[-1] != 0:
                            st.append(0)
                        sub_style = self.get_style_for_tokens(active_voice, len(st))
                        chunk = self.synthesize_chunk(st, sub_style, speed, lang=lang)
                        if len(chunk) > 0:
                            yield chunk
                else:
                    chunk = self.synthesize_chunk(tokens, style_vec, speed, lang=lang)
                    if len(chunk) > 0:
                        yield chunk

                yield default_pause

    def synthesize(self, text: str, voice: str = "af_heart", speed: float = 1.0) -> np.ndarray:
        chunks = list(self.stream_synthesize(text, voice=voice, speed=speed))
        if not chunks:
            return np.zeros(24000, dtype=np.float32)
        return np.concatenate(chunks)


def list_available_voices() -> List[str]:
    voices = set()
    for v_dir in VOICE_SEARCH_DIRS:
        if not os.path.isdir(v_dir):
            continue
        for f in os.listdir(v_dir):
            if f.endswith((".bin", ".gguf")) and not f.startswith("."):
                name = re.sub(r"^kokoro-voice-", "", f)
                name = re.sub(r"\.(bin|gguf)$", "", name)
                voices.add(name)
    return sorted(voices)


def play_audio(pcm: np.ndarray, samplerate: int = 24000, max_seconds: float = 30.0):
    """Plays synthesized audio directly on host using python-sounddevice (PortAudio/PipeWire) with 0 subprocess exec."""
    try:
        import sounddevice as sd
    except ImportError:
        print("=" * 72, file=sys.stderr)
        print(" Error: In-process audio playback requires 'python-sounddevice'", file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        print(
            " Arch Linux package required: python-sounddevice (Arch official repo)", file=sys.stderr
        )
        print(" Install via pacman:", file=sys.stderr)
        print("   sudo pacman -S python-sounddevice", file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        return

    max_samples = int(samplerate * max_seconds)
    audio_to_play = pcm[:max_samples] if len(pcm) > max_samples else pcm
    try:
        sd.play(audio_to_play, samplerate=samplerate)
        sd.wait()
    except Exception as e:
        logger.error("Audio playback error via sounddevice: %s", e)


def encode_audio_container(pcm: np.ndarray, response_format: str) -> Tuple[bytes, str]:
    response_format = response_format.lower()
    buf = io.BytesIO()

    if response_format == "pcm":
        pcm_int16 = (np.clip(pcm, -1.0, 1.0) * 32767).astype(np.int16)
        return pcm_int16.tobytes(), "audio/pcm"
    elif response_format in ("ogg", "opus"):
        sf.write(buf, pcm, 24000, format="OGG", subtype="OPUS")
        return buf.getvalue(), "audio/ogg"
    else:
        sf.write(buf, pcm, 24000, format="WAV", subtype="PCM_16")
        return buf.getvalue(), "audio/wav"


OPENAI_VOICE_MAP = {
    "alloy": "af_alloy",
    "echo": "am_echo",
    "fable": "bm_fable",
    "onyx": "am_onyx",
    "nova": "af_nova",
    "shimmer": "af_sarah",
}


def is_german_lang(val: Optional[str]) -> bool:
    if not val:
        return False
    clean = str(val).strip().lower()
    return clean in ("de", "de-de", "de_de", "ger", "german", "deutsch") or clean.startswith("de")


def is_english_lang(val: Optional[str]) -> bool:
    if not val:
        return False
    clean = str(val).strip().lower()
    return clean in (
        "en",
        "en-us",
        "en_us",
        "en-gb",
        "en_gb",
        "eng",
        "english",
    ) or clean.startswith("en")


def resolve_voice_and_lang(
    body: dict,
    engine: KokoroPureEngine,
    default_voice_en: str = "af_heart",
    default_voice_de: str = "df_victoria",
    default_lang: str = "en",
) -> Tuple[str, str]:
    """Resolves voice and language with OpenAI-compatible fallback cascades."""
    req_voice = body.get("voice")
    req_lang = body.get("language")

    target_lang = None
    if req_lang:
        if is_german_lang(req_lang):
            target_lang = "de"
        elif is_english_lang(req_lang):
            target_lang = "en"
    elif req_voice:
        if is_german_lang(req_voice):
            target_lang = "de"
            req_voice = None
        elif is_english_lang(req_voice):
            target_lang = "en"
            req_voice = None

    if target_lang == "de":
        if req_voice and engine.has_voice(req_voice):
            return req_voice, "de"
        return default_voice_de, "de"

    if target_lang == "en":
        if req_voice:
            v_lower = str(req_voice).lower()
            if v_lower in OPENAI_VOICE_MAP:
                mapped = OPENAI_VOICE_MAP[v_lower]
                if engine.has_voice(mapped):
                    return mapped, "en-us"
            if engine.has_voice(req_voice):
                return req_voice, engine.get_language(req_voice)
        return default_voice_en, "en-us"

    if req_voice:
        v_lower = str(req_voice).lower()
        if v_lower in OPENAI_VOICE_MAP:
            mapped = OPENAI_VOICE_MAP[v_lower]
            if engine.has_voice(mapped):
                return mapped, "en-us"
            return default_voice_en, "en-us"
        if engine.has_voice(req_voice):
            return req_voice, engine.get_language(req_voice)
        return default_voice_en, "en-us"

    if is_german_lang(default_lang):
        return default_voice_de, "de"
    return default_voice_en, "en-us"


def create_app(
    engine: KokoroPureEngine,
    default_voice: str = "af_heart",
    default_voice_en: str = "af_heart",
    default_voice_de: str = "df_victoria",
    default_lang: str = "en",
) -> fastapi.FastAPI:
    app = fastapi.FastAPI(title="Kokoro Pure ONNX TTS Server", version="2.1.0")

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "engine": "kokoro-onnx-pure",
            "model_path": engine.model_path,
            "voices_count": len(list_available_voices()),
            "formats": ["wav", "pcm", "ogg", "opus"],
        }

    @app.get("/v1/models")
    def list_models():
        return {
            "object": "list",
            "data": [
                {
                    "id": "kokoro",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "kokoro",
                },
                {
                    "id": "kokoro-tts",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "kokoro",
                },
            ],
        }

    @app.get("/v1/audio/voices")
    def get_voices():
        return {"voices": list_available_voices()}

    @app.post("/v1/audio/speech")
    async def speech(request: fastapi.Request):
        try:
            body = await request.json()
        except Exception:
            raise fastapi.HTTPException(status_code=400, detail="Invalid JSON body")

        input_text = body.get("input") or body.get("text")
        if not input_text:
            raise fastapi.HTTPException(status_code=400, detail="Missing required field: 'input'")

        voice, _ = resolve_voice_and_lang(
            body,
            engine,
            default_voice_en=default_voice_en,
            default_voice_de=default_voice_de,
            default_lang=default_lang,
        )
        speed = float(body.get("speed", 1.0))
        response_format = body.get("response_format", "wav").lower()
        is_stream = bool(body.get("stream", False))

        if is_stream:

            async def audio_stream() -> AsyncGenerator[bytes, None]:
                for chunk in engine.stream_synthesize(input_text, voice=voice, speed=speed):
                    if len(chunk) == 0:
                        continue
                    if response_format in ("ogg", "opus"):
                        buf = io.BytesIO()
                        sf.write(buf, chunk, 24000, format="OGG", subtype="OPUS")
                        yield buf.getvalue()
                    else:
                        pcm_int16 = (np.clip(chunk, -1.0, 1.0) * 32767).astype(np.int16)
                        yield pcm_int16.tobytes()

            media_type = "audio/ogg" if response_format in ("ogg", "opus") else "audio/pcm"
            return StreamingResponse(audio_stream(), media_type=media_type)

        t0 = time.perf_counter()
        pcm = engine.synthesize(input_text, voice=voice, speed=speed)
        t1 = time.perf_counter()

        audio_dur = len(pcm) / 24000.0
        wall_time = t1 - t0
        rtf = wall_time / audio_dur if audio_dur > 0 else 0
        logger.info(
            "Synthesized %d chars -> %.2fs audio in %.3fs (RTF: %.3f, %.1fx real-time) [voice: %s]",
            len(input_text),
            audio_dur,
            wall_time,
            rtf,
            1.0 / rtf if rtf > 0 else 0,
            voice,
        )

        audio_data, media_type = encode_audio_container(pcm, response_format)
        return Response(content=audio_data, media_type=media_type)

    return app


def main():
    parser = argparse.ArgumentParser(
        description="Kokoro Pure ONNX TTS: Command-Line Interface and OpenAI HTTP Server"
    )
    # CLI arguments
    parser.add_argument("text", nargs="?", help="Text to synthesize (or pipe via stdin)")
    parser.add_argument(
        "-v",
        "--voice",
        "--default-voice",
        default="af_heart",
        help="Voice style (e.g. af_heart, am_adam, dm_martin, df_victoria)",
    )
    parser.add_argument(
        "-o", "--output", default="/tmp/kokoro_cli_out.wav", help="Output audio file path"
    )
    parser.add_argument(
        "-p", "--play", action="store_true", help="Play synthesized speech on speakers"
    )
    parser.add_argument("-s", "--speed", type=float, default=1.0, help="Speech speed multiplier")
    parser.add_argument(
        "-f", "--format", default="wav", choices=["wav", "opus", "pcm"], help="Output format"
    )
    parser.add_argument(
        "-t", "--threads", type=int, default=8, help="Thread count for CPU execution"
    )
    parser.add_argument(
        "-m", "--model", "--model-dir", help="Path to Kokoro ONNX model file or directory"
    )
    parser.add_argument(
        "--default-voice-en",
        default=os.environ.get("LTTS_DEFAULT_VOICE_EN", "af_heart"),
        help="Default English voice for OpenAI fallback (default: af_heart)",
    )
    parser.add_argument(
        "--default-voice-de",
        default=os.environ.get("LTTS_DEFAULT_VOICE_DE", "df_victoria"),
        help="Default German voice for OpenAI fallback (default: df_victoria)",
    )
    parser.add_argument(
        "--default-lang",
        default=os.environ.get("LTTS_DEFAULT_LANGUAGE", "en"),
        help="Default language when omitted in request (default: en)",
    )
    parser.add_argument(
        "--list-voices", action="store_true", help="List all available voices and exit"
    )
    parser.add_argument(
        "--convert-voice",
        nargs="+",
        metavar=("SRC", "DST"),
        help="Convert voice file (.gguf, .safetensors, .npz) to standard ONNX .bin format",
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check and display Arch Linux / AUR dependencies status",
    )

    # Server arguments
    parser.add_argument(
        "--server", action="store_true", help="Run as OpenAI-compatible HTTP daemon"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind to")
    parser.add_argument("--port", type=int, default=20095, help="Port to bind to")
    parser.add_argument("--log-level", default="info", help="Log level")

    args = parser.parse_args()

    if args.list_voices:
        print("=== Available Kokoro Voices ===")
        for v in list_available_voices():
            print(f"  {v}")
        return
    if args.convert_voice:
        src = args.convert_voice[0]
        dst = args.convert_voice[1] if len(args.convert_voice) > 1 else None
        try:
            out_path = convert_voice_file(src, dst)
            size = os.path.getsize(out_path)
            print("Successfully converted voice:")
            print(f"  Source:      {src}")
            print(f"  Destination: {out_path} ({size} bytes, shape (510, 256) float32)")
            sys.exit(0)
        except Exception as e:
            logger.error("Failed to convert voice: %s", e)
            sys.exit(1)

    engine = KokoroPureEngine(model_path=args.model, num_threads=args.threads)

    # Server mode check
    is_piped = not sys.stdin.isatty()
    if args.server or (not args.text and not is_piped and not args.play):
        app = create_app(
            engine,
            default_voice=args.voice,
            default_voice_en=args.default_voice_en,
            default_voice_de=args.default_voice_de,
            default_lang=args.default_lang,
        )
        logger.info("Starting Kokoro Pure ONNX Server on http://%s:%d...", args.host, args.port)
        uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)
        return

    # CLI mode
    text_content = args.text
    if not text_content and is_piped:
        text_content = sys.stdin.read().strip()

    if not text_content:
        logger.error("No input text provided.")
        parser.print_help()
        sys.exit(1)

    print("Synthesizing with Pure ONNX Engine (AVX2 MLAS):")
    print(f"  Voice:  {args.voice}")
    print(f"  Format: {args.format}")
    print(f"  Output: {args.output}")

    t0 = time.perf_counter()
    pcm = engine.synthesize(text_content, voice=args.voice, speed=args.speed)
    t1 = time.perf_counter()

    audio_bytes, _ = encode_audio_container(pcm, args.format)
    with open(args.output, "wb") as f:
        f.write(audio_bytes)

    audio_dur = len(pcm) / 24000.0
    wall_time = t1 - t0
    rtf = wall_time / audio_dur if audio_dur > 0 else 0
    print(
        f"Done: {args.output} ({len(audio_bytes)} bytes, {audio_dur:.2f}s audio in {wall_time:.3f}s, {1 / rtf:.1f}x real-time)"
    )

    if args.play:
        print("Playing audio on speakers via sounddevice (0 subprocess exec)...")
        play_audio(pcm, samplerate=24000, max_seconds=30.0)


if __name__ == "__main__":
    main()
