# Simple test script to debug PowerShell issues
param(
    [switch]$DryRun
)

Write-Host "Testing PowerShell script execution..."
Write-Host "DryRun parameter: $DryRun"

# Test CSV path
$CSV_PATH = "PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv"
Write-Host "CSV Path: $CSV_PATH"

# Test if file exists
if (Test-Path $CSV_PATH) {
    Write-Host "✅ CSV file exists" -ForegroundColor Green
    try {
        $rows = Import-Csv -Path $CSV_PATH -Encoding UTF8
        Write-Host "✅ CSV loaded successfully: $($rows.Count) rows" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error loading CSV: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ CSV file not found" -ForegroundColor Red
}

Write-Host "Script completed successfully!"
