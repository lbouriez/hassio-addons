# Changelog

All notable changes to this project will be documented in this file.

## [0.5.1] - 2026-10-28

### Fixed
- Restore phone swipe scrolling through terminal scrollback even when an application enables mouse reporting; gestures do not send input to the running command.
- Use the phone viewport width instead of a desktop-sized layout.
- Let the History dialog scroll naturally on touch devices without preselecting its entire contents.
- Add real browser touch-gesture regression checks in direct and HA-style iframe views.

## [0.5.0] - 2026-10-26

### Added
- Browser terminal toolbar with Copy, Paste, History, download and Latest controls, including French labels.
- Native clipboard shortcuts and a visible text fallback when HTTP or iframe permissions block clipboard access.
- Optional `terminal_scrollback` (10000 lines), `preserve_terminal_history` (true), and `reasoning_effort` (default) settings. Existing saved options remain valid.
- `ha-api check`, `ha-api reload <domain>` and `ha-api restart`; reload/restart shortcuts require a successful fresh configuration check.
- Browser regression checks for clipboard, history, ingress paths and small screens.

### Fixed
- Stop tmux capturing normal mouse selection; retain keyboard copy mode and session persistence.
- Pass terminal themes as JSON so ttyd applies foreground/background correctly.

## [0.4.3] - 2026-10-26

### Fixed
- Make `yolo_mode` optional in the HA schema and omit its options default so saved configurations from before 0.4.2 remain valid. An absent value still means YOLO is off at runtime; explicit true/false values are preserved.
- Validate optional schema fields independently of defaults and exercise startup with saved options that omit `yolo_mode`.

## [0.4.2] - 2026-10-26

### Added
- Optional `yolo_mode` setting, disabled by default, to launch Codex with sandbox and approvals bypassed. It overrides the two individual access options while enabled and restores their saved values when disabled after restart.
- Terminal lifecycle regression checks for YOLO on/off and tmux disconnect/reattach behavior.
- Run terminal lifecycle checks under the shipped AppArmor profile in CI.

### Clarified
- `session_persistence` keeps the terminal and work alive through browser disconnects, but not App/VM restarts. Login and recorded history persist independently.

### Fixed
- Permit the root terminal supervisor to signal its unprivileged client processes on disconnect under AppArmor.

## [0.4.1] - 2026-10-26

### Fixed
- Allow AppArmor execution and executable mapping of Codex-managed daemon package programs, including temporary `.staging.*` releases used during installation. Keep the daemon enabled and retain the AppArmor profile.
- Install `procps`: Codex's daemon process tracking needs `ps -p PID -o stat= -o lstart=`, which Alpine's BusyBox `ps` does not support.
- Allow listing `/proc/` for process tracking and `/tmp/` for runtime discovery; descendant-file rules alone did not permit these directory reads.

### Added
- Real daemon install/start/version/stop/restart smoke tests as the unprivileged runtime user, with networking disabled and no account credentials. CI also runs them under the shipped AppArmor profile.
- Capture daemon and AppArmor denial diagnostics when a confined startup fails.

## [0.4.0] - 2026-10-26

### Changed
- Connect only to Home Assistant's official Model Context Protocol Server through the internal Supervisor proxy, using the add-on credential automatically. No manual URL, token, OAuth setup or third-party MCP fallback.
- Remove the bundled `hass-mcp` dependency and its privileged wrapper. Migrate managed Codex MCP configuration to the official bridge, preserving unrelated servers.
- Provide actionable connectivity status at startup and through `ha-api status`; keep the terminal available when HA is starting or the official integration is unavailable.

### Added
- Authenticated `ha-api` commands for Core REST, Supervisor management/logs/configuration checks, and WebSocket queries or event subscriptions.
- Fixed-destination credential helpers that keep the Supervisor token out of Codex configuration and the interactive shell; reject redirects and external API URLs.
- AppArmor permissions for the Python clients' native extension libraries.
- Codex instructions covering actual API commands, configuration validation and safe handling of UI-managed settings.
- End-to-end container tests against a local HA protocol fixture for official MCP tools/resources/prompts, REST, WebSocket, Supervisor operations, unprivileged file access and token isolation.

## [0.3.0] - 2026-10-26

### Changed
- Publish the fork and its AMD64/ARM64 images under `lbouriez/ha.addon.codex`, with fork-specific install links, metadata, ownership, and support links; preserve upstream license and attribution.
- Pin the image to Codex CLI 0.164.0 and use Codex's recommended account model instead of the retired gpt-5.4 default. Migrate the inherited App option while preserving manually configured models.
- Validate pull requests, build and smoke-test both native architectures, then publish signed versioned images and a multi-architecture manifest on main. Read base images from build.yaml and preserve existing release tags.

