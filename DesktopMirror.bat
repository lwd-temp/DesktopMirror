@echo off
setlocal

rem 获取脚本所在目录的路径
for %%i in ("%~dp0.") do set "script_dir=%%~fi"

rem 获取当前用户桌面路径
set "desktop_dir=%userprofile%\Desktop"

rem 创建DesktopMirror文件夹
set "mirror_dir=%script_dir%\DesktopMirror"
if not exist "%mirror_dir%" mkdir "%mirror_dir%"

rem 同步桌面到DesktopMirror
xcopy /e /y "%desktop_dir%" "%mirror_dir%"

rem 进入DesktopMirror目录
cd "%mirror_dir%"

rem 指定Git可执行文件路径
set "git_exec_path=C:\Program Files\Git\bin\git.exe"

rem 初始化Git仓库
if not exist "%mirror_dir%\.git" "%git_exec_path%" init

rem 添加所有更改并提交
"%git_exec_path%" add --all
"%git_exec_path%" commit -m "Update desktop mirror on %date% %time%"

rem 返回脚本所在目录
cd "%script_dir%"
