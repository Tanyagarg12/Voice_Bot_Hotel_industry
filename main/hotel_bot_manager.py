import speech_recognition as sr  
from gtts import gTTS  
import pygame  
import google.generativeai as genai  
import os

# Gemini API with your key 
genai.configure(api_key='API_KEY')

for m in genai.list_models():
    print(m.name)


def list_available_models():
    try:
        models = genai.list_models()
        print("\nAvailable Gemini Models:")
        for model in models:
            print(f"- {model.name}: {model.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")

# response from Gemini LLM (with fallback)
model = genai.GenerativeModel("models/gemini-2.5-flash")
chat = model.start_chat(history=[])

def get_llm_response(user_input):
    try:
        response = chat.send_message(user_input)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Sorry, I'm having trouble connecting. Please try again."
    

# listen for user speech
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... (Speak now)")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Speech not understood.")
            return ""
        except sr.RequestError:
            print("Speech recognition service error.")
            return ""
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

# text to speech and play it
def speak(text):
    try:
        pygame.mixer.init()
        tts = gTTS(text=text, lang='en', slow=False)
        filename = "response.mp3"
        tts.save(filename)
        sound = pygame.mixer.Sound(filename)
        sound.play()
        pygame.time.wait(int(sound.get_length() * 1000))
        os.remove(filename)
    except Exception as e:
        print(f"TTS error: {e}")


# bot loop
def main():
    print("Hotel Voice Bot started! Say 'exit' to quit.")
    speak("Hello! I'm your hotel concierge. How can I help you today?")
    chat.history = []  

    while True:
        user_input = listen().lower().strip()
        if not user_input:
            continue

        if any(word in user_input.lower() for word in ["confirm", "that's all", "that is all", "i'm done", "done", "finished"]):
            speak("Great! I'm glad I could assist you with your booking.")
            speak("Is there anything else I can help you with?")
            follow_up = listen()
            if follow_up and any(word in follow_up.lower() for word in ["no", "no thank you", "nothing", "bye"]):
                speak("You're most welcome, Tanya! Have a wonderful day and enjoy your stay.")
                break
            else:
                speak("Sure! How else may I assist you?")

        
        if "confirm" in user_input:
            chat.send_message("Summarize the booking details provided so far.")

        if user_input in ["exit", "quit", "stop"]:
            speak("Goodbye! Have a great stay.")
            print("Bot stopped.")
            break

        
        llm_response = get_llm_response(user_input)
        print(f"Bot: {llm_response}")
        speak(llm_response)


if __name__ == "__main__":
    main()
