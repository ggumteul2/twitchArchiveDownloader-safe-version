import requests
import sys
import re
import functions as fn
app_token = "s5498lg7h36kk5ml7f7jgw180c9rp2"
client_id = "u1azns9tgoo4qkrtaj95mi4jkyj1dy"
#토큰 조회
#req = requests.get('https://id.twitch.tv/oauth2/validate', headers={"Authorization":f"Bearer {app_token}"})
#print(req.json())

full_url = input("트위치 다시보기의 url을 입력해 주세요\n>> ")
try:
    vid_id = full_url.split("/videos/")[1]
except:
    print("올바른 url을 입력해 주세요")
    sys.exit(0)

req = requests.get(f'https://api.twitch.tv/helix/videos?id={vid_id}', headers={"Authorization":f"Bearer {app_token}", "Client-Id":f"{client_id}"})
json_data = req.json()
thumbnail_url = json_data["data"][0]["thumbnail_url"]
title = json_data["data"][0]["title"]

if thumbnail_url == "https://vod-secure.twitch.tv/_404/404_processing_%{width}x%{height}.png":
    print("아직 처리중인 동영상입니다")
    sys.exit(0)
match = re.compile("https://static-cdn.jtvnw.net/cf_vods/d3vd9lfkzbru3h/[^/\t\n\r\f\v]*/").match(thumbnail_url)
if match == None:
    print("올바르지 않은 동영상입니다")
    sys.exit(0)

keyword = thumbnail_url.split("/")[5]
m3u8_url = "https://d3vd9lfkzbru3h.cloudfront.net/" + keyword + "/chunked/index-dvr.m3u8"


req = requests.get(m3u8_url)
length = len(re.compile("[0-9]*[.]ts").findall(req.text))