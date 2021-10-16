from playsound import playsound
import random
import gtts
from datetime import datetime
from datetime import timedelta
from time import sleep
import os
from collections import deque
import math
import copy
from threading import Thread

AUDIO_QUEUE = deque()
#RUN_QUEUE = True
#REMAINING_TIME = 0
RUN_MAIN = True

def download_audio(text, filename):
	audio = gtts.gTTS(text)
	audio.save(filename)
	print(f"Downloaded audio file audio/{filename}")

def check_and_download():
	print("Checking for files...")

	# Check for audio.txt
	root = os.getcwd()
	if not os.path.isfile(root + "/audio.txt"):
		print("audio.txt not found. No audio files will be downloaded.")
		print("To download text-to-speech audio files, enter lines into audio.txt in the format <audio message>|<filename>|<delay in seconds>")
		print("Example: 'Hey Google, turn on the bedroom lamp|bedroomlamp_on.mp3|60'")
		return

	# Check for audio directory, create it if it doesn't exist
	if not os.path.isdir(root + "/audio"):
		print("/audio directory not found. Creating it and downloading missing audio.")
		os.mkdir("audio")

	# Open audio file - at this point audio file and audio dir both exist
	# <text>|<filename>|<min_delay> - [0]|[1]|[2]
	with open("audio.txt", "r") as audio_txt:
		os.chdir("audio")
		audio_txt_lines = [line.split("|") for line in audio_txt.readlines()]
		downloaded_files = os.listdir()
		audio_txt_files = [line[1] for line in audio_txt_lines]
		missing_files = []
		for line in audio_txt_lines:
			if line[1] not in downloaded_files:
			 	missing_files.append(line)

		if missing_files:
			print(f"Found {len(missing_files)} missing files, downloading...")
		else:
			print("No missing files")

		# Download missing files
		for line in missing_files:
			download_audio(line[0], line[1])
		os.chdir("..")


def import_and_queue():
	print("Queueing audio files...")
	with open("audio.txt", "r") as audio_txt:
		audio_txt_lines = [line.split("|") for line in audio_txt.readlines()]

		# Calculate total time
		total_time = 0
		for line in audio_txt_lines:
			total_time += int(line[2])

		# Create a queue at least 7200 seconds long (2 hours)
		# How many copies of the audio list do we need so there is enough audio to fill that timeframe?
		audio_copies_needed = math.ceil(7200 / total_time)
		print(f"{audio_copies_needed} copies needed, total time {total_time}")
		lines_to_queue = audio_txt_lines * audio_copies_needed
		random.shuffle(lines_to_queue)

		count = 0
		previous_time = datetime.now()
		for line in lines_to_queue:
			if count == 0:
				time = previous_time + timedelta(seconds=5)
			else:
				time = previous_time + timedelta(seconds=int(line[2]))

			AUDIO_QUEUE.appendleft({
				"name": line[1],
				"time": time
			})
			count += 1
			previous_time = time

		print("---------------------------- QUEUE ----------------------------")
		print_queue()
		print("---------------------------------------------------------------")


def print_queue():
	qcopy = copy.deepcopy(AUDIO_QUEUE)
	sequence = 0
	while not len(qcopy) == 0:
		item = qcopy.pop()
		filename = item["name"]
		time = item["time"]
		print(f"[{sequence}] {time} - {filename}")
		sequence += 1


# def handle_command(cmd):
# 	if cmd == "printqueue":
# 		print_queue()
# 	elif cmd == "remaining":
# 		print(f"Remaining time until next file played: {REMAINING_TIME} s")
# 	elif cmd == "exit":
# 		print("Stopping queue and exiting program...")
# 		RUN_QUEUE = False
# 		RUN_MAIN = False
# 	else:
# 		print("Commands:\nhelp - prints this help page\nprintqueue - print the audio queue\nexit - stops queue and exits program")


def main_loop():
	print("==================== WELCOME to SimpleSpeak ===================")
	print("The current time is: " + datetime.now().strftime("%H:%M:%S"))

	check_and_download()
	import_and_queue()
	os.chdir("audio")

	print("Startup process complete, starting the audio queue")
	# print("For a list of commands, type 'help'")
	# queue_thread = Thread(target=queue_loop)
	# queue_thread.start()

	while RUN_MAIN:
		# handle commands
		# cmd = input("> ")
		# handle_command(cmd)
		next_scheduled_time = AUDIO_QUEUE[-1]["time"]

		if len(AUDIO_QUEUE) == 0:
			print("Empty queue, requeuing...")
			import_and_queue()
		elif len(AUDIO_QUEUE) < 3:
			print("Queue almost empty (< 3 items left), requeuing...")
			import_and_queue()
		elif next_scheduled_time > datetime.now():
			sleep(1)
		else:
			current_item = AUDIO_QUEUE.pop()
			next_item = AUDIO_QUEUE[-1]
			filename = current_item["name"]
			print(f"Playing {filename} at {datetime.now().strftime('%H:%M:%S')}, next file {next_item['name']} playing at {next_item['time'].strftime('%H:%M:%S')}")
			playsound(filename)

	# queue_thread.join()
	# print("Queue thread execution finished")


# def queue_loop():
# 	print("Starting queue loop in a separate thread")
# 	while RUN_QUEUE:
# 		if AUDIO_QUEUE.empty():
# 			print("Empty queue, requeuing...")
# 			import_and_queue()
# 		elif len(AUDIO_QUEUE) < 3:
# 			print("Queue almost empty (< 3 items left), requeuing...")
# 		else:
# 			current_item = AUDIO_QUEUE.get()
# 			filename = current_item["name"]
# 			playsound(filename)

# 			# How long to sleep for?
# 			next_item = AUDIO_QUEUE[0]["delay"]
# 			print(f"Played {filename} at {datetime.now().strftime('%H:%M:%S')}, next file {next_item['name']} playing in {sleep_time} seconds")

# 			REMAINING_TIME = sleep_time
# 			while REMAINING_TIME > 0:
# 				sleep(1)
# 				REMAINING_TIME -= 1
# 				if not RUN_QUEUE:
# 					break


def main():
	main_loop()
	# main_thread = Thread(target=main_loop)
	# main_thread.start()
	# main_thread.join()
	print("Main thread execution finished. Exiting program")
		

if __name__ == '__main__':
	main()
