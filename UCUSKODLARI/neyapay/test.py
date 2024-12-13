from gtts import gTTS
import pygame
from g4f import ChatCompletion
import random
import os
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import threading
#import pyttsx3
 
#engine = pyttsx3.init()
messages = [] 

def reader():
    with open('system_content.ai', 'r', encoding='utf-8') as file:
       system_content = file.read()
    return system_content

def initialize_system_role(system_content):
    messages.append({
        "role": "system",
        "content": system_content
    })

def voice_to_text(recognizer):
    
    with sr.Microphone() as source:
        print("Gürültüyü ölçmek için birkaç saniye bekliyorum...")
        recognizer.adjust_for_ambient_noise(source)
        print("Gürültü seviyesi ayarlandı. Konuşmaya başlayabilirsiniz.")
        
        try:
            print("Sesinizi dinliyorum...")
            audio = recognizer.listen(source, timeout=10,phrase_time_limit=10)
            print("Ses kaydedildi, şimdi metne dönüştürülüyor...")
            
            metin = recognizer.recognize_google(audio, language='tr-TR')
            print("Metin: ", metin)
            return metin
        
        except sr.UnknownValueError:
            print("Ses anlaşılamadı, lütfen tekrar deneyin.")
        except sr.RequestError:
            print("Google Web Speech API'ye bağlanırken bir hata oluştu.")
        except sr.WaitTimeoutError:
            print("Ses kaydı alınamadı, zaman aşımına uğradı.")

def get_message_ai(user_content):
    messages.append({"role": "user", "content": user_content})
    try:
        cevap = ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )

        if isinstance(cevap, dict):
            assistant_content = cevap['choices'][0]['message']['content']
        else:
            assistant_content = cevap

        messages.append({"role": "assistant", "content": assistant_content})

    except Exception as e:
        print("Hata oluştu:", e)
        return "Bir hata meydana geldi."
    
    cnt = str(assistant_content)
    return cnt

def control(cnt):
    if "$" in cnt:
        text = cnt.split("$")[1]
        tts = gTTS(text, lang='tr')
        tts.save("ses.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load("ses.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

        if cnt.split(" $ ")[0] == "A001":
            os.system('python git-in.py udp:172.22.160.1:14550 1 -35.36312983 149.16520296')
        if cnt.split(" $ ")[0] == "A002":
            exit()
        if cnt.split("$")[0].split(" ")[1] == "!":
            print("böyle bir fonksiyon yok")

"""def control_pyttsx3():
    if "$" in cnt:
        text = cnt.split("$")[1]
        engine.say(text)
        if cnt.split(" $ ")[0] == "A001":
            os.system('python3 git-in.py tcp:localhost:5762 1 40.71221945 30.02442263')
        if cnt.split(" $ ")[0] == "A002":
            exit()
       if cnt.split("$")[0].split(" ")[1] == "!":
            print("böyle bir fonksiyon yok")"""

system_content = reader()
initialize_system_role(system_content)
while True:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Gürültüyü ölçmek için birkaç saniye bekliyorum...")
        recognizer.adjust_for_ambient_noise(source)
        print("Gürültü seviyesi ayarlandı. Konuşmaya başlayabilirsiniz.")
        try:
                print("Dinliyorum...")
                audio = recognizer.listen(source)
                
                print("Sesi çözümlüyorum...")
                text = recognizer.recognize_google(audio, language='tr-TR')      
                print(f"Algılanan Metin: {text}")
                if "sabiha" in text.lower():
                    print("'Sabiha' kelimesi algılandı! Dinlemeye başlıyorum.")
                    
                    user_content = voice_to_text(recognizer)
                    cnt = get_message_ai(user_content)
                    control(cnt)
                
        except sr.UnknownValueError:
            print("Ses anlaşılamadı.")
        except sr.RequestError:
            print("API'ye bağlanırken bir hata oluştu.")
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
