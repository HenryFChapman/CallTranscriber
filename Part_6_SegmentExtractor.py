import pandas as pd
import os
import shutil
from ffmpy import FFmpeg
import datetime
from datetime import timedelta

segmentsLocation = "Calls\\CallPreviews\\"
spreadsheetLocation = "KeywordSummary.xlsx"
TD0 = datetime.timedelta(0)

def make_hyperlink(value):
    text = "Calls\\CallPreviews\\" + value
    return '=HYPERLINK("%s", "%s")' % (text, "Link")

def segmentExtractor():
	#Makes Folder for Call Segments
	if os.path.exists(segmentsLocation):
		shutil.rmtree(segmentsLocation)
	os.makedirs(segmentsLocation)

	KeywordSummary = pd.read_excel(spreadsheetLocation)
	KeywordSummary['timeStamps2'] = pd.to_timedelta(KeywordSummary['timeStamps'])
	one_minute = datetime.timedelta(minutes=1)
	startTime = []
	cutSampleLocations = []

	for i, row in KeywordSummary.iterrows():
		if (row['timeStamps2'] - one_minute) >= TD0:
			startTime.append(row['timeStamps2'] - one_minute)
		else:
			startTime.append(TD0)

	KeywordSummary['startTime'] = startTime

	for i, row in KeywordSummary.iterrows():
		timeStamp = row['timeStamps']
		startTime = str(row['startTime']).split(" ")[2]

		fileName = "Calls\\Folder of Big Videos\\" + row['SourceFile']
		cutSampleLocation = segmentsLocation + "\\relevantSection"+str(i).zfill(4) + ".mp4"
		cutSampleLocations.append("relevantSection"+str(i).zfill(4) + ".mp4")

		ff = FFmpeg(
			inputs = {fileName: '-ss ' + startTime},
			outputs = {cutSampleLocation: " -t 00:02:00 -c copy -loglevel quiet"}
		)

		ff.run()
		print(ff.cmd)

	KeywordSummary['sampleLocation'] = cutSampleLocations
	KeywordSummary = KeywordSummary.drop(columns=['timeStamps2'])
	KeywordSummary = KeywordSummary.drop(columns=['LinkToOriginal'])
	KeywordSummary = KeywordSummary.drop(columns=['startTime'])
	KeywordSummary['LinkToCutSample'] = KeywordSummary['sampleLocation'].apply(lambda x: make_hyperlink(x))
	KeywordSummary = KeywordSummary.drop(columns=['sampleLocation'])

	KeywordSummary = KeywordSummary[['CallIndex', 'callDates','CallTimes','lineContents', 'keywordList', 'SourceFile', 'timeStamps', 'LinkToCutSample']]
	KeywordSummary.to_excel("KeywordSummary.xlsx", encoding = 'utf-8', index = False)
