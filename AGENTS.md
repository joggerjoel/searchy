# searchy

A small Python 3 CLI that queries the Serper API across ticketing/event sites and only prints result URLs whose title/snippet date matches the event date parsed from an input file. The entrypoint is `searchy.py`, driven by `searchy.sh`.

## Cursor Cloud specific instructions

- Setup, run, and input-file conventions are documented in `README.md`. Dependencies are managed by `setup.sh` (creates `.venv` and installs `requirements.txt`); the startup update script already runs this.
- `python3-venv` (system package `python3.12-venv`) must be present for `setup.sh` to build the venv. It is installed in the VM image; only reinstall via `apt` if venv creation ever fails with an `ensurepip` error.
- Always run the app through the venv: `./searchy.sh [file.txt] [--open]` (auto-uses `.venv`), or `.venv/bin/python searchy.py [file.txt]`. Do not rely on the system `python3`, which lacks `python-dotenv`.
- Running the search requires `SERPER_API_KEY` (set in env or `.env`, copied from `.env.example`). Without it the app exits early with `Error: SERPER_API_KEY not set`; the date-parsing/URL-normalization logic still runs and can be exercised directly by importing `searchy` without a key.
- There is no test suite, lint config, or build step. "Build" is just the venv install; "run" is the CLI above.
- The `--open` flag and `scripts/open-chrome.sh` only support macOS/Windows; on Linux (Cloud VM) URL opening is a no-op, so test without `--open`.
