import random
import gtts
import os
import math
import copy
from playsound import playsound
from datetime import datetime, timedelta
from time import sleep
from collections import deque
from threading import Thread, Lock

AUDIO_QUEUE = deque()
RUN_QUEUE = True
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
		print("Going up a level")
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


def print_queue():
	qcopy = None
	with Lock():
		qcopy = copy.deepcopy(AUDIO_QUEUE)

	print("---------------------------- QUEUE ----------------------------")
	sequence = 0
	while not len(qcopy) == 0:
		item = qcopy.pop()
		filename = item["name"]
		time = item["time"]
		print(f"[{sequence}] {time} - {filename}")
		sequence += 1
	print("---------------------------------------------------------------")


def handle_command(cmd):
	if cmd == "printqueue":
		print_queue()
	elif cmd == "remaining":
		with Lock():
			next_time = AUDIO_QUEUE[-1]["time"]
			time_diff = next_time - datetime.now()
			sec = int(time_diff.total_seconds())
			print(f"Next file will be played at {next_time.strftime('%H:%M:%S')}, in {sec} s")
	elif cmd == "exit":
		print("Stopping queue and exiting program...")
		RUN_QUEUE = False
		RUN_MAIN = False
	else:
		print("Commands:\nhelp - prints this help page\nprintqueue - print the audio queue\nexit - stops queue and exits program")


def main_loop():
	print("==================== WELCOME to SimpleSpeak ===================")
	print("The current time is: " + datetime.now().strftime("%H:%M:%S"))

	check_and_download()

	print("Startup process complete, starting the audio queue")
	queue_thread = Thread(target=queue_loop)
	queue_thread.start()

	print("Audio queue is now running")
	print("For a list of commands, type 'help'")
	while RUN_MAIN:
		# handle commands
		# print("[debug] RUN_MAIN: " + str(RUN_MAIN))
		cmd = input("> ")
		handle_command(cmd)

	print("Queue thread execution finished")


def queue_loop():
	print("Starting queue loop in a separate thread")
	import_and_queue()
	os.chdir("audio")

	while RUN_QUEUE:
		with Lock():
			# print("[debug] RUN_QUEUE: " + str(RUN_QUEUE))
			next_scheduled_time = AUDIO_QUEUE[-1]["time"]
			if len(AUDIO_QUEUE) == 0:
				print("Empty queue, requeuing...")
				os.chdir("..")
				import_and_queue()
				os.chdir("audio")
			elif len(AUDIO_QUEUE) < 3:
				print("Queue almost empty (< 3 items left), requeuing...")
				os.chdir("..")
				import_and_queue()
				os.chdir("audio")
			elif next_scheduled_time > datetime.now():
				sleep(1)
			else:
				current_item = AUDIO_QUEUE.pop()
				next_item = AUDIO_QUEUE[-1]
				filename = current_item["name"]
				print(f"Playing {filename} at {datetime.now().strftime('%H:%M:%S')}, next file {next_item['name']} playing at {next_item['time'].strftime('%H:%M:%S')}")
				playsound(filename)


def main():
	main_loop()
	main_thread = Thread(target=main_loop)
	main_thread.start()
	main_thread.join()
	print("Main thread execution finished. Exiting program")
		

if __name__ == '__main__':
	main()
