@echo off
@call setup.py install
if errorlevel 1 goto error
goto end
:error
echo -=-=-=-=-=-=-=-=-=-=-
echo There was an error during the installation. Please check the above text
echo for more information before you
pause
:end
@echo on