import requests
import sys
import re
import functions as fn
import json

app_token = "s5498lg7h36kk5ml7f7jgw180c9rp2"
client_id = "u1azns9tgoo4qkrtaj95mi4jkyj1dy"

def getTSURL(url: str) -> tuple[str, int, str, str, str, list[str]]:
    try:
        # URLパラメータ(?以降)を除去
        vid_id = url.split("/videos/")[1].split("?")[0]
    except:
        print("Please enter correct url")
        sys.exit(0)
    
    req = requests.get(f'https://api.twitch.tv/helix/videos?id={vid_id}', headers={"Authorization":f"Bearer {app_token}", "Client-Id":f"{client_id}"})
    json_data = req.json()
    try:
        thumbnail_url = json_data["data"][0]["thumbnail_url"]
        title = json_data["data"][0]["title"]
        date = json_data["data"][0]["created_at"].split("T")[0]
        channel_name = json_data["data"][0]["user_name"]
    except IndexError:
        print("Network Error")
        sys.exit(0)

    if thumbnail_url == "https://vod-secure.twitch.tv/_404/404_processing_%{width}x%{height}.png":
        print("This video is still on processing")
        sys.exit(0)
    match = re.compile("https://static-cdn.jtvnw.net/cf_vods/d3vd9lfkzbru3h/[^/\t\n\r\f\v]*/").match(thumbnail_url)
    if match == None:
        print("Incorrect video")
        sys.exit(0)

    keyword = thumbnail_url.split("/")[5]
    m3u8_url = "https://d3vd9lfkzbru3h.cloudfront.net/" + keyword + "/chunked/index-dvr.m3u8"

    req = requests.get(m3u8_url)
    muted = list()
    muted = re.compile("[0-9]*-unmuted.ts").findall(req.text)
    length = len(re.compile("[0-9]*[.]ts").findall(req.text))
    return "https://d3vd9lfkzbru3h.cloudfront.net/" + keyword + "/chunked/", length - 1 , fn.nameConvert(channel_name), date, fn.nameConvert(title), muted

def getLastestArchiveURL(username: str) -> str:
    req = requests.get(f'https://api.twitch.tv/helix/users?login={username}', headers={"Authorization":f"Bearer {app_token}", "Client-Id":f"{client_id}"})
    try:
        user_id = req.json()["data"][0]["id"]
    except IndexError:
        print("Network Error or Incorrect username")
        sys.exit(0)
    req = requests.get(f'https://api.twitch.tv/helix/videos?user_id={user_id}&type=archive', headers={"Authorization":f"Bearer {app_token}", "Client-Id":f"{client_id}"})

    try:
        json_data = req.json()["data"]
    except IndexError:
        print("Network Error")
        sys.exit(0)

    try:
        video_id = json_data[0]["id"]
    except IndexError:
        print("There are no archives left")
        sys.exit(0)
    return video_id

if __name__ == "__main__":
    full_url = input("Please enter url if Twitch archive (https://www.twitch.tv/videos/~)\n>> ")
    ts_url, end_num, channel_name, date, title = getTSURL(full_url)
    print(f"{ts_url}\n{end_num}\n{channel_name}\n{date}\n{title}")