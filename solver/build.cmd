@echo off
rem ISOBAR solver build - MSVC (VS 2022) for the CPU reference, nvcc 13.x for the GPU tier.
rem The CPU build MUST succeed with no CUDA toolkit present; the GPU build is skipped with a
rem printed reason if nvcc is absent. Both binaries run --selftest at the end; nonzero fails.
setlocal enabledelayedexpansion
where cl >nul 2>nul
if errorlevel 1 (
  set "VCV=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
  if not exist "!VCV!" ( echo build: vcvars64.bat not found & exit /b 1 )
  call "!VCV!" >nul
)
cd /d "%~dp0"
if not exist build mkdir build

rem --- CPU reference: the same source, serial, same oracles -------------------------------------
rem /TP forces C++ regardless of the .cu extension. The CPU macro is the file's own (LL_CPU until
rem the lift renames it to ISOBAR_CPU; both are defined so either generation of the source builds).
cl /nologo /std:c++17 /O2 /EHsc /TP /DLL_CPU /DISOBAR_CPU /D_CRT_SECURE_NO_WARNINGS /Fo:build\ /Fe:build\isobar_field_cpu.exe isobar_field.cu || exit /b 1
echo build: isobar_field_cpu.exe ok

rem --- GPU tier: skipped, not failed, when nvcc is absent ----------------------------------------
where nvcc >nul 2>nul
if errorlevel 1 (
  echo build: nvcc not found - GPU tier skipped ^(the CPU reference is first-class^)
) else (
  nvcc -O3 -std=c++17 -arch=sm_89 -o build\isobar_field.exe isobar_field.cu || exit /b 1
  echo build: isobar_field.exe ok ^(sm_89^)
)

rem --- selftests: every oracle, nonzero exit on failure --------------------------------------------
build\isobar_field_cpu.exe --selftest || exit /b 1
if exist build\isobar_field.exe ( build\isobar_field.exe --selftest || exit /b 1 )
echo build: selftests green
