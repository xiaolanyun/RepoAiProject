[CmdletBinding()]
param(
    [string]$Container = "hermes"
)

$ErrorActionPreference = "Stop"

$mounts = docker inspect $Container --format "{{json .Mounts}}"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect container: $Container"
}

if ($mounts -notmatch "/workspace/envs/giteerepo") {
    throw "Container mount /workspace/envs/giteerepo is missing."
}

docker exec $Container /opt/hermes/.venv/bin/python3 `
    /workspace/envs/giteerepo/bin/validate-config.py
if ($LASTEXITCODE -ne 0) {
    throw "Container-side configuration validation failed."
}

Write-Host "Runtime validation passed."
