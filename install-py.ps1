Write-Host "Starting..."

$FilePath = [Environment]::GetFolderPath("Desktop") + "\python-3.7.0.exe"

If (Test-Path $FilePath) {
    Write-Host "The executable already exists!"
    Return
}

Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.7.0/python-3.7.0.exe" -OutFile $FilePath

C:\Users\spenc\Desktop\python-3.7.0.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

Write-Host "Done!"
Read-Host -Prompt "Press Enter to exit"
