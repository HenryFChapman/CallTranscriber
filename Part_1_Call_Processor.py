
#Step 01 - Rename Calls
#Step 02 - Generate Slides in Calls
#Step 03 - Make MP4 Videos from Slides and Renamed Calls
#Step 04 - Combine All MP4 Videos into 1 Video
#Step 05 - Split Large Combination into Multiple Videos

from bs4 import BeautifulSoup
import os
import shutil

#Step 01 - Rename Calls
print("Starting to Rename Calls")

with open('index.html', 'r') as f:
	contents = f.read()
	soup = BeautifulSoup(contents, 'lxml')
	outputList = []

	table = soup.find_all('table')
	scrollTable = table[3]

	x = (len(scrollTable.findAll('tr')))
	for row in scrollTable.findAll('tr')[1:x]:
		innerField = []
		col = row.findAll('td')

		#Call Index
		index = col[2].getText()
		innerField.append(index)

		#File Name
		link = col[1].find('a').get('href')
		innerField.append(link)

		#Call Time
		call_time = col[4].getText()
		innerField.append(call_time)
		outputList.append(innerField)

newCallName = []
#This section of code creates a new folder for the copied calls. 
renamedCallsFolder = "Renamed Calls"
if os.path.exists(renamedCallsFolder):
	shutil.rmtree(renamedCallsFolder)
os.makedirs(renamedCallsFolder)

count=1
for innerList in outputList:
	for item in innerList:
		for filename in os.listdir():
			if filename == item:
				indexInt = int(innerList[0])
				formattedCallIndex = f"{indexInt:04}"
				dateNoColons = innerList[2].replace(":", "")
				formattedCallIndex = formattedCallIndex + " - " + dateNoColons
				shutil.copyfile(innerList[1], renamedCallsFolder + "\\" + formattedCallIndex +".mp3")
				count = count+1

print("Finished renaming calls")

#Step 02
#Create Slides from Calls
from PIL import Image, ImageDraw, ImageFont
from ffmpy import FFmpeg
 
print("Creating Placeholder Slides and Converting Video. This will take a long time.")

def text_on_img(filename, text, size=6, color=(255,255,0), bg='white'):
	fnt = ImageFont.truetype('arial.ttf', size)
	# create image
	image = Image.new(mode = "RGB", size = (int(size/2)*len(text),size+50), color = bg)
	draw = ImageDraw.Draw(image)
	# draw text
	draw.text((10,10), text, font=fnt, fill=(0,0,0))
	# save file
	image.save(filename)

Directory = renamedCallsFolder

imagesFolder = "Images"
if os.path.exists(imagesFolder):
	shutil.rmtree(imagesFolder)
os.makedirs(imagesFolder)

VideoDirectory = "Renamed Calls - Video"
if os.path.exists(VideoDirectory):
	shutil.rmtree(VideoDirectory)
os.makedirs(VideoDirectory)

for item in os.listdir(Directory):
	justFilename = item.split(".")[0]
	text = justFilename
	image = imagesFolder + "\\" + text+".jpg"
	text_on_img(image, text, size=75, color=(255,255,0), bg='white')


	audio = Directory + "\\" + item
	image = image

	ff = FFmpeg(
		inputs = {audio: None, image: '-loop 1' },
		outputs = {VideoDirectory+"\\" + text + ".mp4": '-c:a copy -c:v libx264 -shortest'}
		)
	ff.run()
print("Finished creating Placeholder Slides and Converting Video.")