<#
PowerShell helper to compile the app with PyInstaller and optionally run it.
Usage examples:
  .\compile_and_run.ps1            # build and start EXE
  .\compile_and_run.ps1 -SkipInstall # build without installing packages
  .\compile_and_run.ps1 -RunMode python # run via the venv Python (shows console output)
  .\compile_and_run.ps1 -NoRun     # only build, do not run

Parameters:
  -SkipInstall : Skip pip installs
  -NoRun       : Do not start the app after building
  -RunMode     : 'exe' (default) or 'python'
  -CleanDist   : Remove existing dist/ and build/ before building
#>
param(
    [switch]$SkipInstall,
    [switch]$NoRun,
    [ValidateSet('exe','python')][string]$RunMode = 'exe',
    [switch]$CleanDist
)

$ErrorActionPreference = 'Stop'

$Repo = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Push-Location $Repo

$PythonExe = Join-Path $Repo ".venv\Scripts\python.exe"
<#
PowerShell helper to compile the app with PyInstaller and optionally run it.
Usage examples:
  .\compile_and_run.ps1            # build and start EXE
  .\compile_and_run.ps1 -SkipInstall # build without installing packages
  .\compile_and_run.ps1 -RunMode python # run via the venv Python (shows console output)
  .\compile_and_run.ps1 -NoRun     # only build, do not run

Parameters:
  -SkipInstall : Skip pip installs
  -NoRun       : Do not start the app after building
  -RunMode     : 'exe' (default) or 'python'
  -CleanDist   : Remove existing dist/ and build/ before building
#>
param(
    [switch]$SkipInstall,
    [switch]$NoRun,
    [ValidateSet('exe','python')][string]$RunMode = 'exe',
    [switch]$CleanDist
)

$ErrorActionPreference = 'Stop'

$Repo = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Push-Location $Repo

$PythonExe = Join-Path $Repo ".venv\Scripts\python.exe"
<#
PowerShell helper to compile the app with PyInstaller and optionally run it.
Usage examples:
  .\compile_and_run.ps1            # build and start EXE
  .\compile_and_run.ps1 -SkipInstall # build without installing packages
  .\compile_and_run.ps1 -RunMode python # run via the venv Python (shows console output)
  .\compile_and_run.ps1 -NoRun     # only build, do not run

Parameters:
  -SkipInstall : Skip pip installs
  -NoRun       : Do not start the app after building
  -RunMode     : 'exe' (default) or 'python'
  -CleanDist   : Remove existing dist/ and build/ before building
#>
param(
    [switch]$SkipInstall,
    [switch]$NoRun,
    [ValidateSet('exe','python')][string]$RunMode = 'exe',
    [switch]$CleanDist
)

$ErrorActionPreference = 'Stop'

$Repo = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Push-Location $Repo

$PythonExe = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Warning ".venv Python not found at $PythonExe — falling back to system 'python'."
    $PythonExe = 'python'
}

if ($CleanDist) {
    Write-Host "Cleaning previous build artifacts..."
    if (Test-Path "$Repo\dist") { Remove-Item -Recurse -Force "$Repo\dist" }
    if (Test-Path "$Repo\build") { Remove-Item -Recurse -Force "$Repo\build" }
}

if (-not $SkipInstall) {
    Write-Host "Installing/ensuring build dependencies in venv..."
    & $PythonExe -m pip install --upgrade pip setuptools wheel
    & $PythonExe -m pip install -r requirements.txt
    & $PythonExe -m pip install pyinstaller
}

Write-Host "Starting PyInstaller build..."
$icon = Join-Path $Repo 'icon.ico'
$main = Join-Path $Repo 'main.py'
# Use PyInstaller to create onefile, windowed EXE and include icon.ico as data
& $PythonExe -m PyInstaller --onefile --windowed --icon "$icon" --add-data "icon.ico;." --name MicrophoneTranscriber "$main"

# Move EXE to repo root if produced
$exeDist = Join-Path $Repo 'dist\MicrophoneTranscriber.exe'
$exeRoot = Join-Path $Repo 'MicrophoneTranscriber.exe'
if (Test-Path $exeDist) {
    if (Test-Path $exeRoot) { Remove-Item -Force $exeRoot }
    Move-Item -Path $exeDist -Destination $exeRoot
    Write-Host "Moved MicrophoneTranscriber.exe to project root."
} else {
    Write-Warning "Expected EXE not found at $exeDist — check PyInstaller output above for errors."
}

if ($NoRun) {
    Write-Host "Build finished (NoRun specified)."
    Pop-Location
    return
}

if ($RunMode -eq 'exe') {
    if (Test-Path $exeRoot) {
        Write-Host "Launching MicrophoneTranscriber.exe (windowed)..."
        Start-Process -FilePath $exeRoot -WorkingDirectory $Repo
    } else {
        Write-Warning "EXE not found; to run with console output, use -RunMode python."
    }
} else {
    Write-Host "Running via Python to capture console output. Logs: run.log, run.err"
    # Run in a separate PowerShell job so script returns control.
    $logOut = Join-Path $Repo 'run.log'
    $logErr = Join-Path $Repo 'run.err'
    $ps = Start-Job -ScriptBlock { param($py,$main,$out,$err)
        & $py $main *> $out 2> $err
    } -ArgumentList $PythonExe,$main,$logOut,$logErr
    Write-Host "Started background job id=" $ps.Id " to run main.py; use Get-Job / Receive-Job to inspect."
}

Pop-Location
Write-Host "Done."
