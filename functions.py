import os
import sys
import asyncio
import aiohttp
import aiofiles
import aiofiles.os
import ffmpeg
import shutil
from tqdm import tqdm

def nameConvert(name: str):
    if '\\' or '/' or ':' or '*' or '?' or '"' or '<' or '>' or '|' in name:
        name = name.replace('\\', '_')
        name = name.replace('/', '_')
        name = name.replace(':', '_')
        name = name.replace('*', '_')
        name = name.replace('?', '_')
        name = name.replace('<', '_')
        name = name.replace('>', '_')
        name = name.replace('|', '_')
    return name

def makeFolder(name: str, dir: str):
    name = nameConvert(name)
    if os.path.isdir(f"{dir}/{name}"):
        #remove = input("이미 존재하는 폴더입니다. 덮어쓸까요? (y/n)\n>> ")
        #if remove.lower() == "y":
        #    shutil.rmtree(f"{dir}/{name}")
        #else:
        #    return
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
    def __init__(self, end_num: int, name: str, url: str, dir: str, muted: list, lim: int = 5, start_num: int = 0, date = None, channel_name = None):
        self.end_num = end_num
        self.name = name
        self.url = url
        self.dir = dir
        self.lim = lim
        self.start_num = start_num
        self.working = True
        self.date = date
        self.channel_name = channel_name
        self.muted = muted
        self.ts = list()
        
        for i in range(start_num, end_num + 1):
            self.ts.append(i)
            if i == start_num:
                ts_text = i
                continue
            ts_text = f"{ts_text}\n{i}"
        
        #이미 다운로드가 끝났는지 확인
        if os.path.isfile(f"{dir}/{name}/{end_num}.ts"):
            self.concat()
        
        
            
        makeFolder(name, dir)
        #임시파일 생성
        if os.path.isfile(f"{dir}/{name}/temp.txt"):
            self.ts = list()
            with open(f"{dir}/{name}/temp.txt", "r") as f:
                ts = f.readlines()
                for index, value in enumerate(ts):
                    value = int(value)
                    if index == 0 and value != 0:
                        for i in range(0,self.lim):
                            if value - i - 1 < self.start_num:
                                continue
                            self.ts.append(value - i - 1)
                    self.ts.append(value)
            self.pbar = tqdm(range(start_num, end_num + 1), desc="Processing", initial=self.end_num - self.start_num + 1 - len(self.ts), unit="ts files")
            return
        self.pbar = tqdm(range(start_num, end_num + 1), desc="Processing", unit="ts files")
        try:
            with open(f"{dir}/{name}/temp.txt", "w") as f:
                f.write(ts_text)
        except PermissionError:
            print("insufficient privileges. Shutting down the program")
            sys.exit(0)
        except Exception as e:
            print(f'An unexpected error occurred: {e}. Shutting down the program')
            sys.exit(0)
    
    async def downloadFile(self, num: int):
        if await aiofiles.os.path.isfile(f"{self.dir}/{self.name}/{num}.ts"):
            await aiofiles.os.remove(f"{self.dir}/{self.name}/{num}.ts")
        
        
        async with aiohttp.ClientSession() as session:
            if f"{num}-unmuted.ts" in self.muted:
                requestURL = f"{self.url}{num}-muted.ts"
            else:
                requestURL = f"{self.url}{num}.ts"
            async with session.get(requestURL) as req:
                
                async with aiofiles.open(f"{self.dir}\\{self.name}\\{num}.ts", 'ab') as file:
                    async for chunk in req.content.iter_chunked(8 * 1024):
                        await file.write(chunk)
            #if f"{num}-unmuted.ts" in self.muted:
            ##    log = f"{num}-muted.ts download complete"
            ##else:
            ##    log = f"{num}.ts download complete"
            #print(log)
            self.pbar.update(1)
            ts_text = ""            
            for index, value in enumerate(self.ts):
                if index == 0:
                    ts_text = value
                    continue
                ts_text = f"{ts_text}\n{value}"
            if ts_text == "":
                return
            async with aiofiles.open(f"{self.dir}/{self.name}/temp.txt", "w") as f:
                await f.write(ts_text)
                #sys.exit(0)
    
    async def downloadTSFiles(self):
        semaphore = asyncio.Semaphore(self.lim)
        async with semaphore:
            while self.working:
                current = list()
                for i in range(0, self.lim):
                    try:
                        current.append(self.ts.pop(0))
                    except IndexError:
                        self.working = False
                        continue
                await asyncio.gather(*[self.downloadFile(int(index)) for index in current])
            if os.path.isfile(f"{self.dir}/{self.name}/temp.txt"):
                os.remove(f"{self.dir}/{self.name}/temp.txt")
            self.pbar.close()
            self.concat()

    def download(self):
        asyncio.run(self.downloadTSFiles())
    
    def concat(self):
        videoName = ""
        if self.channel_name != None:
            videoName = f"{videoName}[{self.channel_name}] "
        if self.date != None:
            videoName = f"{videoName}[{self.date}] "
        videoName = f"{videoName}{self.name}.mkv"
        self.ts = list()
        for i in range(self.start_num, self.end_num + 1):
            self.ts.append(f"file \'{self.dir}/{self.name}\'/{i}.ts\n")
        with open(f"{self.dir}/{self.name}/concat.txt", "w", encoding="utf-8") as f:
            f.writelines([inputs for inputs in self.ts])
        for i in range(self.start_num, self.end_num + 1):
            if f"{i}-unmuted.ts" in self.muted:
                continue
            ts_hasAudio = f"{i}.ts"
            ts_hasAudio = f"{self.dir}/{self.name}/{ts_hasAudio}"
            break
        for muted_ts in self.muted:
            ts_muted = muted_ts.split("-")[0]
            process_and_match_stream(f"{self.dir}/{self.name}/{ts_muted}.ts", f"{self.dir}/{self.name}/{ts_muted}-unmuted.ts", ts_hasAudio)
            os.remove(f"{self.dir}/{self.name}/{ts_muted}.ts")
            os.rename(f"{self.dir}/{self.name}/{ts_muted}-unmuted.ts", f"{self.dir}/{self.name}/{ts_muted}.ts")
                
        ffmpeg.input(f"{self.dir}/{self.name}/concat.txt", format="concat", safe=0).output(videoName, c="copy").run()
        delete_folder = input("Do you want to delete temporary folders? (y/n) >>\n")
        if delete_folder != "y":
            sys.exit(0)
        shutil.rmtree(f"{self.dir}/{self.name}")



#below 2 functions are generated by google gemini                
def get_reference_audio_info(ref_file):
    """기준 파일에서 첫 번째 오디오 스트림의 상세 정보를 추출합니다."""
    probe = ffmpeg.probe(ref_file)
    audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
    return audio_info

def process_and_match_stream(input_file, output_file, ref_file):
    # 1. 기준 파일의 오디오 정보 가져오기
    ref_audio = get_reference_audio_info(ref_file)
    if not ref_audio:
        return

    # 2. 입력 스트림 설정
    input_stream = ffmpeg.input(input_file)
    
    # 3. 기준 파일 순서(Audio:0, Video:1) 및 파라미터 강제 적용
    output = ffmpeg.output(
        input_stream['a:0'],  # Stream #0:0 (Audio)
        input_stream['v:0'],  # Stream #0:1 (Video)
        output_file,
        acodec=ref_audio['codec_name'],
        ar=ref_audio['sample_rate'],
        ac=ref_audio['channels'],
        vcodec='copy',
        map_metadata=-1
    ).overwrite_output()  # 오타 수정 완료

    # 4. 실행
    try:
        output.run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error:
        raise
    
    