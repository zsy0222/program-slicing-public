# Run Error Invariants on the two unique P-V2b top-1 patches via the user's
# Windows SSH Agent. This script never reads a private key file.

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$patchRoot = Join-Path $projectRoot "03_experiments\outputs\deepseek_v2_mapped_2026-08-23\P_V2b_mapped_closed_loop_patch_validation\work"
$outputDir = Join-Path $projectRoot "03_experiments\outputs\v2_static_delta_2026-08-23"
$remoteDir = "/tmp/v2_static_delta_20260823"
$target = "vboxuser@127.0.0.1"

$targets = @(
    @{
        Id = "Seed01_update_sign_top1"
        Source = Join-Path $patchRoot "Seed01_update_sign_r1\candidate_1.c"
    },
    @{
        Id = "Seed03_initial_value_v2_top1"
        Source = Join-Path $patchRoot "Seed03_initial_value_v2_r1\candidate_1.c"
    }
)

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
ssh -o BatchMode=yes -p 2222 $target "mkdir -p $remoteDir; test -x /home/vboxuser/error-invariants-work/error_inv/Main.native"
if ($LASTEXITCODE -ne 0) { throw "SSH connection or remote analyzer check failed." }

foreach ($item in $targets) {
    if (-not (Test-Path -LiteralPath $item.Source)) {
        throw "Expected patch source not found: $($item.Source)"
    }
    $remoteSource = "$remoteDir/$($item.Id).c"
    $remoteOutput = "$remoteDir/$($item.Id).out"
    scp -o BatchMode=yes -P 2222 $item.Source "${target}:$remoteSource"
    if ($LASTEXITCODE -ne 0) { throw "Upload failed for $($item.Id)." }
    $command = "eval `"`$(opam env)`"; timeout 60s /home/vboxuser/error-invariants-work/error_inv/Main.native -full -domain polyhedra $remoteSource > $remoteOutput 2>&1; code=`$?; echo exit=`$code"
    $result = ssh -o BatchMode=yes -p 2222 $target $command
    if ($LASTEXITCODE -ne 0) { throw "Analyzer command transport failed for $($item.Id)." }
    $result | Set-Content -Encoding utf8 (Join-Path $outputDir "$($item.Id).status.txt")
    scp -o BatchMode=yes -P 2222 "${target}:$remoteOutput" (Join-Path $outputDir "$($item.Id).out")
    if ($LASTEXITCODE -ne 0) { throw "Download failed for $($item.Id)." }
}

Write-Host "Completed. Outputs written to: $outputDir"
