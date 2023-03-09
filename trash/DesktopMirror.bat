@echo off

setlocal enabledelayedexpansion

REM 获取当前用户桌面路径
set desktop=%userprofile%\Desktop

REM 设置同步目录
set sync_dir=%~dp0DesktopMirror

REM 如果同步目录不存在，则创建它
if not exist "%sync_dir%" mkdir "%sync_dir%"

REM 切换到同步目录
cd /d "%sync_dir%"

REM 初始化Git版本库
if not exist "%sync_dir%\.git" (
    git init
    echo Initialized empty Git repository in %sync_dir%\.git/
)

REM 使用robocopy命令同步文件夹（排除.git文件夹）
robocopy "%desktop%" "%sync_dir%" /E /ZB /PURGE /XO /FFT /R:3 /W:10 /XD .git

REM 将更改提交到Git版本库
git add .
git commit -m "Update desktop files on %date% %time%"

echo Done.
pause
