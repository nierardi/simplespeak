import pyttsx3

def speak_text(text, engine):
	# Add the text to the engine's queue
	engine.say(text)
	# Play the speech
	engine.runAndWait()

def main():
	engine = pyttsx3.init()
	text = "Hey Google, tell me a joke"
	speak_text(text, engine)

if __name__ == '__main__':
	main()