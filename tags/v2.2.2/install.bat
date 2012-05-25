@echo off
@call setup.py install
if errorlevel 1 goto error
goto end
:error
echo -=-=-=-=-=-=-=-=-=-=-
echo There was an error during the installation.
echo Please check the above text for more information.
pause
:end
@echo on
