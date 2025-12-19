import os
import shutil
import sys
import requests

def nameConvert(name):
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

def makeFolder(name, dir):
    name = nameConvert(name)
    if os.path.isdir(f"{dir}/{name}"):
        remove = input("이미 존재하는 폴더입니다. 덮어쓸까요? (y/n)\n>> ")
        if remove.lower() != "y":
            print("폴더가 이미 존재하여 프로그램을 종료합니다")
            sys.exit(0)
        shutil.rmtree(f"{dir}/{name}")
    try:
        os.mkdir(f"{dir}/{name}")
    except PermissionError:
        print("권한이 부족합니다. 프로그램을 종료합니다")
        sys.exit(0)
    except Exception as e:
        print(f'예기치 않은 오류가 발생했습니다 : {e}. 프로그램을 종료합니다')
        sys.exit(0)

def main():
    name = input("만들 폴더의 이름을 입력해 주세요\n>> ")
    dir = input("만들 폴더의 경로를 입력해 주세요\n>> ")
    makeFolder(name, dir)

if __name__ == "__main__":
    main()
    
    