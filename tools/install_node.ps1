param([string]$ReleaseMajor = '24')
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$runtimeRoot = Join-Path $workspaceRoot '.tools/node'
New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
$index = Invoke-RestMethod -Uri 'https://nodejs.org/dist/index.json'
$release = $index | Where-Object { $_.lts -and $_.version -match "^v$ReleaseMajor\." -and $_.files -contains 'win-x64-zip' } | Select-Object -First 1
if (-not $release) { throw 'No matching official Node LTS release found.' }
$archiveName = "node-$($release.version)-win-x64.zip"
$archivePath = Join-Path $runtimeRoot $archiveName
$releaseUrl = "https://nodejs.org/dist/$($release.version)"
$checksums = (Invoke-WebRequest -Uri "$releaseUrl/SHASUMS256.txt").Content
$checksumLine = ($checksums -split "`n") | Where-Object { $_.Trim().EndsWith("  $archiveName") } | Select-Object -First 1
if (-not $checksumLine) { throw 'Official SHA-256 checksum missing.' }
$expected = ($checksumLine.Trim() -split '\s+')[0].ToLowerInvariant()
if (-not (Test-Path -LiteralPath $archivePath)) {
    Invoke-WebRequest -Uri "$releaseUrl/$archiveName" -OutFile $archivePath
}
$actual = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw 'Checksum mismatch: archive retained for inspection, not extracted.' }
$installPath = Join-Path $runtimeRoot $archiveName.Replace('.zip', '')
if (-not (Test-Path -LiteralPath (Join-Path $installPath 'node.exe'))) {
    Expand-Archive -LiteralPath $archivePath -DestinationPath $runtimeRoot
}
$manifest = @{version = $release.version; sha256 = $actual; source = "$releaseUrl/$archiveName"; directory = $installPath}
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtimeRoot 'runtime.json') -Encoding utf8
& (Join-Path $installPath 'node.exe') --version
Write-Output "Verified portable runtime: $installPath"
