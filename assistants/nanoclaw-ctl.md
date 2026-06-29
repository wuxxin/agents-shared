# NanoClaw Control Guide

This guide describes configuration, onboarding, and integration features specific to the NanoClaw assistant.

For shared commands, variable expansion rules, sidecars supervision, temporary file cleanups, and unified sandboxing profiles, see the general [Agent Service Guide](agents-ctl.md).

- **Source Code**: [GitHub - gavrielc/nanoclaw](https://github.com/gavrielc/nanoclaw)
- **Arch/AUR Packages**: `nanoclaw-git` (AUR, git-based typescript source build). Alternatives: `nanoclaw`, `nanoclaw-bin`.

---

## Agent-Specific Defaults

- **Home Directory:** `~/.local/sandbox/nanoclaw`
- **Default Workspace Path:** `%h/.local/sandbox/nanoclaw/groups`
- **Configuration File:** `~/.config/systemd/user/nanoclaw.env` (environment overrides)
- **State Database:** `file:~/.local/sandbox/nanoclaw/nanoclaw.db`
- **Webhook Service Port:** [3000](http://localhost:3000/)

---

## Onboarding & Wizards

*   **Initialize Database & Channels**: Run `./assistants/nanoclaw-ctl exec tsx scripts/init-first-agent.ts` to set up first channel connections and wire routing groups.
*   **OneCLI Secret Credentials Mode**: Access OneCLI vault at `http://127.0.0.1:10254` and authorize credentials using:
    ```bash
    onecli agents set-secret-mode --id <agent-group-id> --mode all
    ```

---

## Sandboxing & Security Profile Differences

Because NanoClaw acts as an orchestrator that spawns and manages Docker/Podman containers to isolate scripts and MCP plugins, its systemd sandbox settings must be adjusted:

1.  **Container Access Sockets**:
    - **`PrivateDevices=no`**
    - **Rationale:** Requires access to host sockets (such as `/var/run/docker.sock` or `/run/user/.../podman/podman.sock`) to coordinate container creation.
2.  **Namespace Support & Container Runtimes (Docker/Podman)***:
    - **Properties Omitted:** `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
    - **Rationale:** Standard systemd namespace isolation or proc limits would prevent the Node process from spinning up nested cgroup or network namespaces.
    - **Rationale**: NanoClaw orchestrates local container runtimes (such as Docker or Podman) to launch helper agents and execute sandboxed scripts. Standard systemd namespace isolation or proc limits would prevent the runtime from communicating with container daemons or creating nested namespaces.
3. **Writable & Executable Memory (Node.js/V8 JIT)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: NanoClaw is written in TypeScript/JavaScript and runs under Node.js, which depends on V8 JIT code generation. Rejecting W^X memory regions would prevent Node.js from running correctly.


---

## Switch to Local Inference & Qwen3

To route LLM queries, vectors, and embeddings, update `~/.config/systemd/user/nanoclaw.env`:

```env
# Default OpenAI-compatible LLM provider
LLM_PROVIDER="openai"
LLM_BASE_URL="http://localhost:50080/v1"
LLM_API_KEY="unused"
LLM_MODEL="qwen3"

# Embeddings endpoint (llama-server on port 50082)
EMBEDDING_PROVIDER="local"
EMBEDDING_MODEL="qwen3-embedding"
EMBEDDING_BASE_URL="http://localhost:50082/v1"
EMBEDDING_API_KEY="unused"

# Reranker endpoint (llama-server on port 50086)
RERANK_URL="http://localhost:50086/v1/rerank"
RERANK_MODEL="qwen3-reranker"
```
