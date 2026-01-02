import functions as fn
import twitchAPI
import os
import requests
import sys

url = "https://www.twitch.tv/videos/2654060514"

#url = input("Please enter url if Twitch archive (https://www.twitch.tv/videos/~)\n>> ")
ts_tamplet_url, end_num, channel_name, date, title, muted = twitchAPI.getTSURL(url)
print("checking pre-downloaded tsfiles")
title = fn.nameConvert(title)
channel_name = fn.nameConvert(channel_name)


downloader = fn.TSFilesDownloader(end_num, title, ts_tamplet_url, os.getcwd(), muted, 12, date=date, channel_name=channel_name)
downloader.download()