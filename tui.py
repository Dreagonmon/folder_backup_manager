import asyncio, atexit, math
from concurrent.futures import ThreadPoolExecutor
from typing import List

PAGE_SIZE = 10

_io_executor = ThreadPoolExecutor(1)
atexit.register(lambda: _io_executor.shutdown())

async def async_input(prompt: str = "") -> str:
    return await asyncio.get_event_loop().run_in_executor(_io_executor, input, prompt)

async def select(message: str, options: List[str]) -> int:
    page_size = len(options)
    page_count = math.ceil(page_size / PAGE_SIZE)
    if page_count > 1:
        print("================")
        print("||: '>' Last page. '<' means 1 page, '<<' means 2 pages.")
        print("||: '<' Next page. '>' means 1 page, '>>' means 2 pages.")
    pages = 0
    while True:
        print("================")
        print(message)
        print("================")
        if page_count > 1: print("|| PAGE {}/{} ||".format(pages+1, page_count))
        for i in range(pages*PAGE_SIZE, pages*PAGE_SIZE+PAGE_SIZE):
            if i >= page_size:
                break
            print("{:> 4d}: {}".format(i, options[i]))
        num_sel = await async_input("> ")
        print()
        if num_sel.startswith("<"):
            pages -= num_sel.count("<")
            if pages < 0:
                pages = 0
        elif num_sel.startswith(">"):
            pages += num_sel.count(">")
            if pages >= page_count:
                pages = page_count - 1
        else:
            try:
                num = int(num_sel)
            except: continue
            if num >= 0 and num < page_size:
                return num
