import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

import dirsync
import pygit2
import win32api

# Failsafe
base_dir = os.path.dirname(os.path.abspath(__file__))
# 等待录入的logs
pending_logs = ["Hello."]

try:
    # 仅Windows
    if os.name != "nt":
        raise OSError("Windows only feature.")

    drive_found = False

    # 获取所有驱动器列表
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    # 创建一个空列表，用于存放结果
    result = []
    # 遍历每个驱动器
    for drive in drives:
        # 拼接文件路径
        file_path = os.path.join(drive, 'sunset_destination.txt')
        # 检查文件是否存在
        if os.path.exists(file_path):
            # 如果存在
            base_dir = os.path.dirname(file_path)
            drive_found = True
            break

    if not drive_found:
        raise Exception("Drive not found.")
except Exception:
    import traceback
    pending_logs.append(traceback.format_exc())
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
