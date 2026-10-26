# Terminal 2 (keep open)
Set-Location (Join-Path (Split-Path $PSScriptRoot -Parent) "frontend")
npx ng serve --open --proxy-config proxy.conf.json
