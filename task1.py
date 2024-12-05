import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile
import sys
from colorama import Fore, Style
from itertools import chain

async def main():
    try:
        if len(sys.argv) != 3:
            print(Fore.RED + "Incorrect number of arguments")
            print(Style.RESET_ALL + "usage: python task1.py source_dir target_dir")
            sys.exit(1)
        
        source_dir = AsyncPath(sys.argv[1])
        if not await source_dir.exists() or not await source_dir.is_dir():
            print(Fore.RED + "Source directory does not exist")
            sys.exit(2)

        target_dir = AsyncPath(sys.argv[2])
        if await target_dir.exists() and not await target_dir.is_dir():
            print(Fore.RED + "Target directory is a file")
            sys.exit(3)
        if not await target_dir.exists():
            await target_dir.mkdir(parents=True)
        
        await sort_files(source_dir, target_dir)
        print("Done!")

    except Exception as err:
        print (f"Unexprected error: {err}")
        sys.exit(9)
    finally:
        print (Style.RESET_ALL)

async def sort_files(source: AsyncPath, target: AsyncPath):
    content = source.iterdir()
    async for path in content:
        if await path.is_dir():
            await sort_files(path, target)
        else:
            await copy_file(path, target)

async def copy_file(source: AsyncPath, target: AsyncPath):
    suffix = source.suffix
    if not suffix:
        suffix = "NO_EXT"
    dest = AsyncPath(target, suffix)
    if not await dest.exists():
        await dest.mkdir()
    
    dest_file = AsyncPath(dest, source.name)
    if await dest.is_file() or await dest_file.exists():
        print(f'File {source.name} already exist, skipping')
        return
        
    await copyfile(source, dest_file)


if __name__ == '__main__':
    asyncio.run(main())