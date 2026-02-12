import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
import datetime as dt
import pywhatkit as pwk
import wikipedia as wiki


r=sr.Recognizer()

def speak(cmd):
    tts=gTTS(cmd,lang='te')
    tts.save("telugu_audio.mp3")
    playsound(r"C:\Users\mgraj\AppData\Local\Programs\Python\Python313\telugu_audio.mp3")
    os.remove("telugu_audio.mp3")

bot="స్వీటీ"



def main(check):
    cmd=""
    try:
        with sr.Microphone() as source:
            print("say something ra...")
            audio=r.listen(source)
            if check:
                cmd=r.recognize_google(audio,language='te-IN')
                if bot in cmd:
                    cmd=cmd.replace("స్వీటీ"," ")
                    print(cmd)
                #speak(cmd)
                else:
                    cmd=""
            else:
                cmd=r.recognize_google(audio,language='en-US')
        
    except:
        print('check your mic')
    return cmd
while True:
    final_cmd=main(True)
    if final_cmd!="":
        if "సమయం" in final_cmd:
            cu_time=dt.datetime.now().strftime("%I:%M %p")
            speak(cu_time)
        if "యూట్యూబ్" in final_cmd or "youtube" in final_cmd:
            speak("నేను ఏ వీడియో ప్లే చేయాలి")
            final_cmd=main(False)
            pwk.playonyt(final_cmd)
            print(final_cmd)
            break
        if "గూగుల్" in final_cmd or "google" in final_cmd:
            speak("నేను ఏమి వెతకాలి")
            final_cmd=main(False)
            pwk.search(final_cmd)
            print(final_cmd)
        elif "ఎవరు" in final_cmd:
            query = final_cmd.replace("ఎవరు", "").strip()
            wiki.set_lang('te')
            info = wiki.summary(query, sentences=3)
            print(info)
            speak(info)
            final_cmd=main(False)
        elif "నువ్వు తెలియదు" in final_cmd:
            speak("నేను నీ స్వీటి నిఖిల్‌ని. నన్ను మర్చిపోయావా? చాలా బాధగా ఉంది")
            final_cmd=main(False)

        elif "ఎక్కడ" in final_cmd:
            final_cmd=final_cmd.replace("ఎక్కడ"," ").strip()
            wiki.set_lang('te')
            info=wiki.summary(final_cmd,sentences=2)
            print(info)
            speak(info)
            final_cmd=main(False)
    

        


