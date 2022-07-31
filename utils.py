import os, sys, asyncio, shlex, shutil, atexit
from typing import Optional, Tuple, List, Union, Callable, Generator
from concurrent.futures import ThreadPoolExecutor

_io_executor = ThreadPoolExecutor(os.cpu_count() * 2)
atexit.register(lambda: _io_executor.shutdown())

_input_lock = asyncio.Lock()
_encoding = sys.getdefaultencoding()
_join = os.path.join
_isdir = os.path.isdir
_stat = os.stat

def _unix_join_1(pt: str, *pts):
    if pt.endswith("/"):
        return pt + "/".join(pts)
    else:
        return pt + "/" + "/".join(pts)

async def shell(cmd: Union[str, List[str]], cwd: str = None) -> Tuple[asyncio.subprocess.Process, bytes, bytes]:
    if not isinstance(cmd, str):
        cmd = shlex.join(cmd)
    if cwd == None:
        cwd = os.getcwd()
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )
    stdout, stderr = await proc.communicate()
    return proc, stdout, stderr

async def async_input(prompt: str = "") -> str:
    async with _input_lock:
        return await asyncio.get_event_loop().run_in_executor(_io_executor, input, prompt)

# List dir
class FileItem:
    def __init__(self, path: str, is_dir: bool, mtime: int, size: int):
        self.path = path
        self.is_dir = is_dir
        self.mtime = mtime
        self.size = size
    
    def __hash__(self) -> int:
        return hash(self.path)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, FileItem):
            if (self.path == other.path):
                if self.is_dir and other.is_dir:
                    return True
                if self.is_dir == other.is_dir and self.mtime == other.mtime and self.size == other.size:
                    return True
        return False
    
    def __repr__(self) -> str:
        return f"FileItem({self.path}, {self.is_dir}, {self.mtime}, {self.size})"

async def list_dir_gen(tree_root: str, rel_path: str = "", base: str = "/", *, filter: Callable[[str], Optional[bool]] = lambda _: False, follow_link=False) -> Generator[FileItem, None, None]:
    if filter(base):
        return
    ignore_path: set[str] = set()
    if await is_git_dir(tree_root):
        for f in await list_git_ignored_files(tree_root):
            ignore_path.add(_join(rel_path, f))
    try:
        with os.scandir(tree_root) as it:
            for entry in it:
                name, is_dir, is_file = entry.name, entry.is_dir(follow_symlinks=follow_link), entry.is_file(follow_symlinks=True)
                item_path = _join(rel_path, name)
                if is_dir:
                    yield FileItem(item_path, True, 0, 0)
                    async for file in list_dir_gen(_join(tree_root, name), item_path, _unix_join_1(base, name), filter=filter, follow_link=follow_link):
                        if file.path in ignore_path:
                            continue
                        yield file
                elif is_file:
                    if filter(_unix_join_1(base, name)):
                        continue
                    if item_path in ignore_path:
                        continue
                    stat = _stat(_join(tree_root, name))
                    yield FileItem(item_path, False, int(stat.st_mtime), stat.st_size)
    except (FileNotFoundError, PermissionError): pass

# command line wraper
GIT = shutil.which("git")

async def is_git_dir(tree_root: str) -> bool:
    try:
        if not _isdir(_join(tree_root, ".git")): return False
    except (FileNotFoundError, PermissionError): return False
    try:
        result = await shell([GIT, "rev-parse", "--is-inside-work-tree"], tree_root)
        return result[1].strip().lower() == b"true"
    except (FileNotFoundError, PermissionError):
        return False

async def list_git_ignored_files(tree_root: str) -> List[str]:
    try:
        result = await shell([GIT, "ls-files", "-oi", "--exclude-standar"], tree_root)
        tmp = [ line.strip() for line in result[1].decode(_encoding).split("\n") ]
        return list(filter(lambda i: True if i else False, tmp))
    except (FileNotFoundError, PermissionError):
        return []
