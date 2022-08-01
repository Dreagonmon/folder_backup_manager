# https://github.com/Dreagonmon/async_termux_api/blob/main/termux.py
# https://docs.python.org/3/library/getpass.html#getpass.getuser
# https://www.ruanyifeng.com/blog/2020/08/rsync.html
# SUDO_USER="dreagonmon"; id dreagonmon -gn
# BackupFolder
# |-- SourceFolders
# |-- BackupFolders
# |-- Excludes
# |-- Includes
# |-- Options
# git rev-parse --is-inside-work-tree
# git ls-files -oc --exclude-standar
import os, sys, asyncio
APP_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, APP_ROOT) # ensure import path
os.chdir(APP_ROOT)
import items, utils

def random_str(size):
    return hex(int.from_bytes(os.urandom(size//2), "big"))[2:].upper()

async def main():
    print("========")
    cfg = items.get_config()
    s_dir = cfg.backup_items[0].source_folders[0]
    b_dir = cfg.backup_items[0].backup_folders[0]
    async for proc in utils.backup_files(s_dir, b_dir):
        stage, count, total, info = proc
        # if stage == utils.BackupProgressStage.ERROR:
        print(f"{stage.name} || <{count}/{total}> || {info}")

if __name__ == "__main__":
    asyncio.run(main())
