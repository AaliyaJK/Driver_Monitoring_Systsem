import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()

# Test the engine by speaking a message
engine.say("Hello, this is a test message!")
engine.runAndWait()

