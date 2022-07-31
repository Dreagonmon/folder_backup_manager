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
import re, utils, time

REGEXP_CACHE = re.compile(r".*cache.*", re.IGNORECASE)

def filter(path: str):
    if path.startswith("/."):
        return True
    return REGEXP_CACHE.match(path)
    pass

async def main():
    print("========")
    # print(await utils.async_input("EN? "))
    for _ in range(1):
        lst = set()
        ts = time.time_ns()
        # async for f in utils.list_dir_gen("/run/media/dreagonmon/Data/", filter=filter):
        async for f in utils.list_dir_gen("/home/dreagonmon/", filter=filter):
        # async for f in utils.list_dir_gen("."):
            # print(f)
            lst.add(f)
            pass
        te = time.time_ns()
        # for f in lst: print(f)
        print("扫描到的文件数:", len(lst))
        print("花费时间:", (te - ts) / 1_000_000)

if __name__ == "__main__":
    asyncio.run(main())
