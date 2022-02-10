from __future__ import unicode_literals
import youtube_dl
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import timedelta
import os
import shutil

def downloadTranscript(ydl_outs, playlistUrls, cookie):
	outputFilePath = "Calls\\CallTranscripts\\"

	if os.path.exists(outputFilePath):
		shutil.rmtree(outputFilePath)
	os.makedirs(outputFilePath)

	for playlistUrl in playlistUrls:
		with youtube_dl.YoutubeDL(ydl_outs) as ydl:
			extraInfo = ydl.extract_info(playlistUrl, download=False)

		videos = extraInfo['entries']
		videoTitles = []
		videoIDs = []

		for video in videos:
			vidTitle = video['title']
			videoTitles.append(vidTitle)
			vidID = video['id']
			videoIDs.append(vidID)

		i = 0
		blankTranscripts = []

		for transcript in videoIDs:
			try:
				transcript = YouTubeTranscriptApi.get_transcript(transcript, cookies=cookie)
				text_file = open(outputFilePath + videoTitles[i]+".txt", "w")

				for item in transcript:
					text = item['text']
					startTime = float(item['start'])
					startTime = timedelta(seconds=startTime)
					startTime = str(startTime)
					startTime = startTime.split(".")
					startTime = startTime[0]
					line = startTime + " - " + text + '\n'
					n = text_file.write(line)
				text_file.close()

			except:
				print("No transcripts are availible for " + videoTitles[i])
				text_file = open(outputFilePath + videoTitles[i]+".txt", "w")
				n = text_file.write("No transcripts are availible for " + videoTitles[i])
				blankTranscripts.append('I')
				text_file.close()
			i = i + 1
			
		print("You had " + str(len(blankTranscripts)))