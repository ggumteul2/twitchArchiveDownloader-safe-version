import os
import shutil
import sys
import requests
from tqdm import tqdm
import asyncio
import aiohttp


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
        remove = input("이미 존재하는 폴더입니다. 덮어쓸까요? (y/n)\n>> ")
        if remove.lower() == "y":
            shutil.rmtree(f"{dir}/{name}")
    try:
        os.mkdir(f"{dir}/{name}")
    except PermissionError:
        print("권한이 부족합니다. 프로그램을 종료합니다")
        sys.exit(0)
    except Exception as e:
        print(f'예기치 않은 오류가 발생했습니다 : {e}. 프로그램을 종료합니다')
        sys.exit(0)

def downloadFile(file_name: str, url: str, dir: str):
    try:
        if os.path.isfile(f"{dir}/{file_name}"):
            init_pos = os.path.getsize(f"{dir}/{file_name}")
            resume_req_header = {'Range':'bytes={}-'.format(init_pos)}
        else:
            init_pos = 0
            resume_req_header = {'Range':'bytes=0-'}
        if init_pos >= int(requests.get(url).headers.get('Content-Length')):
            return
        with requests.get(url, stream=True, headers=resume_req_header) as req:
            total_size = int(req.headers.get('Content-Length')) + init_pos
            print(f"total size is {total_size} bytes")
            t = tqdm(total=total_size, unit="iB", unit_scale=True, leave=False, initial=init_pos)
            with open(f"{dir}/{file_name}", 'ab') as file:
                for chunk in req.iter_content(chunk_size = 8 * 1024):
                    file.write(chunk)
                    t.update(len(chunk))
    except Exception as e:
        print(e)

class TSFilesDownloader:
    def __init__(self, end_num: int, name: str, url: str, dir: str, lim: int = 5, start_num: int = 0):
        self.end_num = end_num
        self.name = name
        self.url = url
        self.dir = dir
        self.lim = lim
        self.start_num = start_num
        ts = list()
        for i in range(start_num, end_num + 1):
            ts.append(0)
        self.ts = ts
        makeFolder(name, dir)
        
        
        
    def tempUpdate(self):
        #임시파일 없으면 생성
        temp_dir = f"{self.dir}/{self.name}/temp.txt"
        if os.path.isfile(temp_dir) != True:
            text = ""
            for status in ts:
                text = text + f"\n{status}"
            with open(temp_dir, "w") as f:
                f.write(f"{self.start_num}\n{self.end_num}\n{self.name}\n{self.lim}" + text)
        
        #임시파일 읽기
        with open(temp_dir, "r") as f:
            temps = f.readlines()
        self.start_num = int(temps[0])
        self.end_num = int(temps[1])
        self.name = temps[2]
        self.lim = int(temps[3])
        ts = list()
        for i in range(0,len(temps)):
            if i <= 3:
                continue
            ts.extend(temps[i])
        self.ts = ts
    

def downloadTSFiles(end_num: int, name: str, url: str, dir: str, lim: int = 5, start_num: int = 0):
    
    
    
    
    for i in range(start_num,end_num):
        tsurl = url.replace('(*)', str(i))
        downloadFile(f"{i}.ts", tsurl, dir)

def main():
    name = input("만들 폴더의 이름을 입력해 주세요\n>> ")
    dir = input("만들 폴더의 경로를 입력해 주세요\n>> ")
    makeFolder(name, dir)

if __name__ == "__main__":
    main()
    
    