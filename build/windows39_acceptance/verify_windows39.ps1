# Executes prebuilt BF-generated PE32+ fixtures on an actual x64 Windows host.
# This is a target-side smoke test, not a Windows BF compiler bootstrap.
param([string]$Output = "windows39-result.json")
$ErrorActionPreference = 'Stop'
if (-not $IsWindows -and $PSVersionTable.PSEdition -eq 'Core') { throw "Windows required" }
if (-not [Environment]::Is64BitOperatingSystem) { throw "64-bit Windows required" }
$base = Split-Path -Parent $MyInvocation.MyCommand.Path
$manifest = Get-Content -Raw -LiteralPath (Join-Path $base 'manifest.json') | ConvertFrom-Json
$results = @()
foreach ($case in $manifest.fixtures) {
    $path = Join-Path $base $case.file
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
    if ($actual -ne $case.sha256) { throw "Fixture checksum mismatch for $($case.name)" }
    $pi = New-Object System.Diagnostics.ProcessStartInfo
    $pi.FileName = $path
    $pi.UseShellExecute = $false
    $pi.CreateNoWindow = $true
    $pi.RedirectStandardOutput = $true
    $pi.RedirectStandardError = $true
    $proc = [System.Diagnostics.Process]::Start($pi)
    if (-not $proc.WaitForExit(10000)) {
        try { $proc.Kill() } catch {}
        $entry = @{name=$case.name; sha256=$actual; status='TIMEOUT'}
    } else {
        $stdout = $proc.StandardOutput.ReadToEnd()
        $stderr = $proc.StandardError.ReadToEnd()
        $entry = @{name=$case.name; sha256=$actual; exit_code=$proc.ExitCode;
                   stdout=$stdout;stderr=$stderr;
                   status=$(if ($proc.ExitCode -eq 0 -and $stdout.Length -eq 0 -and $stderr.Length -eq 0) {'PASS'} else {'FAIL'})}
    }
    $proc.Dispose()
    $results += $entry
}
$record = @{os=[Environment]::OSVersion.VersionString;
             os64bit=[Environment]::Is64BitOperatingSystem;
             arch=[System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture.ToString();
             timestamp_utc=[DateTime]::UtcNow.ToString('o');
             results=$results}
$record | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $base $Output)
$record | ConvertTo-Json -Depth 8
if (@($results | Where-Object {$_.status -ne 'PASS'}).Count -gt 0) { exit 1 }
