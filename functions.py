import os
import sys
import asyncio
import aiohttp
import aiofiles
import aiofiles.os
import ffmpeg
import shutil
import re
from datetime import datetime
from tqdm import tqdm

def nameConvert(name: str):
    if name is None:
        return ""
    return re.sub(r'[^0-9a-zA-Z._-]', '_', name)

def makeFolder(name: str, dir: str):
    if os.path.isdir(f"{dir}/{name}"):
        return
    try:
        os.mkdir(f"{dir}/{name}")
    except PermissionError:
        print("insufficient privileges. Shutting down the program")
        sys.exit(0)
    except Exception as e:
        print(f'An unexpected error occurred: {e}. Shutting down the program')
        sys.exit(0)


class TSFilesDownloader:
    def __init__(
        self,
        end_num: int,
        name: str,
        url: str,
        dir: str,
        muted: list,
        lim: int = 5,
        start_num: int = 0,
        date=None,
        channel_name=None
    ):
        self.end_num = end_num
        self.start_num = start_num
        self.url = url
        self.dir = dir
        self.lim = lim
        self.working = True
        self.date = date
        self.channel_name = channel_name
        self.muted = muted
        self.ts = list()

        # ==== フォルダ名を「日付_配信ID」に固定 ====
        safe_date = self.date.replace("-", "") if self.date else datetime.now().strftime("%Y%m%d")
        self.name = f"{safe_date}_{name}"

        makeFolder(self.name, self.dir)

        # TS番号リスト作成
        for i in range(start_num, end_num + 1):
            self.ts.append(i)

        # 途中再開チェック
        if os.path.isfile(f"{self.dir}/{self.name}/{end_num}.ts"):
            self.concat()
            return

        self.pbar = tqdm(
            range(start_num, end_num + 1),
            desc="Processing",
            unit="ts files"
        )

    async def downloadFile(self, num: int):
        file_path = f"{self.dir}/{self.name}/{num}.ts"

        if await aiofiles.os.path.isfile(file_path):
            await aiofiles.os.remove(file_path)

        async with aiohttp.ClientSession() as session:
            requestURL = (
                f"{self.url}{num}-muted.ts"
                if f"{num}-unmuted.ts" in self.muted
                else f"{self.url}{num}.ts"
            )
            async with session.get(requestURL) as req:
                async with aiofiles.open(file_path, "ab") as file:
                    async for chunk in req.content.iter_chunked(8 * 1024):
                        await file.write(chunk)

        self.pbar.update(1)

    async def downloadTSFiles(self):
        semaphore = asyncio.Semaphore(self.lim)
        async with semaphore:
            while self.ts:
                current = []
                for _ in range(self.lim):
                    if not self.ts:
                        break
                    current.append(self.ts.pop(0))
                await asyncio.gather(*[self.downloadFile(i) for i in current])

        self.pbar.close()
        self.concat()

    def download(self):
        asyncio.run(self.downloadTSFiles())

    def concat(self):
        videoName = ""
        if self.channel_name:
            videoName += f"[{self.channel_name}] "
        if self.date:
            videoName += f"[{self.date}] "
        videoName += f"{self.name}.mkv"

        concat_path = f"{self.dir}/{self.name}/concat.txt"

        with open(concat_path, "w", encoding="utf-8") as f:
            for i in range(self.start_num, self.end_num + 1):
                path = f"{self.dir}/{self.name}/{i}.ts"
                f.write(f"file {path}\n")

        ffmpeg.input(
            concat_path,
            format="concat",
            safe=0
        ).output(
            videoName,
            c="copy"
        ).run(overwrite_output=True)

        delete_folder = input("Do you want to delete temporary folders? (y/n) >> ")
        if delete_folder == "y":
            shutil.rmtree(f"{self.dir}/{self.name}")