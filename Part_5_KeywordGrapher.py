from matplotlib import pyplot as plt
import pandas as pd
import os
import shutil

def countKeywordsPerLine(dataset, dictionaryFilePath, analysisLocation):
	wordsInDictionary = set()
	with open(dictionaryFilePath, "r") as dictionaryFile:
		for word in enumerate(dictionaryFile):
			justWord = word[1]
			justWord = justWord.split("\n")[0]
			wordsInDictionary.add(justWord)
	dictionaryFile.close()

	wordsInDictionary = list(wordsInDictionary)


	allKeywords = []
	for i, row in dataset.iterrows():
		tempList = list( dict.fromkeys(row['keywordList'].split(",")))

		for item in tempList:
			allKeywords.append(item.strip())

	counts = []
	for word in wordsInDictionary:
		count = 0
		for keywordHit in allKeywords:
			if word == keywordHit:
				count = count + 1
		counts.append(count)

	result = []
	result.append(wordsInDictionary)
	result.append(counts)
	return result

def hitsPerDay(KeywordSummary, dictionaryFilePath, analysisLocation):
	histogramOfDates = KeywordSummary.groupby(KeywordSummary["callDates"]).count()
	histogramOfDates = histogramOfDates.reset_index()
	dateHistogramOutput = pd.DataFrame()
	hitsPerKeyword(KeywordSummary, dictionaryFilePath, analysisLocation)
	dateHistogramOutput['callDates'] = histogramOfDates['callDates']
	dateHistogramOutput['count'] = histogramOfDates['CallIndex']
	dateHistogramOutput.to_excel(analysisLocation+"\\dateHistogramOutput.xlsx", encoding = 'utf-8', index = False)

def hitsPerCall(KeywordSummary, dictionaryFilePath, analysisLocation):
	histogramOfCalls = KeywordSummary.groupby(KeywordSummary["CallIndex"]).count()
	histogramOfCalls = histogramOfCalls.reset_index()

	callHistogramOutput = pd.DataFrame()
	callHistogramOutput['CallIndex'] = histogramOfCalls['callDates']
	callHistogramOutput['count'] = histogramOfCalls['CallIndex']

	callHistogramOutput.to_excel(analysisLocation+"\\callHistogramOutput.xlsx", encoding = 'utf-8', index = False)

def hitsPerKeyword(KeywordSummary,dictionaryFilePath, analysisLocation):
	#This Section of Code Loads a List that is a Dictionary
	result = countKeywordsPerLine(KeywordSummary, dictionaryFilePath, analysisLocation)
	hitsPerKeyword = pd.DataFrame()
	hitsPerKeyword['wordsInDictionary'] = result[0]
	hitsPerKeyword['counts'] = result[1]
	hitsPerKeyword = hitsPerKeyword.sort_values(by='counts', ascending=False)

	hitsPerKeyword.to_excel(analysisLocation+"\\hitsPerKeyword.xlsx", encoding = 'utf-8', index = False)

	return hitsPerKeyword


def worldCloud():
	return None 


def mainDataVisualization():
	spreadsheetLocation = "KeywordSummary.xlsx"
	KeywordSummary = pd.read_excel(spreadsheetLocation)
	dictionaryFilePath = "JailCallDictionary.txt"
	analysisLocation = "AnalysisDirectory\\"

	if os.path.exists(analysisLocation):
		shutil.rmtree(analysisLocation)
	os.makedirs(analysisLocation)


	hitsPerDay(KeywordSummary, dictionaryFilePath, analysisLocation)
	hitsPerCall(KeywordSummary, dictionaryFilePath, analysisLocation)