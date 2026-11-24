@echo off
setlocal

for %%I in ("%~dp0..") do set "PLUGIN_ROOT=%%~fI"
set "PYTHON=%KNOWLEDGE_BUNDLE_PYTHON%"
if not defined PYTHON (
    set "DATA_HOME=%XDG_DATA_HOME%"
    if not defined DATA_HOME set "DATA_HOME=%USERPROFILE%\.local\share"
    set "PYTHON=%DATA_HOME%\kb-skeleton\venv\Scripts\python.exe"
)

if not exist "%PYTHON%" set "PYTHON=%PLUGIN_ROOT%\.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    >&2 echo No Python environment found. Run: py "%PLUGIN_ROOT%\scripts\setup_plugin.py"
    exit /b 1
)

pushd "%PLUGIN_ROOT%" || exit /b 1
"%PYTHON%" %*
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
