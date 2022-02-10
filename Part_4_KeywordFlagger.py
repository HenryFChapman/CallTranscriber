import os
import shutil
import pandas as pd
from ffmpy import FFmpeg
import pytesseract
from PIL import Image
import re

TranscriptsLocation = "Calls\\CallTranscripts\\"
dictionaryFilePath = "JailCallDictionary.txt"
EditedTranscriptsLocation = "Calls\\EditedJailCallTranscripts\\"


def make_hyperlink(value):
    text = "Calls\\Folder Of Big Videos\\" + value
    return '=HYPERLINK("%s", "%s")' % (text, "Link")

def returnDateOfCall(dataset):
	outputFilePath = "Calls\\Screenshots\\"

	callIndexes = []
	callDates = []
	callTimes = []

	for i, row in dataset.iterrows():
		if os.path.exists(outputFilePath):
			shutil.rmtree(outputFilePath)
		os.makedirs(outputFilePath)

		fileName = 'Calls\\Folder Of Big Videos\\' + row['SourceFile']
		timeStamp = row['timeStamps']

		ff = FFmpeg(
			inputs = {fileName: '-ss ' + timeStamp },
			outputs = {outputFilePath + 'image.jpg': " -vframes 1 -q:v 10 -loglevel quiet"}
		)
		ff.run()

		img = Image.open(outputFilePath + 'image.jpg')
		pytesseract.pytesseract.tesseract_cmd ='C:/Program Files/Tesseract-OCR/tesseract.exe'
		result = pytesseract.image_to_string(img)
		callIndexes.append(result.split(" - ")[0])
		callDates.append(result.split(" - ")[1].split(" ")[0])
		callTimes.append(result.split(" - ")[1].split(" ")[1])

		print(i)
		img.close()

	dataset['CallIndex'] = callIndexes
	dataset['callDates'] = callDates
	dataset['CallTimes'] = callTimes

def flagKeywords():
	if os.path.exists(EditedTranscriptsLocation):
		shutil.rmtree(EditedTranscriptsLocation)
	os.makedirs(EditedTranscriptsLocation)

	lines = []

	cleanTranscripts()

	#This Section of Code Loads a List that is a Dictionary
	wordsInDictionary = set()
	with open(dictionaryFilePath, "r") as dictionaryFile:
		for word in enumerate(dictionaryFile):
			justWord = word[1]
			justWord = justWord.split("\n")[0]
			wordsInDictionary.add(justWord)
	dictionaryFile.close()
	wordsInDictionary = list(wordsInDictionary)


	#This Section of Code Reads Transcripts
	summaryFiles = []
	sourceFiles = []
	timeStamps = []
	lineContents = []
	keywords = []
	helperColumn = []

	for file in os.listdir(EditedTranscriptsLocation):
		linesInFile = []

		with open(EditedTranscriptsLocation+file, "r") as f:
			for line in f:
				lineNoSpace = line.split("\n")[0]
				if "No transcripts are availible for" not in line:

					justWords = lineNoSpace.split(" - ")[1]
					justWords = justWords.split(" ")
				else:
					continue

				for word in justWords:
					for entry in wordsInDictionary:
						if word == entry:
							lineNoSpace = lineNoSpace + " - RELEVANT KEYWORD - " + entry

							summaryLineToAppend = file + " - " + lineNoSpace
							summaryFiles.append(summaryLineToAppend + "\n")

				linesInFile.append(lineNoSpace + "\n")

			f.close()

		#This Section of Code Writes Transcripts
		f = open(EditedTranscriptsLocation+file, "w")
		for line in linesInFile:
			f.write(line)
		f.close()


	#This Section of Code Writes a Summary File
	keywordSummaryDataFrame = pd.DataFrame()

	for summary in summaryFiles:
		#Append File Name - Add MP4 To it
		videoFile = summary.split(" - ")[0].split(".")[0] + ".mp4"
		videoFile = videoFile[:9] + '-' + videoFile[10:]
		sourceFiles.append(videoFile)

		#Add Time Stamp
		timeStamp = summary.split(" - ")[1]
		timeStamps.append(timeStamp)

		helperColumn.append(videoFile + " - " + timeStamp)

		#Add Text
		lineContent = summary.split(" - ")[2]
		lineContents.append(lineContent)

		#Add Keyword
		keywordList = summary.split(" - RELEVANT KEYWORD - ")

		keyword = ""
		if len(keywordList)==2:
			keyword = keywordList[1].split("\n")[0]
		if len(keywordList)==3:
			keyword = keywordList[1] + ", " + keywordList[2].split("\n")[0]
		if len(keywordList)==4:
			keyword = keywordList[1] + ", " + keywordList[2] + ", " + keywordList[3].split("\n")[0]
		if len(keywordList)==5:
			keyword = keywordList[1] + ", " + keywordList[2] + ", " + keywordList[3] + ", " + keywordList[4].split("\n")[0]
		if len(keywordList)==6:
			keyword = keywordList[1] + ", " + keywordList[2] + ", " + keywordList[3] + ", " + keywordList[4] + ", "+ keywordList[5].split("\n")[0]
		if len(keywordList)==7:
			keyword = keywordList[1] + ", " + keywordList[2] + ", " + keywordList[3] + ", " + keywordList[4] +", " + keywordList[5] + ", "+ keywordList[6].split("\n")[0]
		keywords.append(keyword)

	keywordSummaryDataFrame['SourceFile'] = sourceFiles
	keywordSummaryDataFrame['timeStamps'] = timeStamps
	keywordSummaryDataFrame['lineContents'] = lineContents
	keywordSummaryDataFrame['keywordList'] = keywords
	keywordSummaryDataFrame['helperColumn'] = helperColumn
	keywordSummaryDataFrame['LinkToOriginal'] = keywordSummaryDataFrame['SourceFile'].apply(lambda x: make_hyperlink(x))

	keywordSummaryDataFrame = keywordSummaryDataFrame.drop_duplicates(['helperColumn'], keep="last")
	keywordSummaryDataFrame = keywordSummaryDataFrame.drop(columns=['helperColumn'])

	returnDateOfCall(keywordSummaryDataFrame)

	keywordSummaryDataFrame.to_excel("KeywordSummary.xlsx", encoding = 'utf-8', index = False)

def cleanTranscripts():

	regexp = re.compile(r'\d{1}:\d{2}:\d{2} - ')

	for file in os.listdir(TranscriptsLocation):
		i = 0
		lines = []

		with open(TranscriptsLocation+file, "r") as f:
			lastLine = ""

			for line in f:
				if "No transcripts are availible for"  in line:
					continue

				if bool(re.search(regexp, line))==False:
					ammendedLine = lines[i-1].replace('\n', '') + " " + line
					lines.append(ammendedLine)
				else:
					lines.append(line)
				i = i + 1

			timeStamps = []
			content = []

			for line in lines:
				timeStamps.append(line.split(" - ")[0])
				content.append(line.split(" - ")[1])

			tempDataFrame = pd.DataFrame()
			tempDataFrame['timeStamps'] = timeStamps
			tempDataFrame['content'] = content
			tempDataFrame['lines'] = lines
			tempDataFrame = tempDataFrame.drop_duplicates(subset ='timeStamps', keep='last')

			content = []
			for i, row in tempDataFrame.iterrows():
				content.append(row['lines'])
			f = open(EditedTranscriptsLocation+file, "w")
			for line in content:
				f.write(line)
			f.close()