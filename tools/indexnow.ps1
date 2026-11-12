# Tells Bing, Yandex and other IndexNow search engines (used by ChatGPT search and Copilot) about every page in sitemap.xml.
# Run after publishing:   powershell -ExecutionPolicy Bypass -File tools/indexnow.ps1
# Optional: only pages under one folder:   ... -File tools/indexnow.ps1 -Folder tax-refund
# The key file https://tavion.ie/ff806d885d8b07efed4bf5522ac65a62.txt must stay on the site – it proves we own tavion.ie. Free, no account needed.
param([string]$Folder = "")
$key  = "ff806d885d8b07efed4bf5522ac65a62"
$root = Split-Path -Parent $PSScriptRoot
[xml]$map = Get-Content -Raw -Encoding UTF8 (Join-Path $root "sitemap.xml")
$urls = @($map.urlset.url | ForEach-Object { $_.loc } | Where-Object { -not $Folder -or $_ -like "https://tavion.ie/$Folder/*" })
"Submitting " + $urls.Count + " URLs to IndexNow..."
for ($i = 0; $i -lt $urls.Count; $i += 10000) {
  $batch = $urls[$i..([Math]::Min($i + 9999, $urls.Count - 1))]
  $body = @{ host = "tavion.ie"; key = $key; keyLocation = "https://tavion.ie/$key.txt"; urlList = $batch } | ConvertTo-Json -Depth 3
  try {
    $r = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "https://api.indexnow.org/indexnow" -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($body)) -TimeoutSec 120
    "Batch of " + $batch.Count + ": HTTP " + $r.StatusCode + " (200/202 = accepted)"
  } catch { "Batch failed: HTTP " + $_.Exception.Response.StatusCode.value__ + " " + $_.Exception.Message }
}
