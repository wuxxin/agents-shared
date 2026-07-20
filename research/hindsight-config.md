Your revised configuration iswell-tuned for a local-inference model engine with a **240k Unified KV Cache** serving **3 parallel sessions**. 

By capping the concurrency at `1` for the global, reflect, and consolidation scopes, you guarantee that background memory management (which can be computationally heavy) will queue up in single file. This prevents the LLM from trying to spin up parallel slots that would trigger prompt-swapping, VRAM exhaustion, or lag in your active chat sessions.

Below is a complete catalog of your configured knobs, alongside a few hidden/advanced knobs you might want to consider adding to your setup to keep local storage clean and prevent memory bloat.

### Knob Catalog (Markdown Reference Table)

| Knob Name | Default Value | Actual Value | Description | Rationale for Your Setup |
| :--- | :---: | :---: | :--- | :--- |
| **`HINDSIGHT_API_LLM_TIMEOUT`** | `120` | `180` | Individual client HTTP request timeout in seconds. | Gives your local hardware up to 3 minutes to handle initial pre-fill and decode before aborting. |
| **`HINDSIGHT_API_LLM_MAX_CONCURRENT`** | `32` | `1` | Global cap on simultaneous LLM requests sent by Hindsight. | **Critical for Local:** Restricts Hindsight to 1 active pipeline, reserving remaining slots for active user chat sessions. |
| **`HINDSIGHT_API_LLM_REASONING_EFFORT`** | `medium` | `low` | Reasoning parameter passed to supporting reasoning models. | Minimizes unnecessary "thinking" token overhead to speed up background ingestion/synthesis. |
| **`HINDSIGHT_API_RECALL_INCLUDE_CHUNKS`** | `true` | `false` | Decides whether raw text chunks are pulled alongside facts. | **Token Saver:** Dropping raw chunks slices the memory-model input payload size in half. |
| **`HINDSIGHT_API_RECALL_MAX_TOKENS`** | `2048` | `1536` | Token budget allocated to facts gathered by internal recall. | Keeps the memory database context light enough to prevent prompt processing bottlenecks. |
| **`HINDSIGHT_API_RECALL_CHUNKS_MAX_TOKENS`** | `1000` | `500` | Token budget for chunks if `include_chunks` is true. | Effectively a dormant backup budget since you have disabled chunks globally. |
| **`HINDSIGHT_API_REFLECT_WALL_TIMEOUT`** | `300` | `600` | Timeout in seconds for the entire background reflection job. | Prevents Hindsight from giving up on a long-running mental model synthesis task. |
| **`HINDSIGHT_API_REFLECT_MAX_CONTEXT_TOKENS`** | `100000` | `65536` | Strict cap on total tokens fed to a single reflection. | **Protects VRAM:** Prevents the system from executing 120k–150k token bursts, keeping memory footprints predictable. |
| **`HINDSIGHT_API_REFLECT_LLM_MAX_CONCURRENT`** | `32` | `1` | Cap on concurrent LLM tasks specifically for the reflect phase. | Enforces strict serial processing during reflection to maintain local server responsiveness. |
| **`HINDSIGHT_API_REFLECT_LLM_TIMEOUT`** | `HINDSIGHT_API_LLM_TIMEOUT` | `300` | HTTP request timeout specifically for reflect LLM queries. | Allows slower generation passes up to 5 minutes to complete complex, deeply detailed synthesis. |
| **`HINDSIGHT_API_RETAIN_LLM_MAX_CONCURRENT`** | `32` | `1` | Concurrent LLM threads allowed for incoming interaction ingestion. | Ensures background data retention runs silently without interrupting foreground tasks. |
| **`HINDSIGHT_API_CONSOLIDATION_RECALL_BUDGET`** | `medium` | `low` | Token retrieval density used during memory consolidation. | Lowers CPU/GPU memory footprint during consolidation by querying only the highest-scoring records. |
| **`HINDSIGHT_API_CONSOLIDATION_SOURCE_FACTS_MAX_TOKENS`** | `4096` | `4096` | Maximum total tokens retrieved when grouping older memories. | Stays at default to allow Hindsight to evaluate a reasonably rich set of facts when merging. |
| **`HINDSIGHT_API_CONSOLIDATION_SOURCE_FACTS_MAX_TOKENS_PER_OBSERVATION`** | `256` | `256` | Target size limit for individual facts when summarizing. | Preserves clear, concise boundaries for facts inside your memory graphs. |
| **`HINDSIGHT_API_CONSOLIDATION_LLM_MAX_CONCURRENT`** | `32` | `1` | Concurrency cap for background consolidation routines. | Restricts the automatic memory-merging system from running multiple background processes concurrently. |
| **`HINDSIGHT_API_CONSOLIDATION_LLM_BATCH_SIZE`** | `8` | `2` | Number of LLM operations dispatched at once in consolidation. | Shallows the pipeline depth to prevent massive concurrent VRAM pre-fill spikes. |
| **`HINDSIGHT_API_CONSOLIDATION_MAX_MEMORIES_PER_ROUND`** | `50` | `20` | Max memories evaluated in a single consolidation round. | Prevents background tasks from processing massive document dumps in one heavy sweep. |

