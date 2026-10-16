# Target-side acceptance only. It does not build or repair executable images.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$manifest = Get-Content .\manifest.json -Raw | ConvertFrom-Json
$records = @()
foreach ($case in $manifest.programs) {
    $path = Join-Path $PSScriptRoot $case.executable
    $actualHash = (Get-FileHash -Path $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $case.sha256) { throw "Artifact SHA mismatch $($case.name)" }
    $record = [ordered]@{name=$case.name; sha256=$actualHash; launched=$false; passed=$false; exit_code=$null; stdout_hex=$null; stderr=$null; error=$null}
    try {
        $info = New-Object System.Diagnostics.ProcessStartInfo
        $info.FileName = $path
        $info.WorkingDirectory = $PSScriptRoot
        $info.UseShellExecute = $false
        $info.RedirectStandardInput = $true
        $info.RedirectStandardOutput = $true
        $info.RedirectStandardError = $true
        $info.CreateNoWindow = $true
        $p = [System.Diagnostics.Process]::Start($info)
        $record.launched = $true
        $inBytes = [byte[]]::new([int]($case.stdin_hex.Length / 2))
        for ($i=0; $i -lt $inBytes.Length; $i++) { $inBytes[$i] = [Convert]::ToByte($case.stdin_hex.Substring($i*2,2),16) }
        $p.StandardInput.BaseStream.Write($inBytes,0,$inBytes.Length)
        $p.StandardInput.Close()
        $mem = New-Object System.IO.MemoryStream
        $p.StandardOutput.BaseStream.CopyTo($mem)
        $err = $p.StandardError.ReadToEnd()
        $p.WaitForExit()
        $record.exit_code = $p.ExitCode
        $record.stdout_hex = [BitConverter]::ToString($mem.ToArray()).Replace('-','').ToLowerInvariant()
        $record.stderr = $err
        $expectZero = ($case.expected_exit -eq 'zero')
        $exitOk = if ($expectZero) { $record.exit_code -eq 0 } else { $record.exit_code -ne 0 }
        $record.passed = $exitOk -and ($record.stdout_hex -eq $case.expected_stdout_hex)
    } catch {
        $record.error = $_.Exception.Message
    }
    $records += [pscustomobject]$record
}
$output = [ordered]@{
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    computer = $env:COMPUTERNAME
    windows_version = [System.Environment]::OSVersion.VersionString
    processor_architecture = $env:PROCESSOR_ARCHITECTURE
    cases = @($records)
    all_passed = (@($records | Where-Object { -not $_.passed }).Count -eq 0)
}
$output | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 .\device_results_windows40.json
Write-Host ($output | ConvertTo-Json -Depth 8)
if (-not $output.all_passed) { exit 1 }
