# Run only on a real Windows x64 machine (not Linux shims).
# Writes factual test results. No pass can be recorded for a missing/failed run.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$manifest = Get-Content (Join-Path $root 'manifest.json') -Raw | ConvertFrom-Json
$results = @()
foreach ($case in $manifest.cases) {
  $binary = Join-Path $root $case.executable
  $actualHash = (Get-FileHash $binary -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actualHash -ne $case.sha256) { throw "Hash mismatch: $($case.name)" }
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $binary
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true
  $psi.RedirectStandardInput = $true
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $process = New-Object System.Diagnostics.Process
  $process.StartInfo = $psi
  $null = $process.Start()
  [byte[]]$stdinBytes = @()
  for ($i=0; $i -lt $case.stdin_hex.Length; $i+=2) {
    $stdinBytes += [Convert]::ToByte($case.stdin_hex.Substring($i,2),16)
  }
  if ($stdinBytes.Length -gt 0) { $process.StandardInput.BaseStream.Write($stdinBytes,0,$stdinBytes.Length) }
  $process.StandardInput.Close()
  $mem = New-Object System.IO.MemoryStream
  $copyTask = $process.StandardOutput.BaseStream.CopyToAsync($mem)
  if (-not $process.WaitForExit(20000)) {
    $process.Kill()
    throw "Timeout: $($case.name)"
  }
  $copyTask.GetAwaiter().GetResult()
  $outHex = [BitConverter]::ToString($mem.ToArray()).Replace("-","").ToLowerInvariant()
  $status = $process.ExitCode
  $ok = ($outHex -eq $case.expected_stdout_hex)
  if ($case.expected_exit -eq 'zero') { $ok = $ok -and ($status -eq 0) }
  else { $ok = $ok -and ($status -ne 0) }
  $results += [pscustomobject]@{ name=$case.name; pass=$ok; exit_code=$status; stdout_hex=$outHex; sha256=$actualHash }
  Write-Host "$($case.name): $ok"
}
$report = [pscustomobject]@{
   iteration=43
   platform='Windows-native x64'
   host=$env:COMPUTERNAME
   os=[System.Environment]::OSVersion.VersionString
   architecture=[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
   results=$results
   passed=(@($results | Where-Object { $_.pass }).Count)
   total=$results.Count
}
$destination = Join-Path $root 'device_results_windows43.json'
$report | ConvertTo-Json -Depth 5 | Set-Content -Path $destination -Encoding UTF8
if ($report.passed -ne $report.total) { exit 1 }
Write-Host "All $($report.total) Windows loader cases passed; results at $destination"
