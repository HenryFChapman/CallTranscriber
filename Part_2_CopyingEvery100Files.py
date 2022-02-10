import shutil
import os
import math
from ffmpy import FFmpeg

outerNestedFolder = "Calls\\Folder Of Big Videos"

def moveSetsOfCalls(numberOfFilesPerFolder):
	VideoDirectory = "Calls\\Renamed Calls - Video"
	numberOfFolders = math.ceil(len(os.listdir(VideoDirectory))/numberOfFilesPerFolder)

	#Make Outer Folder

	if os.path.exists(outerNestedFolder):
		shutil.rmtree(outerNestedFolder)
	os.makedirs(outerNestedFolder)

	#Make Inner Folders
	for i in range(1, numberOfFolders+1):
		renamedCallsFolder = "Calls\\Chunk" + str(i).zfill(3)
		
		if os.path.exists(outerNestedFolder + "\\" + renamedCallsFolder):
			shutil.rmtree(outerNestedFolder + "\\" + renamedCallsFolder)
		os.makedirs(outerNestedFolder + "\\" + renamedCallsFolder)

	#Move Sets of 100 files to new folders
	fileCount = 0

	for i in range(1, numberOfFolders+1):
		fileCount = fileCount + 1	
		numberOfFilesToGrabInEachChunk = fileCount*numberOfFilesPerFolder

		for file in os.listdir(VideoDirectory):
			numberOfFile = int(file.split(" ")[0])

			if numberOfFile <= numberOfFilesToGrabInEachChunk and numberOfFile > numberOfFilesToGrabInEachChunk-numberOfFilesPerFolder:
				shutil.copyfile(VideoDirectory + "\\" + file, outerNestedFolder + "\\Chunk" + str(i) + "\\" + file)

def concatenateIndividualChunks():
	#Loop Through Inner Folders
	for folder in os.listdir(outerNestedFolder):
		allFiles = ""

		for filename in os.listdir(outerNestedFolder + "\\" + folder):
			line =  "file '" + outerNestedFolder + "\\" + folder + "\\" + filename + "'" +"\n"
			allFiles =  allFiles + line

		textDirectory = outerNestedFolder + "\\" + folder+"\\"+"myfile.txt"
		file1 = open(textDirectory,"w") 
		file1.write(allFiles)
		file1.close()

		#Concatenates all the Video Files
		ff = FFmpeg(
			inputs = {textDirectory: '-f concat -safe 0' },
			outputs = {outerNestedFolder + "\\" + folder + ".mp4": '-c copy'}
			)
		ff.run()
		print("Finished Combining All Video Files Into for " + folder)

		shutil.rmtree(outerNestedFolder + "\\" + folder)

		print(folder)

def splitChunksIntoEvenSegments(hoursPerSegment):
	#Loop Through Each Chunk and Split it Up into 2-Hour Segments
	for largeVideo in os.listdir(outerNestedFolder):
		largeVideoJustName = largeVideo.split(".")[0]

		ff = FFmpeg(
			inputs = {outerNestedFolder+"\\"+largeVideo: None},
			outputs = {outerNestedFolder + "\\" + largeVideoJustName+'-%0d.mp4':"-c copy -map 0 -segment_time 0" + str(hoursPerSegment) + ":00:00 -f segment -reset_timestamps 1"}
			)
		ff.run()
		print(largeVideo)
		os.remove(outerNestedFolder+"\\"+largeVideo)