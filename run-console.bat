cd /d %~dp0
powershell "cmd /k 'deskmirror.bat&exit' | tee -a deskmirror.log.txt"
