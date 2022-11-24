from pytube import YouTube,Playlist
from pytube.cli import on_progress
import ffmpeg
import sys
import os
import traceback


resPriority = [
	"4320p",
	"2160p",
	"1440p",
	"1080p",
	"720p",
	"480p",
	"360p",
	"240p",
	"144p",
]

#abrPriority = [
#	"320kbps"
#	"192kbps"
#	"160kbps",
#	"128kbps",
#	"70kbps",
#	"50kbps",
#	"48kbps",
#]

videoMimeTypes = [
	"video/3gpp",
	"video/webm",
	"video/mp4"
]

audioMimeTypes = [
	"audio/webm",
	"audio/mp4"
]




def downloadFile(streams,path,fileName):

	def normilizeFileName(fileName):
		excludeChars = ['\\' , '/' , ':' , '*' , '?' , '"' , '<' , '>' , '|'];
		#return "".join(x for x in fileName if x.isalnum() or x == ' ' or x == '-' or x == '_' or x == '#' or x == '.' or x == '+')
		return "".join(x for x in fileName if excludeChars.count(x) == 0)

	def getVideoBestSteamFrom(streams):
		global videoMimeTypes,resPriority


		filteredStreams = []

		for res in resPriority:
			filteredStreams = streams.filter(type="video",res=res)
			if len(filteredStreams) > 0:
				break


		highestVideo = None

		for stream in filteredStreams:
			if highestVideo == None:
				highestVideo = stream
			else:
				choosenFPS = int(highestVideo.fps)
				compareFPS = int(stream.fps)
				if choosenFPS < compareFPS:
					highestVideo = stream
				elif choosenFPS == compareFPS:
					choosenMimeTypePriority = videoMimeTypes.index(highestVideo.mime_type)
					compareMimeTypePriority = videoMimeTypes.index(stream.mime_type)
					if choosenMimeTypePriority < compareMimeTypePriority:
						highestVideo = stream

		return highestVideo

		
	def getAudioBestSteamFrom(streams):
		global audioMimeTypes


		filteredStreams = []

		for abr in range(1024,1,-1):
			filteredStreams = streams.filter(type="audio",abr=f'{abr}kbps')
			if len(filteredStreams) > 0:
				break


		highestAudio = None

		for stream in filteredStreams:
			if highestAudio == None:
				highestAudio = stream
			else:
				choosenMimeTypePriority = audioMimeTypes.index(highestAudio.mime_type)
				compareMimeTypePriority = audioMimeTypes.index(stream.mime_type)
				if choosenMimeTypePriority < compareMimeTypePriority:
					highestAudio = stream

		return highestAudio

	
	bestVideoStream = getVideoBestSteamFrom(streams)
	bestAudioStream = getAudioBestSteamFrom(streams)


	normilizedFileName = normilizeFileName(fileName)

	rawVidFileName = f'{normilizedFileName}.vid'
	rawAudFileName = f'{normilizedFileName}.aud'
	mergedMP4FileName = f'{normilizedFileName}.mp4'

	rawVidFilePath = f'{path}\\{rawVidFileName}'
	rawAudFilePath = f'{path}\\{rawAudFileName}'
	mergedMP4FilePath = f'{path}\\{mergedMP4FileName}'


	print(f'downloading: {normilizedFileName}')

	def mergeVidAndAud(vidPath,audPath,mp4Path):
		print("merging Video & Audio:")
		input_video = ffmpeg.input(vidPath)
		input_audio = ffmpeg.input(audPath)
		ffmpeg.concat(input_video, input_audio, v=1, a=1).output(mp4Path).run()
		os.remove(vidPath)
		os.remove(audPath)

	try:


		if (os.path.exists(mergedMP4FilePath) and os.path.isfile(mergedMP4FilePath)) \
		and not(os.path.exists(rawVidFilePath) and os.path.isfile(rawVidFilePath)) \
		and not(os.path.exists(rawAudFilePath) and os.path.isfile(rawAudFilePath)):
			print(f'video file: {normilizedFileName} already exist!')
		elif (os.path.exists(mergedMP4FilePath) and os.path.isfile(mergedMP4FilePath)) \
		and (os.path.exists(rawVidFilePath) and os.path.isfile(rawVidFilePath)) \
		and (os.path.exists(rawAudFilePath) and os.path.isfile(rawAudFilePath)):
			os.remove(mergedMP4FilePath)
			mergeVidAndAud(rawVidFilePath,rawAudFilePath,mergedMP4FilePath)

		elif (os.path.exists(rawVidFilePath) and os.path.isfile(rawVidFilePath)) \
		and (os.path.exists(rawAudFilePath) and os.path.isfile(rawAudFilePath)):
			os.remove(rawAudFilePath)
			print('audio:')
			bestAudioStream.download(output_path = path,filename = rawAudFileName)
			mergeVidAndAud(rawVidFilePath,rawAudFilePath,mergedMP4FilePath)

		elif os.path.exists(rawVidFilePath) and os.path.isfile(rawVidFilePath):
			os.remove(rawVidFilePath)
			print('video:')
			bestVideoStream.download(output_path = path,filename = rawVidFileName)
			print('')
			print('audio:')
			bestAudioStream.download(output_path = path,filename = rawAudFileName)
			mergeVidAndAud(rawVidFilePath,rawAudFilePath,mergedMP4FilePath)

		else:
			print('video:')
			bestVideoStream.download(output_path = path,filename = rawVidFileName)
			print('')
			print('audio:')
			bestAudioStream.download(output_path = path,filename = rawAudFileName)
			mergeVidAndAud(rawVidFilePath,rawAudFilePath,mergedMP4FilePath)


	except Exception as ex:
		print("An error has occurred")
		print("Error:")
		print(ex)
		print("Traceback:")
		traceback.print_exc()
		print("tryng use the highest resolution function: ")
		try:
			streams.get_highest_resolution().download(output_path = path,filename = f'{normilizedFileName}.mp4')
		except:
			print("An error has occurred on get_highest_resolution() function")
	print("Download is completed successfully")







def downloadVideo(link,path,prefix = None):
    youtubeObject = YouTube(link,on_progress_callback=on_progress,use_oauth=True)
    if prefix != None:
    	downloadFile(youtubeObject.streams,path,prefix+'.'+youtubeObject.title)
    else:
    	downloadFile(youtubeObject.streams,path,youtubeObject.title)

def downloadPlaylist(playlistId,path,start):
	def prefixZeros(order,amount):
		result = ''
		diff = len(str(amount-1)) - len(str(order))
		while(diff > 0):
			result += '0'
			diff -= 1
		return result

	global downloadVideo
	p = Playlist(f'https://www.youtube.com/playlist?list={playlistId}')
	print(f'Downloading: {p.title}')
	numOfVids = len(p.video_urls)
	vidCounter = 0

	for videoURL in p.video_urls:
		if start > vidCounter:
			vidCounter += 1
			continue
		downloadVideo(videoURL,path,prefixZeros(vidCounter,numOfVids)+str(vidCounter))
		vidCounter += 1


if len(sys.argv[1:]) > 0:
	if sys.argv[1:][0] == "playlist":
		downloadPlaylist(input("Enter the YouTube playlist Id: "),\
			input("Enter the path:\n"),\
			int(input("Start from:")))
	elif sys.argv[1:][0] == "video":
		downloadVideo(input("Enter the YouTube video URL: "),input("Enter the path:\n"))
	else:
		print("i don't understand please enter video or audio as a parameter next time!")
else:
	print("please enter video or audio as a parameter next time!")






