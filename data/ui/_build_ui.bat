@ECHO OFF
setlocal enabledelayedexpansion
for %%f in (.\*.ui) do (
  echo Generating file %%~nf.py...
  pyuic5 -o ..\..\src\ui\%%~nf_ui.py %%~nf.ui
)
echo Finished!