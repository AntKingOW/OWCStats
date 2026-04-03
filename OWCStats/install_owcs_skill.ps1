$repoSkillRoot = Join-Path $PSScriptRoot "codex-skills\owcs-stats-screenshot-parser"
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$targetRoot = Join-Path $codexHome "skills\owcs-stats-screenshot-parser"

New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
Copy-Item -Path (Join-Path $repoSkillRoot "*") -Destination $targetRoot -Recurse -Force

Write-Host "Installed OWCS skill to: $targetRoot"
