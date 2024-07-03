import tkinter as tk
import customtkinter as ctk
import threading
import re
import time
import json
import speech_recognition as sr
import vlc
import os
from datetime import datetime
import smtplib, ssl

# set defualt apearance
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(ctk.CTk):
    def __init__(self, sr, mailer, diary, player):
        self.sr = sr
        self.mailer = mailer
        self.diary = diary
        self.player = player
        self.mode = 'English'
        ctk.CTk.__init__(self)
        self.about_text_text =('\n		Mano Speech v0.1 Beta\n'+
                '		----------------------------------\n\n'+
                'This is a Mini Project for SCI students, L3, 2022/2023.\n'+
                'You can send email, write note or play.\n'+
                'It has two mode Dark Mode and Light Mode.\n'+
                'you can use trained sphinx model or Google API.\n'+
                'you can use the manual interface or speech recognizer.\n\n'+
                '		<Press Ctrl + Space to talk>\n\n\n'+
                '			         This project is made by:\n'+
                '				Walid  Tolba\n'+
                '				Manel Abdelaziz')

        # configure window
        self.title("Mano Speech")
        self.geometry("650x500")
        self.minsize(600, 400)

        # configure grid layout (2, 3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)


        # create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Mano Speech", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.email_button = ctk.CTkButton(self.sidebar_frame, text = 'Send Email', command=lambda : (self.email_frame.tkraise(), self.frame_label.configure(text='Email')))
        self.email_button.grid(row=1, column=0, padx=20, pady=10)
        self.note_button = ctk.CTkButton(self.sidebar_frame, text = 'Write Note', command=lambda : (self.note_frame.tkraise(), self.frame_label.configure(text='Note')))
        self.note_button.grid(row=2, column=0, padx=20, pady=10)
        self.music_button = ctk.CTkButton(self.sidebar_frame, text = 'Play Music', command=self.process_play_music)
        self.music_button.grid(row=3, column=0, padx=20, pady=10)
        self.about_button = ctk.CTkButton(self.sidebar_frame, text = 'About', command=lambda : (self.about_frame.tkraise(), self.frame_label.configure(text='About')))
        self.about_button.grid(row=4, column=0, padx=20, pady=10)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(0, 10))
        self.acoustic_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Module:", anchor="w")
        self.acoustic_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.recognition_model_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Arabic", "English", "Google API"],
                        command=lambda x: (self.sr.change_model(x), self.change_mode_to_arabic() if x == 'Arabic' else self.change_mode_to_english()))
        self.recognition_model_optionemenu.grid(row=9, column=0, padx=20, pady=(0, 20))

        # Title
        self.frame_label = ctk.CTkLabel(self, text="About", font=ctk.CTkFont(size=16, weight="bold"))
        self.frame_label.grid(row=0, column=1, padx=10, pady=(5, 5))

        # create tabview
        self.email_frame = ctk.CTkFrame(self)
        self.email_frame.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="nsew")
        self.note_frame = ctk.CTkFrame(self)
        self.note_frame.grid(row=1, column=1, padx=20, pady=(10, 10), sticky="nsew")
        self.about_frame = ctk.CTkFrame(self)
        self.about_frame.grid(row=1, column=1, padx=20, pady=(10, 10), sticky="nsew")
        self.about_frame.tkraise()

        
        self.email_frame.columnconfigure(0, weight=1);
        self.email_frame.rowconfigure(4, weight=1);
                
        self.email_from = ctk.CTkEntry(self.email_frame, placeholder_text="From")
        self.email_from.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.email_password = ctk.CTkEntry(self.email_frame, placeholder_text="Password", show='*')
        self.email_password.grid(row=1, column=0, padx=10, pady=(7, 0), sticky="nsew")

        self.email_to = ctk.CTkEntry(self.email_frame, placeholder_text="To")
        self.email_to.grid(row=2, column=0, padx=10, pady=(7, 0), sticky="nsew")

        self.email_object = ctk.CTkEntry(self.email_frame, placeholder_text="Object")
        self.email_object.grid(row=3, column=0, padx=10, pady=(7, 0), sticky="nsew")

        self.email_text = ctk.CTkTextbox(self.email_frame, border_width=2)
        self.email_text.grid(row=4, column=0, padx=10, pady=(7, 0), sticky="nsew")

        self.email_button = ctk.CTkButton(self.email_frame, text = 'Submit', command=self.process_submit_email)
        self.email_button.grid(row=5, column=0, padx=20, pady=7)


        self.note_frame.columnconfigure(0, weight=1);
        self.note_frame.rowconfigure(0, weight=1);

        self.note_text = ctk.CTkTextbox(self.note_frame, border_width=2)
        self.note_text.grid(row=0, column=0, padx=10, pady=(7, 0), sticky="nsew")

        self.note_button = ctk.CTkButton(self.note_frame, text = 'Add Note', command=self.process_add_note)
        self.note_button.grid(row=1, column=0, padx=20, pady=7)

        self.about_frame.columnconfigure(0, weight=1);
        self.about_frame.rowconfigure(0, weight=1);
        
        self.about_text = ctk.CTkTextbox(self.about_frame, border_width=2)
        self.about_text.grid(row=0, column=0, padx=10, pady=(7, 0), sticky="nsew")
        self.about_text.insert('0.1', self.about_text_text)

        # create progress talking bar
        self.progressbar = ctk.CTkProgressBar(self, mode="indeterminnate")
        self.progressbar.grid(row=2, column=1, padx=(20, 20), pady=(0, 10), sticky="ew")

        self.music_frame = ctk.CTkFrame(self, height=30)
        self.music_frame.grid(row=3, column=1, padx=(20, 20), pady=(0, 15), sticky="nsew")
        self.music_label = ctk.CTkLabel(master=self.music_frame, text="No Music is playing.")
        self.music_label.grid(row=0, column=0, padx=10, sticky="")

        self.bind('<Control-space>', self.process_space)
        self.get_current_frame()
        
    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def process_play_music(self):
        if (not self.player.is_playing()):
            music = self.player.play()
            self.music_button.configure(text='Stop Music')
            self.music_label.configure(text='Playing: ' + music)
        else:
            self.player.stop()
            self.music_button.configure(text='Play Music')
            self.music_label.configure(text='No Music is playing.')

    def process_add_note(self):
        self.diary.add_note(self.note_text.get("1.0", "end-1c"))
        self.note_text.delete("1.0", tk.END)

    def process_submit_email(self):
        self.mailer.send_email(self.email_from.get(), self.email_password.get(), self.email_to.get(), self.email_object.get(), self.email_text.get('1.0', 'end-1c'))
        self.email_from.delete(0, tk.END)
        self.email_password.delete(0, tk.END)
        self.email_to.delete(0, tk.END)
        self.email_object.delete(0, tk.END)
        self.email_password.delete(0, tk.END)
        self.email_text.delete("0.1", tk.END)
        
    def process_space(self, event = None):
            self.progressbar.start()
            thread = threading.Thread(target = self.talk)
            thread.start()

    def talk(self):
        text = self.sr.talk()
        print(text)
        order = self.recognize_order(text)
        self.progressbar.stop()
        self.process_order(order)
        
    def talk_to_write(self, widget):
        def talk_then_write():
                text = self.sr.talk()
                self.progressbar.stop()
                self.active_writing(widget, text)
        self.progressbar.start()
        thread = threading.Thread(target = talk_then_write)
        thread.start()
        
    def get_current_frame(self):
        return self.frame_label.cget('text')
    
            
    def recognize_order(self, text):
        text = text.lower()
        current_frame = self.get_current_frame()
        if self.sr.model in ('English', 'Google API'):
            if text == 'email' or re.search('send.*email', text):
                return 'SEND_EMAIL_FRAME'
            elif text == 'note' or re.search('write.*note', text):
                return 'WRITE_NOTE_FRAME'
            elif not self.player.is_playing() and (text in ('play', 'music') or re.search('play.*music', text)):
                return 'PLAY_MUSIC'
            elif self.player.is_playing() and (text == 'stop' or re.search('stop.*music', text)):
                return 'STOP_MUSIC'
            elif text == 'about' or text == 'home' or re.search('home.*page', text):
                return 'ABOUT_FRAME'
            elif text == 'light' or re.search('light.*mode', text):
                return 'LIGHT_MODE'
            elif text == 'dark' or re.search('dark.*mode', text):
                return 'DARK_MODE'
            elif re.search('system.*mode', text):
                return 'SYSTEM_MODE'
            elif text == 'english' or re.search('english.*mode', text):
                return 'ENGLISH'
            elif text == 'arabic' or re.search('arabic.*mode', text):
                return 'ARABIC'
            elif re.search('google.*mode|api', text):
                return 'GOOGLE_API'
            elif current_frame == 'Email' and re.search('write', text):
                return 'WRITE_EMAIL'
            elif current_frame == 'Email' and re.search('from', text):
                return 'FROM'
            elif current_frame == 'Email' and re.search('to', text):
                return 'TO'
            elif current_frame == 'Email' and re.search('object', text):
                return 'OBJECT'
            elif current_frame == 'Email' and re.search('submit', text):
                return 'SUMBIT_EMAIL'
            elif current_frame == 'Note' and re.search('write', text):
                return 'WRITE_NOTE'
            elif current_frame == 'Note' and re.search('add|submit', text):
                return 'ADD NOTE'
            elif text == 'quit' or text == 'exit':
                return 'DESTROY'
            
        elif self.sr.model == 'Arabic':
            if text == 'risala' or re.search('arsil.*risala', text):
                return 'SEND_EMAIL_FRAME'
            elif text == 'modhakira' or re.search('oktob.*modhakira', text):
                return 'WRITE_NOTE_FRAME'
            elif not self.player.is_playing() and (text in ('shghil', 'almousiqa') or re.search('shagil.*almousiqa', text)):
                return 'PLAY_MUSIC'
            elif self.player.is_playing() and (text == 'awqif' or re.search('awqif.*almousiqa', text)):
                return 'STOP_MUSIC'
            elif re.search('asafha.*ara2isya', text):
                return 'ABOUT_FRAME'
            elif text == 'almodhi2' or re.search('alwadha3.*almodhi2', text):
                return 'LIGHT_MODE'
            elif text == 'almodhlim' or re.search('alwadha3.*almodhlim', text):
                return 'DARK_MODE'
            elif text == 'inglizi' or re.search('alwadha3.*inglizi', text):
                return 'ENGLISH'
            elif text == '3arabi' or re.search('alwadha3.*3arabi', text):
                return 'ARABIC'
            elif current_frame == 'Email' and re.search('oktob', text):
                return 'WRITE_EMAIL'
            elif current_frame == 'Email' and re.search('min', text):
                return 'FROM'
            elif current_frame == 'Email' and re.search('ila', text):
                return 'TO'
            elif current_frame == 'Email' and re.search('al3onwan', text):
                return 'OBJECT'
            elif current_frame == 'Email' and re.search('arsil', text):
                return 'SUMBIT_EMAIL'
            elif current_frame == 'Note' and re.search('oktob', text):
                return 'WRITE_NOTE'
            elif current_frame == 'Note' and re.search('arsil', text):
                return 'ADD NOTE'
            
        elif self.model == 'Arabic':
            pass
    def process_order(self, order):
        print(order)
        if order == 'SEND_EMAIL_FRAME':
            self.email_frame.tkraise()
            self.frame_label.configure(text='Email')
        elif order == 'WRITE_NOTE_FRAME':
            self.note_frame.tkraise()
            self.frame_label.configure(text='Note')
        elif order == 'ABOUT_FRAME':
            self.about_frame.tkraise()
            self.frame_label.configure(text='About')
        elif order == 'LIGHT_MODE':
            self.change_appearance_mode_event('Light')
        elif order == 'DARK_MODE':
            self.change_appearance_mode_event('Dark')
        elif order == 'SYSTEM_MODE':
            self.change_appearance_mode_event('System')
        elif order == 'PLAY_MUSIC' or order == 'STOP_MUSIC':
            self.process_play_music()
        elif order == 'ENGLISH':
            self.sr.change_model('English')
            change_mode_to_english()
        elif order == 'ARABIC':
            self.sr.change_model('Arabic')
            change_mode_to_arabic()
        elif order == 'GOOGLE_API':
            self.sr.change_model('Google API')
            change_mode_to_english()
        elif order == 'SUMBIT_EMAIL':
            self.process_submit_email()
        elif order == 'ADD_NOTE':
            self.process_add_note()
        elif order == 'WRITE_NOTE':
            self.talk_to_write(self.note_text)
        elif order == 'WRITE_EMAIL':
            self.talk_to_write(self.email_text)
        elif order == 'OBJECT':
            self.talk_to_write(self.email_object)
        elif order == 'FROM':
            self.active_writing(self.email_from, 'walidtest24@gmail.com')
            self.email_password.insert(0, 'oirwhponowplmhna')
        elif order == 'TO':
            self.active_writing(self.email_to, 'wrt0624@gmail.com')
        elif order == 'DESTROY':
            exit()
            

    def change_mode_to_arabic(self):
        if not self.mode == 'Arabic':
            self.mode = 'Arabic'
            
            
    def change_mode_to_english(self):
        if not self.mode == 'English':
            
            self.mode = 'English'
    def active_writing(self, widget, text):
        if isinstance(widget, ctk.CTkTextbox):
            widget.delete('0.1', tk.END)
        else:
            widget.delete(0, tk.END)
        for l in text:
            widget.insert(tk.END, l)
            self.update_idletasks()
            time.sleep(0.1)



