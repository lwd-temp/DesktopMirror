cd /d %~dp0
powershell "cmd /k deskmirror.bat | tee -a deskmirror.log.txt"