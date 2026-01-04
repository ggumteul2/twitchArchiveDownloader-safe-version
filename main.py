import functions as fn
import twitchAPI
import os
import sys

#url = "https://www.twitch.tv/videos/2654060514"
mode = input("Please choose the mode\n==============================\n0 : download archive by URL\n1 : download lastest archive by username\n==============================\n\n>> ")
match mode:
    case "0":
        url = input("Please enter url of Twitch archive (https://www.twitch.tv/videos/~)\n>> ")
        url = url.split("?")[0] 
    
    case "1":
        username = input("Please enter username of Twitch channel\n>> ")
        vid_id = twitchAPI.getLastestArchiveURL(username)
        url = "https://www.twitch.tv/videos/" + vid_id
        
    case _:
        print("please choose the correct mode")
        sys.exit(0)
        
ts_tamplet_url, end_num, channel_name, date, title, muted = twitchAPI.getTSURL(url)
print("checking pre-downloaded tsfiles")
archive_id = url.split("/videos/")[1].split("?")[0]

#名前を修正
downloader = fn.TSFilesDownloader(
    end_num=end_num,
    name=archive_id,
    url=ts_tamplet_url,
    dir=os.getcwd(),
    muted=muted,
    lim=15,
    date=date,
    channel_name=channel_name
)
downloader.download()