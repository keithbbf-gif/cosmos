# install.ps1 — TokenCenter / COSMOS pay: fresh-machine installer (Windows)
# The friction ladder, step 1. Borrowed: Hermes's install.ps1 shape.
#
#   iex (irm https://tokenctr.com/install.ps1)
#
# What it does:
#   1. Verifies Python 3.11+ (offers winget install if missing)
#   2. Creates %USERPROFILE%\.cosmos_pay\ (config + secrets templates)
#   3. Copies the pay modules from -Source (default: the download dir this script ships with)
#   4. Prints the next step: run the app → the first-run wizard takes over
#
# Param([string]$Source = "$PSScriptRoot")

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== TokenCenter installer ===" -ForegroundColor Cyan

# --- 1. Python ---
$py = Get-Command py -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $py) {
    Write-Host "Python not found. Install with:" -ForegroundColor Yellow
    Write-Host "  winget install Python.Python.3.13"
    Write-Host "…then re-run this installer." 
    exit 1
}
$ver = & $py.Source -3 --version 2>$null
if (-not $ver) { $ver = & python --version 2>$null }
Write-Host "Python: $ver"

# --- 2. Root ---
$root = "$env:USERPROFILE\.cosmos_pay"
New-Item -ItemType Directory -Force -Path $root | Out-Null
Write-Host "Root: $root"

# --- 3. Modules ---
$source = if ($Source) { $Source } else { $PSScriptRoot }
$modules = @(
    "cosmos_pay_config.py", "cosmos_pay_toll.py", "cosmos_pay_pricing.py",
    "cosmos_pay_meter.py", "cosmos_pay_entitlement.py", "cosmos_pay_runpod_rail.py",
    "cosmos_pay_gateway.py", "cosmos_pay_processors.py", "cosmos_pay_founding.py",
    "cosmos_pay_webhooks.py", "cosmos_pay_nightly.py", "cosmos_pay_smoke.py",
    "cosmos_pay_wizard.py", "cosmos_pay_cloudflare.py"
)
$copied = 0
foreach ($m in $modules) {
    $src = Join-Path $source $m
    if (Test-Path $src) {
        Copy-Item $src (Join-Path $root $m) -Force
        $copied++
    }
}
Write-Host "Modules copied: $copied/$($modules.Count) (source: $source)"
if ($copied -eq 0) {
    Write-Host "No modules found at $source — pass -Source <dir> with the module files." -ForegroundColor Yellow
}

# --- 4. Config + secrets templates (never overwritten) ---
if (-not (Test-Path "$root\config.json")) {
    @{ gateway = @{host = "127.0.0.1"; port = 8787}
       free_tier = @{daily_face_usd = 1.5; reset_tz = "UTC"} } | ConvertTo-Json -Depth 5 |
        Set-Content "$root\config.json" -Encoding UTF8
}
if (-not (Test-Path "$root\secrets.json")) {
    @{ _comment = "Fill these. NEVER in git."
       runpod_api_key = ""; runpod_endpoint_id = ""
       mesh_hmac_key_hex = ""; setup_key = ""
       cloudflare_api_token = ""; cloudflare_account_id = ""; cloudflare_zone_id = ""
       cloudflare_turnstile_secret_key = ""
       stripe_secret_key = ""; stripe_webhook_secret = ""
       paypal_client_id = ""; paypal_client_secret = "" } | ConvertTo-Json -Depth 3 |
        Set-Content "$root\secrets.json" -Encoding UTF8
    Write-Host "Secrets template written — fill before going live." -ForegroundColor Yellow
}

# --- 5. Next step ---
Write-Host ""
Write-Host "=== Installed. Next: ===" -ForegroundColor Cyan
Write-Host "  1. Fill $root\secrets.json (RunPod key, HMAC key, processor keys)"
Write-Host "  2. Start the gateway:  py -3 $root\cosmos_pay_gateway.py"
Write-Host "  3. Smoke test:         py -3 $root\cosmos_pay_smoke.py --live --key <your-key>"
Write-Host "  4. The app (cDeck) walks the rest: sign in → verified task → Founding offer"
Write-Host ""
