It's the safe version of twitchArchiveDownloader which is for pc that does not supports languages which are not English
If you don't have to use safe version, please use the standard version(https://github.com/ggumteul2/twitchArchiveDownloader)

1. Install Python
2. Open terminal and enter "pip install -r requirements.txt"
3. Install ffmpeg(https://www.ffmpeg.org/download.html)
4. add ffmpeg/bin folder to environment variable "Path"
5. open "start.cmd" and enter the twitch archive url or twitch username
6. You can change a download speed by changing "lim" parameter of TSFilesDownloader in main.py
7. After the download, I recommend you to remove temporary folders (which contains ts files)
