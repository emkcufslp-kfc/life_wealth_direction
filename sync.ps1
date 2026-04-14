# Sync Script
$src = "d:\Backtest\紫微"
$dst = "d:\Backtest\life_wealth_direction"

Write-Host "Copying files to $dst..."
Copy-Item "$src\Life.py" "$dst\" -Force
Copy-Item "$src\backend\*" "$dst\backend\" -Recurse -Force
Copy-Item "$src\assets\*" "$dst\assets\" -Recurse -Force
Copy-Item "$src\*.md" "$dst\" -Force
Copy-Item "$src\*.png" "$dst\" -Force
Copy-Item "$src\*.json" "$dst\" -Force
Copy-Item "$src\*.txt" "$dst\" -Force
Copy-Item "$src\*.xlsx" "$dst\" -Force
Copy-Item "$src\sync.ps1" "$dst\" -Force

Write-Host "Performing Git operations in $dst..."
Set-Location $dst
git add .
git commit -m "Institutional Hardening (v6.43): Traditional Chinese Localization & High-Fidelity SOP Matrix Integration"
git push origin main
