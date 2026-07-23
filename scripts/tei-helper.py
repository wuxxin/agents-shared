import builtins
import sys

print("Loading TEI PPLX Qwen3 Config & trust_remote_code monkeypatch...", file=sys.stderr, flush=True)

# 1. Bypassing Hugging Face dynamic class comparison bug for Perplexity Config
old_isinstance = builtins.isinstance

def check_name(x):
    try:
        # Use object.__getattribute__ to bypass any custom metaclass __getattribute__
        # (e.g. torchao's metaclass) and avoid recursion loops.
        name = object.__getattribute__(x, "__name__")
        if name == "PPLXQwen3Config":
            return True
    except Exception:
        pass
    return False

def new_isinstance(obj, class_or_tuple):
    is_pplx = False
    # Use type(x) is tuple to avoid calling issubclass/isinstance on class_or_tuple,
    # which would trigger metaclass attribute lookup and cause infinite recursion.
    if type(class_or_tuple) is tuple:
        for c in class_or_tuple:
            if check_name(c):
                is_pplx = True
                break
    else:
        if check_name(class_or_tuple):
            is_pplx = True

    if is_pplx:
        if type(obj).__name__ == "PPLXQwen3Config":
            return True

    return old_isinstance(obj, class_or_tuple)

builtins.isinstance = new_isinstance

# 2. Force trust_remote_code=True on Auto classes to prevent interactive terminal prompts
try:
    from transformers import AutoConfig, AutoModel, AutoTokenizer

    old_config_from_pretrained = AutoConfig.from_pretrained
    def new_config_from_pretrained(*args, **kwargs):
        kwargs["trust_remote_code"] = True
        return old_config_from_pretrained(*args, **kwargs)
    AutoConfig.from_pretrained = new_config_from_pretrained

    old_model_from_pretrained = AutoModel.from_pretrained
    def new_model_from_pretrained(*args, **kwargs):
        kwargs["trust_remote_code"] = True
        return old_model_from_pretrained(*args, **kwargs)
    AutoModel.from_pretrained = new_model_from_pretrained

    old_tokenizer_from_pretrained = AutoTokenizer.from_pretrained
    def new_tokenizer_from_pretrained(*args, **kwargs):
        kwargs["trust_remote_code"] = True
        return old_tokenizer_from_pretrained(*args, **kwargs)
    AutoTokenizer.from_pretrained = new_tokenizer_from_pretrained

except Exception as e:
    print(f"Warning: could not monkeypatch transformers from_pretrained: {e}", file=sys.stderr)
