import logging
import os
import pathlib
import sys
import time
from logging.handlers import RotatingFileHandler

import dirsync
import pygit2

# Failsafe
base_dir = os.path.dirname(os.path.abspath(__file__))
# 等待录入的logs
pending_logs = ["Hello."]

try:
    # 仅Windows
    if os.name != "nt":
        raise OSError("Windows Only Feature.")

    drive_found = False
    # 获取所有可用的驱动器
    drives = pathlib.Path().cwd().glob("**/*:/")

    # 遍历每个驱动器
    for drive in drives:
        # 获取驱动器的路径
        drive_path = str(drive)
        # 尝试打开驱动器
        try:
            os.startfile(drive_path)
            # 在根目录下查找文件名为sunset_destination.txt的文件
            files = pathlib.Path(drive_path).glob("sunset_destination.txt")
            # 如果找到了，打印驱动器的路径并退出循环
            for file in files:
                pending_logs.append(
                    f"Found {file} in {drive_path}, it will be the destination.")
                base_dir = os.path.dirname(drive_path)
                drive_found = True
                break
        # 如果打开失败，跳过该驱动器
        except:
            continue

    if not drive_found:
        raise Exception("Drive not found.")
except Exception:
    import traceback
    pending_logs.append(traceback.format_exc)
    pending_logs.append("Failed to find the destination, use script location.")
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        pending_logs.append('running in a PyInstaller bundle')
        base_dir = os.path.dirname(sys.executable)
    else:
        pending_logs.append('running in a normal Python process')
        base_dir = os.path.dirname(os.path.abspath(__file__))

# 配置logging
log_file = os.path.join(base_dir, "sync.log")
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
log_handler = RotatingFileHandler(log_file, maxBytes=1048576, backupCount=3)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)
log_console_handler = logging.StreamHandler()
log_console_handler.setFormatter(log_formatter)
log_console_handler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
logger.addHandler(log_console_handler)
logger.setLevel(logging.INFO)

for log in pending_logs:
    logger.info(log)

try:
    # 获取当前用户桌面路径
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")

    # 设置同步目录
    sync_dir = os.path.join(base_dir, "DesktopMirror")

    # 记录同步目录信息
    logger.info(f"Syncing desktop folder from {desktop} to {sync_dir}...")

    # 如果同步目录不存在，则创建它
    if not os.path.exists(sync_dir):
        os.makedirs(sync_dir)
        logger.info(f"Created sync folder {sync_dir}.")

    # 初始化Git版本库
    git_dir = os.path.join(sync_dir, ".git")
    pygit2.option(pygit2.GIT_OPT_SET_OWNER_VALIDATION, 0)
    if not os.path.exists(git_dir):
        repo = pygit2.init_repository(sync_dir)
        logger.info(f"Initialized empty Git repository in {sync_dir}.")
    else:
        repo = pygit2.Repository(sync_dir)

    # 使用dirsync库同步文件夹
    changes = dirsync.sync(desktop, sync_dir, "sync", exclude=[
        ".git"], logger=logger, verbose=True)

    # 如果有文件更改，则提交到Git版本库
    if changes:
        index = repo.index
        index.add_all()
        index.write()
        tree_oid = index.write_tree()
        author = pygit2.Signature("Your Name", "your.email@example.com")
        committer = author
        commit_message = f"Update desktop files on {time.strftime('%Y-%m-%d %H:%M:%S')}"
        commit_oid = repo.create_commit(
            "HEAD", author, committer, commit_message, tree_oid, [])
        logger.info(f"Committed changes with id: {commit_oid}.")
    else:
        logger.info("No changes detected. Nothing to commit.")

    logger.info("Done.")
except Exception as e:
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)
