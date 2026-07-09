# TSE CLI - PowerShell Setup Script

$VenvPath = "C:\Users\AADI\Desktop\My\CODE\Github\savior\venv\Scripts"
$ExecPath = "$VenvPath\tse.exe"

if (Test-Path $ExecPath) {
    # 1. Update User PATH permanently
    $UserPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    if ($UserPath -notlike "*$VenvPath*") {
        [System.Environment]::SetEnvironmentVariable("Path", $UserPath + ";$VenvPath", "User")
        Write-Host "✅ Successfully added TSE to your User PATH!" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ PATH is already configured." -ForegroundColor Cyan
    }

    # 2. Register alias for current session
    Set-Alias -Name tse -Value $ExecPath -Scope Global
    
    Write-Host "🚀 'tse' is now ready to use in this PowerShell session!" -ForegroundColor Green
    Write-Host "🔥 Try typing: tse about" -ForegroundColor Green
    Write-Host "💡 Note: For other terminal windows, restart them to load the permanent PATH updates." -ForegroundColor Yellow
} else {
    Write-Host "❌ Error: Could not find tse executable at $ExecPath." -ForegroundColor Red
    Write-Host "Please make sure the project virtual environment is fully installed." -ForegroundColor Yellow
}
