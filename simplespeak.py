from playsound import playsound
import random
import gtts
from time import sleep

FILENAMES = [ # files to play - use something like download_audio to download them.
"livingroomlamp_on.mp3", 
"livingroomlamp_off.mp3", 
"weather.mp3",
"joke.mp3",
"bedroomlamp_on.mp3",
"bedroomlamp_off.mp3"
]

TIME_BETWEEN_REQUESTS = 60 # seconds

def download_audio(text, filename):
	audio = gtts.gTTS(text)
	audio.save(filename)

def main():
	while True:
		filename = random.choice(FILENAMES)
		playsound(filename)
		print(f"Played {filename}")
		sleep(TIME_BETWEEN_REQUESTS)

if __name__ == '__main__':
	main()
