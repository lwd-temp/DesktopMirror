cd /d %~dp0
powershell "cmd /k deskmirror.bat | tee deskmirror.log.txt"
pause