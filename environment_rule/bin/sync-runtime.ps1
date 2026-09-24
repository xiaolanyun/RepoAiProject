[CmdletBinding()]
param(
    [string]$Container = "hermes"
)

$ErrorActionPreference = "Stop"

$mounts = docker inspect $Container --format "{{json .Mounts}}"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect container: $Container"
}

if ($mounts -notmatch "/workspace/envs") {
    throw "Container mount /workspace/envs is missing."
}

if ($mounts -notmatch "/workspace/secrets") {
    throw "Container mount /workspace/secrets is missing."
}

docker exec $Container /opt/hermes/.venv/bin/python3 `
    /workspace/envs/giteerepo/bin/validate-config.py
if ($LASTEXITCODE -ne 0) {
    throw "Container-side configuration validation failed."
}

docker exec $Container bash -n `
    /workspace/envs/giteerepo/bin/remote_runner.sh
if ($LASTEXITCODE -ne 0) {
    throw "remote_runner.sh syntax validation failed."
}

Write-Host "Runtime validation passed."
