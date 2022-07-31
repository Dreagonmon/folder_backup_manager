import asyncio, os, atexit
from concurrent.futures import ProcessPoolExecutor

_io_executor = ProcessPoolExecutor(os.cpu_count())
atexit.register(lambda: _io_executor.shutdown())
