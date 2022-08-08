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
import os, sys, asyncio, re
from typing import List, Callable
APP_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, APP_ROOT) # ensure import path
os.chdir(APP_ROOT)
import items, utils, tui

def make_filter_function(excludes: List[str], includes: List[str]) -> Callable[[str], bool]:
    re_excludes = [ re.compile(rule) for rule in excludes ]
    re_includes = [ re.compile(rule) for rule in includes ]
    def _filter_(path: str):
        for pt in re_excludes:
            if pt.match(path):
                for pti in re_includes:
                    if pti.match(path):
                        return True
                return False
        return True
    return _filter_

async def main():
    cfg = items.get_config()
    sel = await tui.select("Please choose an item.", [ i.name for i in cfg.backup_items ])
    backup_item = cfg.backup_items[sel]
    # select path
    source_path_list, backup_path_list = backup_item.get_matched_folders()
    if len(source_path_list) > 1:
        sel = await tui.select("Please choose a source path.", source_path_list)
        source_path = source_path_list[sel]
    elif len(source_path_list) <= 0:
        if len(backup_item.source_folders) <= 0:
            print("Please configure the source folders.")
            return
        sel = await tui.select("Please choose a source folder to create.", backup_item.source_folders)
        source_path = backup_item.source_folders[sel]
    else:
        source_path = source_path_list[0]
    if len(backup_path_list) > 1:
        sel = await tui.select("Please choose a backup path.", backup_path_list)
        backup_path = backup_path_list[sel]
    elif len(backup_path_list) <= 0:
        if len(backup_item.backup_folders) <= 0:
            print("Please configure the backup folders.")
            return
        sel = await tui.select("Please choose a backup folder to create.", backup_item.backup_folders)
        backup_path = backup_item.backup_folders[sel]
    else:
        backup_path = backup_path_list[0]
    # select action
    sel = await tui.select("What do you want to do?", ["Backup", "Restore"])
    from_path = source_path if sel == 0 else backup_path
    to_path = backup_path if sel == 0 else source_path
    # do action
    filter = make_filter_function(backup_item.excludes, backup_item.includes)
    to_delete = []
    to_copy = []
    errors = set()
    async for stage, count, total, info in utils.backup_files(from_path, to_path, filter):
        if stage == utils.BackupProgressStage.ERROR:
            errors.add(info)
        elif stage == utils.BackupProgressStage.TO_DELETE:
            to_delete.append(info)
        elif stage == utils.BackupProgressStage.TO_COPY:
            to_copy.append(info)
        elif stage == utils.BackupProgressStage.COMPAREED:
            print()
            if len(to_delete) > 0:
                await tui.select("The following files will be deleted:", to_delete)
            if len(to_copy) > 0:
                await tui.select("The following files will be copied:", to_copy)
            if len(to_delete) > 0 or len(to_copy) > 0:
                sel = await tui.select("Do you want to continue?", ["No, stop", "Yes, continue"])
                if sel == 0:
                    break
        print(f"{stage.name} || <{count}/{total}> || {info}")
    if len(errors) > 0:
        print("The following files failed:")
        for f in errors:
            print(f)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