class Recognizer:
    def __init__(self):
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone()
        self.model = 'Google API'

    def change_model(self, model):
        if model in ('English', 'Arabic', 'Google API'):
            self.model = model

    def talk(self):
        audio = self.record_speech()
        text = self.recognize_speech(audio)
        return text

    def record_speech(self):
        with self.mic as source:
            audio = self.rec.listen(source)
        return audio

    def recognize_speech(self, audio):
        text = None
        if self.model == 'Arabic':
            text = self.rec.recognize_sphinx(audio,
                                language = ('wmdb.ci_cont', 'wmdb.lm.DMP', 'wmdb.dic'))
        elif self.model == 'English':
            text = self.rec.recognize_sphinx(audio,
                                language = ('an4.ci_cont', 'an4.lm.DMP', 'an4.dic'))
        elif self.model == 'Google API':
            text = self.rec.recognize_google(audio)
        return text


class Player:
    def __init__(self):
        self.playlist = os.listdir(os.path.join('Music'))
        self.sound = None
        
    def play(self):
        if not self.is_playing():
            self.sound = vlc.MediaPlayer(os.path.join('Music', self.playlist[0]))
            self.sound.play()
            return self.playlist[0]
            
    def stop(self):
            if self.is_playing():
                self.sound.stop()
                self.sound = None
                
    def is_playing(self):
        return self.sound != None


class Diary:
    @staticmethod
    def add_note( text):
        temp = str(datetime.now()) + '\n'
        temp += text
        temp += '\n' + '-' * 50 + '\n'
        file = open('Diary.txt', 'a')
        file.write(temp)
        file.close()

class Mailer():
    def __init__(self):
        self.port = 465
        self.smtp_server = "smtp.gmail.com"
    def send_email(self, from_, pw, to_,sbj , msg):
        message = 'Subject:' + sbj + '\n\n' + msg + '\n'
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(from_, pw)
            server.sendmail(from_, to_, message)

if __name__ == "__main__":
    rec = Recognizer()
    mailer = Mailer()
    diary = Diary()
    player = Player()
    app = App(rec, mailer, diary, player)
    app.mainloop()

