@ECHO OFF
setlocal enabledelayedexpansion
for %%f in (.\*.ui) do (
  echo Generating file %%~nf.py...
  pyuic5 -o ..\..\src\ui\ui_%%~nf.py %%~nf.ui
)
echo Finished!