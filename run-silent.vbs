Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "cmd /c run-autoexit.bat"
oShell.Run strArgs, 0, false