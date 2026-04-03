# Codex Skill Setup

The repository includes a local copy of the OWCS screenshot parsing skill here:

- `codex-skills/owcs-stats-screenshot-parser/`

To install it into Codex on another PC, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\OWCStats\install_owcs_skill.ps1
```

This copies the skill into:

- `%CODEX_HOME%\skills\owcs-stats-screenshot-parser`
- or `~/.codex/skills/owcs-stats-screenshot-parser` if `CODEX_HOME` is not set

After that, reopen Codex if needed so the skill is available in the new environment.