### Fixed
- Honor explicit `enable_mcp: false` and reduce terminal connection noise (adapted from upstream PR #6).
- Persist optional startup CLI updates as the unprivileged user and permit execution under AppArmor (adapted from upstream PR #7).
- Permit executable mapping of the bundled npm CLI under its actual `/usr/local/lib/node_modules` prefix.
- Select the image CLI when a persisted installation is older or broken, including failed installs and execution errors.
- Enforce Linux line endings for extensionless runtime scripts checked out on Windows.

### Added
- Configuration, model-preservation, and CLI-selection regression tests plus container startup smoke tests.
- Dependabot updates for Actions and base images, release instructions, and a recorded review of upstream PRs.

## [0.2.15] - 2026-05-31

### Fixed
- Stopped exposing `/root/.npm` as the runtime npm cache so Codex CLI updates no longer fail with `EACCES` after the terminal drops to the unprivileged `codex` user
- Gave interactive Codex sessions a persistent user-owned npm cache and global prefix under the persistent Codex user home so `npm install -g @openai/codex@latest` works from the terminal and stays on `PATH`
- Isolated optional startup-time root CLI updates to a temporary root-owned npm cache instead of reusing the interactive session cache

## [0.2.14] - 2026-05-24

### Added
- Installed `bubblewrap` so Codex workspace sandbox mode has the Linux sandbox runtime it expects

### Fixed
- Added a default `BUILD_FROM` value to silence Docker's invalid default build-arg warning while preserving Home Assistant's per-architecture build argument override

## [0.2.13] - 2026-05-24

### Fixed
- Repair saved Codex UI state when `tui.model_availability_nux` is stored as a table/map instead of the integer expected by current Codex CLI versions
- Back up semantically repaired config files as `config.toml.repaired.bak`

## [0.2.12] - 2026-05-24

### Fixed
- Quote TOML table keys for project paths such as `/homeassistant` so generated `config.toml` remains valid after Codex records trusted projects
- Repair legacy invalid `[projects./homeassistant]` config sections by backing up the bad file and rewriting them as `[projects."/homeassistant"]`
- Re-run Codex config merge and repair before every Codex launch from the terminal shell, including retries after Codex exits

## [0.2.11] - 2026-05-24

### Added
- Added a `codex_approval_policy` App option with `on-request`, `untrusted`, and `never` choices
- Documented autonomous mode using `codex_permissions: full_access` together with `codex_approval_policy: never`

### Changed
- Generate Codex `approval_policy` from the App option so users can disable per-action approval prompts when they explicitly choose autonomous mode

## [0.2.10] - 2026-05-24

### Added
- Added a GitHub Actions workflow to publish prebuilt `amd64` and `aarch64` Codex App images to GitHub Container Registry
- Added the `image` field so Home Assistant pulls `ghcr.io/kecksdigital/codex-hass:<version>` instead of building locally

### Fixed
- Passed the per-architecture Home Assistant base image into the GHCR build workflow so Docker builds do not rely on local Supervisor build arguments

### Changed
- Documented the difference between Home Assistant App updates and optional Codex CLI startup updates

## [0.2.9] - 2026-05-24

### Changed
- Rewrote Codex documentation as a standalone Home Assistant App guide with first-run authentication, model, access, MCP, persistence, and update guidance
- Changed new installs to start with `session_persistence` disabled for a cleaner first sign-in flow
- Reduced tmux history, ttyd client count, and ttyd scrollback for safer startup on smaller Home Assistant systems
- Increased healthcheck startup grace and capped Node heap usage to improve reliability during heavier Codex CLI starts

### Added
- Added optional bounded Codex CLI startup updates with `auto_update_codex` and `codex_update_timeout`
- Added startup validation for the generated Codex config when the installed CLI exposes `codex debug prompt-input`
- Added SHA256 verification for downloaded `ttyd` binaries

### Fixed
- Sanitized terminal font size and update timeout values before using them in startup commands
- Prevented optional Codex CLI runtime updates from inheriting the Home Assistant Supervisor token
- Removed unnecessary `net_admin` from the AppArmor profile

## [0.2.8] - 2026-05-24

### Changed
- Set the starter `default_model` add-on option to `gpt-5.4` instead of leaving Codex to choose its current default
- Added a `codex_permissions` add-on option with `workspace` and `full_access` choices
- Generate Codex `sandbox_mode` from the add-on option, mapping `full_access` to `danger-full-access`
- Documented how to change the model and access level from Home Assistant options

## [0.2.7] - 2026-05-24

### Fixed
- Pre-created the unprivileged Codex runtime user at image build time instead of trying to run `adduser` inside Home Assistant AppArmor at terminal connection time
- Kept the terminal open with an unprivileged diagnostic shell if session startup fails, instead of letting ttyd fall back to its restart prompt
- Made direct-ttyd mode explicitly use the shared `anonymous` Codex home instead of partially emulating per-user runtime accounts
- Moved the tmux socket into the managed Codex state directory and made generated Codex config writable by the runtime user
- Serialized startup config generation and atomically replaced `config.toml` to avoid races when multiple terminals connect
- Added base terminfo data for tmux compatibility with `xterm-256color`

## [0.2.6] - 2026-05-24

### Fixed
- Restored direct ttyd ingress serving on port 7681 so the WebSocket console works behind Home Assistant ingress
- Removed the nginx proxy and ttyd auth-header mode that caused `/ws` 502 responses and ttyd restart prompts
- Updated the healthcheck to probe ttyd directly after removing nginx from the runtime path
- Updated documentation to describe the current shared direct-ttyd ingress identity accurately

### Changed
- Start Codex automatically when the Web UI opens so unauthenticated users are taken directly into the Codex sign-in flow
- Retry Codex by default when startup exits before completion, with an explicit diagnostic shell escape

## [0.2.5] - 2026-05-24

### Fixed
- Fixed the per-user tmux launcher so ttyd opens an interactive shell instead of falling back to its restart prompt
- Added visible session startup errors in the browser terminal when the shell wrapper fails before bash starts

## [0.2.4] - 2026-05-24

### Changed
- Reduced nginx health-check log noise so Web UI proxy errors are easier to see in add-on logs

## [0.2.3] - 2026-05-24

### Fixed
- Switched the nginx upstream from a Unix socket to `127.0.0.1:7682` so ttyd no longer depends on socket permission compatibility
- Expanded the ingress allowlist from a single hard-coded Supervisor IP to private network ranges used by Home Assistant installations

## [0.2.2] - 2026-05-24

### Fixed
- Allowed AppArmor execution of `/usr/sbin/nginx` so the hardened ingress proxy can start correctly
- Moved Codex startup validation out of `/tmp` to avoid Codex helper-binary warnings during MCP config checks

## [0.2.1] - 2026-05-24

### Changed
- Rewrote the Codex documentation to explain installation, per-user sessions, MCP wiring, persistence, and everyday usage more clearly
- Replaced upstream repository links and metadata with the `kecksdigital/codex-hass` repository
- Updated the add-on branding, description, and panel icon so the Codex add-on no longer ships with Claude-oriented presentation

## [0.2.0] - 2026-05-23

### Added
- Per-user Codex homes under `/data/codex-home/users/<ha-user-id>/.codex`
- Dedicated Unix users for each Home Assistant ingress user before the shell starts
- Per-user tmux session isolation keyed by the Home Assistant ingress user id
- Reverse-proxied ingress terminal with nginx in front of ttyd and ttyd bound to a local Unix socket
- `hass-mcp-wrapper` and a privileged root helper so the Supervisor token stays out of the interactive shell
- Non-destructive merging of add-on-managed Codex defaults into each user's `~/.codex/config.toml`
- One-time backup of legacy shared Codex state from `/homeassistant/.codex-home` without auto-assigning it to a user

### Changed
- Moved persistent Codex state out of `/homeassistant` and into `/data/codex-home`
- Removed the shared global ttyd/tmux session model in favor of per-user sessions
- Added startup validation for the generated per-user Codex MCP configuration
- Removed inherited `docker_api` and `full_access` privileges from the Codex add-on

## [0.1.0] - 2026-05-23

### Added
- Initial Codex add-on release alongside the existing Claude Code add-on
- OpenAI Codex CLI installed during image build with `codex --version` validation
- Home Assistant ingress terminal powered by ttyd on port 7681
- Persistent Codex home directory at `/homeassistant/.codex-home`
- Generated `~/.codex/AGENTS.md` with Home Assistant path mapping, log guidance, and MCP notes
- Generated `~/.codex/config.toml` with optional default model selection and Home Assistant MCP wiring
- Session persistence via tmux with the `codex` session name
- Initial architecture support for amd64 and aarch64

### Changed
- Removed Playwright MCP and Claude-specific runtime behavior from the new Codex add-on
- Removed inherited Modbus/serial tooling and UART access from the Codex v1 scope
