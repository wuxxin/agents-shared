# kpxc-secret

Fast, secure secret retrieval helper communicating directly with KeePassXC using `git-credential-keepassxc` over the KeePassXC browser/proxy protocol (Native Messaging UNIX domain socket).

## Features

- **No DBus Secret Service Dependency:** Bypasses `org.freedesktop.secrets` entirely, preventing conflicts with GNOME Keyring.
- **Strict Caller Support:** Automatically whitelists caller binaries (including `bash`, `python3`, `git`, and sandbox harnesses) to prevent `git-credential-keepassxc` strict-caller aborts.
- **URI Resolution Schemes:**
  - `kpxc://[<group>/]<target>[:<field>]`
    - Resolves from KeePassXC entries (matching URL, host, or title).
    - Supported fields: `password` (default), `username`, `totp`, `notes`, or any custom attribute name (including `KPH: <name>`).
  - `env://<VAR_NAME>`
    - Reads from an existing environment variable.
  - `cmd://<shell_command>`
    - Executes arbitrary command in a subshell and captures stdout.
- **In-Memory Secret Injection:** Inject secrets directly into child processes (`run`) or shell environments (`export`) without writing credentials to disk.

## Setup & Pairing

1. In KeePassXC, ensure browser integration is enabled:
   - **Tools** → **Settings** → **Browser Integration** → check **Enable browser integration**.
   - Under **Advanced**, ensure **Return advanced string fields which start with "KPH: "** is enabled.
2. Pair `kpxc-secret` with your database:
   ```bash
   ./scripts/kpxc-secret configure --group Automation
   ```
   KeePassXC will display a connection dialog. Enter an identifier (e.g. `kpxc-automation`) and click **Save and allow access**.

## Usage Examples

### 1. Print Secret to stdout
```bash
# Retrieve password for an entry
./scripts/kpxc-secret get "kpxc://api.openai.com"

# Retrieve TOTP code
./scripts/kpxc-secret get "kpxc://github.com:totp"

# Retrieve specific custom attribute from dedicated group
./scripts/kpxc-secret get "kpxc://Automation/anthropic:KPH:api_key"
```

### 2. Export into Current Shell
```bash
eval "$(./scripts/kpxc-secret export OPENAI_API_KEY="kpxc://api.openai.com" GITHUB_TOKEN="kpxc://github.com")"
```

### 3. Wrap Command Execution (In-Memory Environment)
```bash
./scripts/kpxc-secret run --secret OPENAI_API_KEY="kpxc://api.openai.com" -- python3 agent.py
```

### 4. Check Connection & Configuration Status
```bash
./scripts/kpxc-secret status
```
