@echo off
setlocal

set "ROOT=%~dp0"
set "GPP="

if exist "%ProgramFiles%\GNU Octave\Octave-11.1.0\mingw64\bin\g++.exe" (
  set "GPP=%ProgramFiles%\GNU Octave\Octave-11.1.0\mingw64\bin\g++.exe"
) else if exist "%ProgramFiles(x86)%\GNU Octave\Octave-11.1.0\mingw64\bin\g++.exe" (
  set "GPP=%ProgramFiles(x86)%\GNU Octave\Octave-11.1.0\mingw64\bin\g++.exe"
) else (
  for %%I in (g++) do if exist "%%~$PATH:I" set "GPP=%%~$PATH:I"
)

if not defined GPP (
  echo No C++ compiler found. Install MinGW-w64 or add g++ to PATH.
  exit /b 1
)

echo Using compiler: %GPP%
"%GPP%" -std=c++17 -O2 -Wall -shared -o "%ROOT%engine.dll" -I"%ROOT%cpp\include" "%ROOT%cpp\src\Detectors.cpp" "%ROOT%cpp\src\FreeFaceEngine.cpp" "%ROOT%cpp\src\engine_api.cpp"
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

echo Build succeeded: %ROOT%engine.dll
exit /b 0
