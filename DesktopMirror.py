import os

import dirsync
import pygit2

# 获取当前用户桌面路径
desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")

# 设置同步目录
sync_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "DesktopMirror")

# 如果同步目录不存在，则创建它
if not os.path.exists(sync_dir):
    os.makedirs(sync_dir)

# 初始化Git版本库
git_dir = os.path.join(sync_dir, ".git")
if not os.path.exists(git_dir):
    repo = pygit2.init_repository(git_dir)
    print(f"Initialized empty Git repository in {git_dir}/")
else:
    repo = pygit2.Repository(git_dir)

# 使用dirsync库同步文件夹
dirsync.sync(desktop, sync_dir, "sync", exclude=[".git"])

# 将更改提交到Git版本库
index = repo.index
index.add_all()
index.write()
tree_oid = index.write_tree()
author = pygit2.Signature("Your Name", "your.email@example.com")
committer = author
commit_message = f"Update desktop files on {pygit2.time.time()}"
commit_oid = repo.create_commit(
    "HEAD", author, committer, commit_message, tree_oid, [])
print(f"Committed changes with id: {commit_oid}")

print("Done.")
