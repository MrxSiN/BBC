@echo off
setlocal
for /f "usebackq delims=" %%i in (`"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "BF_MSVC_ROOT=%%i"
if not defined BF_MSVC_ROOT exit /b 1
call "%BF_MSVC_ROOT%\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1
if not exist "%~dp0..\build\android_optimization" mkdir "%~dp0..\build\android_optimization"
pushd "%~dp0..\build\android_optimization"
cl /nologo /O2 /std:c11 /D_CRT_SECURE_NO_WARNINGS /Fe:seed.exe /Fo:seed.obj ..\..\bootstrap\seed_interpreter.c
if errorlevel 1 exit /b 1
cl /nologo /O2 /std:c11 /D_CRT_SECURE_NO_WARNINGS /Fe:seed_alt.exe /Fo:seed_alt.obj ..\..\bootstrap\seed_interpreter_alt.c
if errorlevel 1 exit /b 1
popd
