# DesktopMirror
Batch Script for Mirroring Current User's Desktop Files

# Environments
Tested on Windows 11, should run correctly on Windows 7 & above.

自动同步当前用户桌面文件到：
* 根目录有`sunset_destination.txt`的第一个被遍历的驱动器
* 脚本同目录
* Pyinstaller可执行文件同目录

并使用Git管理版本。

构建指令`pyinstaller --onedir --hidden-import=_cffi_backend --name DesktopMirrorExecutable --console DesktopMirror.py`。

使用`onedir`避免低I/O硬盘自解压造成的效率问题。
