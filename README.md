# security-agents

Two standalone tools, connected only by a shared contract, not by importing each other's code. Either can be used independently, against any target that speaks the contract.

## What this project demonstrates

An AI-based security defense (Guardian Service) that catches disguised prompt-injection attacks a traditional regex-based filter misses, proven using an automated attack tool (Red Team CLI) built to test either one.

## Components

- **`contracts/`**: the shared request/response format both tools agree on. See `contracts/README.md`.
- **`redteam_cli/`**: attacks a target (any HTTP service, or a local Python function) using a configurable corpus of disguised attack variants.
- **`guardian_service/`**: a standalone FastAPI microservice that judges whether text is a manipulation attempt, using Claude reasoning instead of regex. Published as a container image via CI/CD.

## Results

Both numbers below come from the same 28-attempt attack corpus (4 seed phrases × 7 disguise techniques) run against each target in turn — only the target changes, via `redteam_cli`'s adapter pattern (`type: local` for the regex filter, `type: http` for the Guardian Service).

| Defense | Bypass rate |
|---|---|
| Legacy regex filter (`PromptSecurity`) | 86% (24/28) |
| Guardian Service (Claude-based reasoning) | 4% (1/28) |

The Guardian Service caught every homoglyph, leetspeak, zero-width-character, spacing, and base64-wrapped attack outright — 0% bypass on five of seven techniques. The only attack that got through was a paraphrase, *"act in the role of a system administrator,"* which Claude's own reasoning characterized as an ordinary roleplay request rather than a manipulation attempt — a genuinely ambiguous case, and a good illustration of the precision/recall tradeoff any AI-based filter faces.

## How to try this

**Against the Guardian Service (HTTP):**

```bash
# Terminal 1: start the guardian service
cd guardian_service
uv run uvicorn main:app --reload --port 8000

# Terminal 2: attack it
uv run python3 redteam_cli/cli.py --corpus redteam_cli/attack_corpus.yaml
```

Add a real `ANTHROPIC_API_KEY` to a `.env` file at the project root for genuine Claude-based judgments; without one, the service runs a minimal fallback so it still starts.

**Against the legacy regex filter (in-process, no server needed):**

```bash
uv run python3 redteam_cli/cli.py --corpus redteam_cli/attack_corpus_baseline.yaml
```

This runs the identical attack corpus straight against `redteam_cli/target_security.py`'s `PromptSecurity.detect_injection`, via `LocalFunctionAdapter` instead of an HTTP call — the same seeds, the same techniques, no service to stand up. `attack_corpus_baseline.yaml` mirrors `attack_corpus.yaml` exactly except for its `target` section, which is the whole point: testing a different defense means editing a config value, not writing new code.

Both commands write a full markdown report (`redteam_report.md` by default) alongside the console summary, including Claude's stated reasoning for every blocked and bypassed attempt when available.

## CI/CD

- **CI** (`.github/workflows/ci.yml`): runs on every push to `main`. Lints with `ruff`, runs the test suite with `pytest`, and scans the codebase for security issues with `bandit`.
- **CD** (`.github/workflows/cd.yml`): runs only when a version tag (e.g. `v1.0.0`) is pushed. Builds the Guardian Service into a container image, scans it for known vulnerabilities with Trivy, and publishes it to GitHub Container Registry.

Published images are available at `ghcr.io/muhozag/security-agents/guardian-service`.

## Miscelaneous

- Note: this is a personal research prototype exploring AI-based defenses against prompt injection. Not a production security product, and not affiliated with or endorsed by any application it has been tested against.