---

### Additional Knobs to Consider for Your Setup

If you want to tighten your local instance even further, there are a few additional, less-publicized knobs in the engine code that can prevent host machine storage inflation and RAM leaks:

#### 1. Disk & Memory Hygiene
* **`HINDSIGHT_API_FILE_DELETE_AFTER_RETAIN=true`** (Default: `false`)
  * *Rationale:* Once a file (like a PDF or TXT) has been ingested, parsed, and its memories extracted, Hindsight normally keeps the source file. Setting this to `true` cleans up the source binaries immediately, preventing your local database or directory from swelling with raw document duplicates.

#### 2. Local-Access Security
* **`HINDSIGHT_API_AUTH_ENABLED=true`** (Default: `false`)
  * *Rationale:* If your local deployment is accessible on your LAN or running as a multi-user service, you can enforce basic API-key validation.
* **`HINDSIGHT_API_MCP_AUTH_TOKEN="your_secure_token"`** (Default: `""`)
  * *Rationale:* If you use Hindsight's MCP (Model Context Protocol) capability locally, this sets an authentication token to secure the MCP socket from unauthorized client tools.Your revised configuration iswell-tuned for a local-inference model engine with a **240k Unified KV Cache** serving **3 parallel sessions**. 

By capping the concurrency at `1` for the global, reflect, and consolidation scopes, you guarantee that background memory management (which can be computationally heavy) will queue up in single file. This prevents the LLM from trying to spin up parallel slots that would trigger prompt-swapping, VRAM exhaustion, or lag in your active chat sessions.

Below is a complete catalog of your configured knobs, alongside a few hidden/advanced knobs you might want to consider adding to your setup to keep local storage clean and prevent memory bloat.

### Knob Catalog (Markdown Reference Table)

