import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

import dirsync
import pygit2

# 配置logging
log_file = os.path.join("sync.log")
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

try:
    # 获取当前用户桌面路径
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")

    # 设置同步目录
    sync_dir = os.path.join("DesktopMirror")

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