| Knob Name | Default Value | Actual Value | Description | Rationale for Your Setup |
| :--- | :---: | :---: | :--- | :--- |
| **`HINDSIGHT_API_LLM_TIMEOUT`** | `120` | `180` | Individual client HTTP request timeout in seconds. | Gives your local hardware up to 3 minutes to handle initial pre-fill and decode before aborting. |
| **`HINDSIGHT_API_LLM_MAX_CONCURRENT`** | `32` | `1` | Global cap on simultaneous LLM requests sent by Hindsight. | **Critical for Local:** Restricts Hindsight to 1 active pipeline, reserving remaining slots for active user chat sessions. |
| **`HINDSIGHT_API_LLM_REASONING_EFFORT`** | `medium` | `low` | Reasoning parameter passed to supporting reasoning models. | Minimizes unnecessary "thinking" token overhead to speed up background ingestion/synthesis. |
| **`HINDSIGHT_API_RECALL_INCLUDE_CHUNKS`** | `true` | `false` | Decides whether raw text chunks are pulled alongside facts. | **Token Saver:** Dropping raw chunks slices the memory-model input payload size in half. |
| **`HINDSIGHT_API_RECALL_MAX_TOKENS`** | `2048` | `1536` | Token budget allocated to facts gathered by internal recall. | Keeps the memory database context light enough to prevent prompt processing bottlenecks. |
| **`HINDSIGHT_API_RECALL_CHUNKS_MAX_TOKENS`** | `1000` | `500` | Token budget for chunks if `include_chunks` is true. | Effectively a dormant backup budget since you have disabled chunks globally. |
| **`HINDSIGHT_API_REFLECT_WALL_TIMEOUT`** | `300` | `600` | Timeout in seconds for the entire background reflection job. | Prevents Hindsight from giving up on a long-running mental model synthesis task. |
| **`HINDSIGHT_API_REFLECT_MAX_CONTEXT_TOKENS`** | `100000` | `65536` | Strict cap on total tokens fed to a single reflection. | **Protects VRAM:** Prevents the system from executing 120k–150k token bursts, keeping memory footprints predictable. |
| **`HINDSIGHT_API_REFLECT_LLM_MAX_CONCURRENT`** | `32` | `1` | Cap on concurrent LLM tasks specifically for the reflect phase. | Enforces strict serial processing during reflection to maintain local server responsiveness. |
| **`HINDSIGHT_API_REFLECT_LLM_TIMEOUT`** | `HINDSIGHT_API_LLM_TIMEOUT` | `300` | HTTP request timeout specifically for reflect LLM queries. | Allows slower generation passes up to 5 minutes to complete complex, deeply detailed synthesis. |
| **`HINDSIGHT_API_RETAIN_LLM_MAX_CONCURRENT`** | `32` | `1` | Concurrent LLM threads allowed for incoming interaction ingestion. | Ensures background data retention runs silently without interrupting foreground tasks. |
| **`HINDSIGHT_API_CONSOLIDATION_RECALL_BUDGET`** | `medium` | `low` | Token retrieval density used during memory consolidation. | Lowers CPU/GPU memory footprint during consolidation by querying only the highest-scoring records. |
| **`HINDSIGHT_API_CONSOLIDATION_SOURCE_FACTS_MAX_TOKENS`** | `4096` | `4096` | Maximum total tokens retrieved when grouping older memories. | Stays at default to allow Hindsight to evaluate a reasonably rich set of facts when merging. |
| **`HINDSIGHT_API_CONSOLIDATION_SOURCE_FACTS_MAX_TOKENS_PER_OBSERVATION`** | `256` | `256` | Target size limit for individual facts when summarizing. | Preserves clear, concise boundaries for facts inside your memory graphs. |
| **`HINDSIGHT_API_CONSOLIDATION_LLM_MAX_CONCURRENT`** | `32` | `1` | Concurrency cap for background consolidation routines. | Restricts the automatic memory-merging system from running multiple background processes concurrently. |
| **`HINDSIGHT_API_CONSOLIDATION_LLM_BATCH_SIZE`** | `8` | `2` | Number of LLM operations dispatched at once in consolidation. | Shallows the pipeline depth to prevent massive concurrent VRAM pre-fill spikes. |
| **`HINDSIGHT_API_CONSOLIDATION_MAX_MEMORIES_PER_ROUND`** | `50` | `20` | Max memories evaluated in a single consolidation round. | Prevents background tasks from processing massive document dumps in one heavy sweep. |

---

### Additional Knobs to Consider for Your Setup

If you want to tighten your local instance even further, there are a few additional, less-publicized knobs in the engine code that can prevent host machine storage inflation and RAM leaks:

#### 1. Disk & Memory Hygiene
* **`HINDSIGHT_API_FILE_DELETE_AFTER_RETAIN=true`** (Default: `false`)
  * *Rationale:* Once a file (like a PDF or TXT) has been ingested, parsed, and its memories extracted, Hindsight normally keeps the source file. Setting this to `true` cleans up the source binaries immediately, preventing your local database or directory from swelling with raw document duplicates.

#### 2. Local-Access Security
* **`HINDSIGHT_API_AUTH_ENABLED=true`** (Default: `false`)
  * *Rationale:* If your local deployment is accessible on your LAN or running as a multi-user service, you can enforce basic API-key validation.
* **`HINDSIGHT_API_MCP_AUTH_TOKEN="your_secure_token"`** (Default: `""`)
  * *Rationale:* If you use Hindsight's MCP (Model Context Protocol) capability locally, this sets an authentication token to secure the MCP socket from unauthorized client tools.