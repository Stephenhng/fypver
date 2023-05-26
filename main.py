#FYP Project 69803
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from datetime import datetime
import csv
import warnings
import pandas as pd
import sqlite3
import re
import random
import json
import pickle
import numpy as np
import nltk
import webbrowser
from model import TensorFlowModel

from nltk.stem import WordNetLemmatizer

import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "disease.db")

warnings.filterwarnings("ignore", category=DeprecationWarning)

nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())
description_intents = json.loads(open('description_intents.json').read())
precaution_intents = json.loads(open('precaution_intents.json').read())


words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

model = TensorFlowModel()
model.load(os.path.join(os.getcwd(), 'model.tflite'))

df1 = pd.read_csv('MasterData/Symptom_Severity.csv')


model2 = pickle.load(open('rfc_model.pkl', 'rb'))


now = datetime.now()


class Command(Label):
    text = StringProperty
    size_hint_x = NumericProperty
    halign = StringProperty
    font_size = 17


class Response(Label):
    text = StringProperty
    size_hint_x = NumericProperty
    halign = StringProperty
    font_size = 17


class History(Label):
    text = StringProperty
    size_hint_x = NumericProperty
    halign = StringProperty
    font_size = 17


class Label(Label):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            webbrowser.open_new(self.url)
            return True
        return super().on_touch_down(touch)


class parentApp(App):

    passwd = ObjectProperty(None)
    confirm_passwd = ObjectProperty(None)

    def change_screen(self, name):
        screen_manager.current = name

    def build(self):
        self.icon = "virus.png"
        Window.clearcolor = (1, 1, 1, 1)
        global screen_manager, description_list
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("parent.kv"))
        screen_manager.add_widget(Builder.load_file("register.kv"))
        screen_manager.add_widget(Builder.load_file("content.kv"))
        screen_manager.add_widget(Builder.load_file("history.kv"))
        screen_manager.add_widget(Builder.load_file("profile.kv"))
        screen_manager.add_widget(Builder.load_file("setting.kv"))
        screen_manager.add_widget(Builder.load_file("forget.kv"))
        screen_manager.add_widget(Builder.load_file("updatepro.kv"))
        self.disease_description()
        self.disease_precaution()

        with sqlite3.connect(db_path) as mydb:

            c = mydb.cursor()

            # sql = "DELETE FROM users WHERE email = 'fucai99@gmail.com'"
            # c.execute(sql)

            # sql2 = "SELECT * FROM users"
            # c.execute(sql2)
            # result = c.fetchall()
            #
            # for x in result:
            #     print(x)

            # sql3 = "SELECT * FROM results"
            # c.execute(sql3)
            # result2 = c.fetchall()
            #
            # for a in result2:
            #     print(a)

            # c.execute("""DROP TABLE results""")

            #c.execute("SHOW DATABASES")
            #for db in c:
            #    print(db)

            #c.execute("SELECT * FROM users")
            #print(c.description)

            c.execute("""CREATE TABLE IF NOT EXISTS users (name VARCHAR(255), age INT(10), weight INT(10), height INT(10), gender VARCHAR(255), email VARCHAR(255), phone VARCHAR(255), password VARCHAR(255), confirm_password VARCHAR(255))""")
            c.execute("""CREATE TABLE IF NOT EXISTS results (email VARCHAR(255), symptom VARCHAR(255), disease VARCHAR(255))""")

            # c.execute("SHOW TABLES")
            # for x in c:
            #    print(x)

        mydb.commit()

        mydb.close()

        return screen_manager


    def disease_description(self):
        with open('MasterData/Symptom_Description.csv','r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            _description = {"description_intents": []}
            for row in csv_reader:
                _description["description_intents"].append({"tag":"description_" + row[0].replace(' ','_'), "patterns":[row[0].lower(), row[0], "what is " + row[0], "tell me about " + row[0], "Anything on " + row[0], "how about " + row[0]] , "responses":[row[1]]})

        with open('description_intents.json', 'w') as json_file:
            json.dump(_description, json_file,indent=2)


    def disease_precaution(self):
        with open('MasterData/Symptom_Precaution.csv','r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            _precaution = {"precaution_intents":[]}
            for row in csv_reader:
                _precaution["precaution_intents"].append({"tag":"precaution_" + row[0].replace(' ','_'), "patterns":["medicine for " + row[0], "Recover of " + row[0], "treatment for " + row[0], "I am getting " + row[0], "what is the precaution for " + row[0], "how to avoid " + row[0], "how to prevent " + row[0]] , "responses":[row[1],row[2],row[3],row[4]]})

        with open('precaution_intents.json', 'w') as json_file:
            json.dump(_precaution, json_file,indent=2)


    def log_in(self):
        email = screen_manager.get_screen('main').email.text
        passwd = screen_manager.get_screen('main').passwd.text

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        match = re.match(pattern, email)

        with sqlite3.connect(db_path) as mydb:
            c = mydb.cursor()

            sql = (f"SELECT * FROM users WHERE email = '{email}' and password = '{passwd}'")
            c.execute(sql)
            result = c.fetchone()

            if email == "" or passwd == "":
                layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                popupLabel = Label(text="Please fill all the blank to login")
                closeButton = Button(text="Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title='Error', content=layout)
                popup.open()
                closeButton.bind(on_press=popup.dismiss)
            elif result and match:
                self.root.transition.direction = "left"
                self.root.current = "content"
                app = App.get_running_app()
                app.user_details = {'name': result[0], 'age': result[1], 'weight': result[2], 'height': result[3], 'gender': result[4], 'email': result[5], 'phone': result[6], 'password': result[7], 'confirm_password':result[8]}
            else:
                layout = GridLayout(cols=1, size_hint=(.6, .3), pos_hint={"x": .2, "top": .9}, padding=10)
                popupLabel = Label(text="Email does not register yet\nor\nEmail or password was wrong ")
                closeButton = Button(text="Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title='Error', content=layout)
                popup.open()
                closeButton.bind(on_press=popup.dismiss)


        mydb.commit()

        mydb.close()

        screen_manager.get_screen('main').email.text = ""
        screen_manager.get_screen('main').passwd.text = ""

    def log_out(self):
        layout = GridLayout(cols=1, size_hint=(.6, .3), pos_hint={"x": .2, "top": .9}, padding=10)
        popupLabel = Label(text="Confirm to log out?")
        closeButton = Button(text="Continue")
        backButton = Button(text="Back")
        layout.add_widget(popupLabel)
        layout.add_widget(closeButton)
        layout.add_widget(backButton)
        popup = Popup(title='Log Out', content=layout)
        popup.open()
        backButton.bind(on_press=popup.dismiss, on_release=self.go_to_setting)
        closeButton.bind(on_press = popup.dismiss, on_release = self.go_to_main)

    def go_to_content(self, instance):
        self.root.transition.direction = "left"
        self.root.current = "content"

    def go_to_main(self, instance):
        self.root.transition.direction = "left"
        self.root.current = "main"

    def go_to_setting(self, instance):
        self.root.transition.direction = "left"
        self.root.current = "setting"

    def forget_pass(self):
        layout = GridLayout(cols=1, size_hint=(.6, .3), pos_hint={"x": .2, "top": .9}, padding=10)
        popupLabel = Label(text="Confirm to change your password?")
        closeButton = Button(text="Continue")
        backButton = Button(text="Back")
        layout.add_widget(popupLabel)
        layout.add_widget(closeButton)
        layout.add_widget(backButton)
        popup = Popup(title='Forget Password', content=layout)
        popup.open()
        backButton.bind(on_press=popup.dismiss, on_release=self.go_to_main)
        closeButton.bind(on_press=popup.dismiss, on_release=self.forget_pass2)

    def forget_pass2(self, instance):
        self.root.transition.direction = "left"
        self.root.current = "forget"

    def change_password(self):
        layout = GridLayout(cols=1, size_hint=(.6, .3), pos_hint={"x": .2, "top": .9}, padding=10)
        popupLabel = Label(text="It will required to re-login after change\npassword.Confirm to proceed?")
        backButton = Button(text="Back")
        closeButton = Button(text="Continue")
        layout.add_widget(popupLabel)
        layout.add_widget(closeButton)
        layout.add_widget(backButton)
        popup = Popup(title='Log Out', content=layout)
        popup.open()
        backButton.bind(on_press=popup.dismiss, on_release=self.go_to_setting)
        closeButton.bind(on_press=popup.dismiss, on_release=self.forget_pass2)

    def update_pass(self):
        fg_email = screen_manager.get_screen('forget').fg_email.text
        fg_passwd = screen_manager.get_screen('forget').fg_passwd.text
        fg_confirm_passwd = screen_manager.get_screen('forget').fg_confirm_passwd.text

        with sqlite3.connect(db_path) as mydb:
            c = mydb.cursor()

            sql = "SELECT email FROM users"
            c.execute(sql)
            result = c.fetchall()

            if (fg_email,) not in result:
                layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                popupLabel = Label(text="Email does not register yet")
                closeButton = Button(text="Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title='Error', content=layout)
                popup.open()
                closeButton.bind(on_press=popup.dismiss)
            elif fg_email == "" or fg_passwd == "" or fg_confirm_passwd == "":
                layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                popupLabel = Label(text="Please fill all the blank.")
                closeButton = Button(text="Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title='Error', content=layout)
                popup.open()
                closeButton.bind(on_press=popup.dismiss)
            else:
                sql2 = "UPDATE users SET password = %s , confirm_password = %s WHERE email = %s"
                var = (fg_passwd, fg_confirm_passwd , fg_email)
                c.execute(sql2, var)

                layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                popupLabel = Label(text="Save/Update successful. Proceed to Login")
                closeButton = Button(text="Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title='Change Password', content=layout)
                popup.open()
                closeButton.bind(on_press=popup.dismiss, on_release=self.go_to_main)


        mydb.commit()

        mydb.close()




    def register(self, *args):
        username = screen_manager.get_screen('register').username.text
        age = screen_manager.get_screen('register').age.text
        weight = screen_manager.get_screen('register').body_weight.text
        height = screen_manager.get_screen('register').body_height.text
        gender = screen_manager.get_screen('register').gender.text
        email = screen_manager.get_screen('register').email.text
        phone = screen_manager.get_screen('register').phone.text
        password = screen_manager.get_screen('register').passwd.text
        confirm_password = screen_manager.get_screen('register').confirm_passwd.text

        username = re.sub(r"\s+", "", username)
        age = re.sub(r"\s+", "", age)
        weight = re.sub(r"\s+", "", weight)
        height = re.sub(r"\s+", "", height)
        gender = re.sub(r"\s+", "", gender)
        email = re.sub(r"\s+", "", email)
        phone = re.sub(r"\s+", "", phone)
        password = re.sub(r"\s+", "", password)
        confirm_password = re.sub(r"\s+", "", confirm_password)


        with sqlite3.connect(db_path) as mydb:

            c = mydb.cursor()

            sql2 = "SELECT name FROM users"
            c.execute(sql2)
            result = c.fetchall()


            if (email,) in result:
                layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                popupLabel = Label(text="Email already exist")
                closeButton = Button(text="Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title='Error', content=layout)
                popup.open()
                closeButton.bind(on_press=popup.dismiss)
            elif password != confirm_password:
                layout = GridLayout(cols = 1,size_hint = (.6,.2), pos_hint = {"x":.2,"top": .9}, padding = 10)
                popupLabel = Label(text = "Password and Confirm Password must same")
                closeButton = Button(text = "Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title = 'Error', content = layout)
                popup.open()
                closeButton.bind(on_press = popup.dismiss)
            elif len(password)<8 or len(confirm_password)<8:
                layout = GridLayout(cols = 1,size_hint = (.6,.3), pos_hint = {"x":.2,"top": .9}, padding = 10)
                popupLabel = Label(text = "Too short for password. Please enter\nat least 8 characters.")
                closeButton = Button(text = "Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title = 'Error', content = layout)
                popup.open()
                closeButton.bind(on_press = popup.dismiss)
            elif username == "" or age == "" or weight == "" or height == "" or gender == "" or email == "" or phone == "" or password == "" or confirm_password == "":
                layout = GridLayout(cols = 1, size_hint = (.6, .2), pos_hint = {"x": .2, "top": .9}, padding = 10)
                popupLabel = Label(text = "Please fill all the blank to register a new account")
                closeButton = Button(text = "Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title = 'Error', content = layout)
                popup.open()
                closeButton.bind(on_press = popup.dismiss)
            else:

                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                match = re.match(pattern, email)
                if match:
                    sql = """INSERT INTO users (name, age, weight, height, gender, email, phone, password, confirm_password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                    record = (username, age, weight, height, gender, email, phone, password, confirm_password)
                    c.execute(sql, record)

                    layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                    popupLabel = Label(text="Register Successful")
                    closeButton = Button(text="Close to continue")
                    layout.add_widget(popupLabel)
                    layout.add_widget(closeButton)
                    popup = Popup(title='Registration', content=layout)
                    popup.open()
                    closeButton.bind(on_press=popup.dismiss)
                    self.root.current = "main"
                else:
                    layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                    popupLabel = Label(text="Email format was wrong")
                    closeButton = Button(text="Close to continue")
                    layout.add_widget(popupLabel)
                    layout.add_widget(closeButton)
                    popup = Popup(title='Error', content=layout)
                    popup.open()
                    closeButton.bind(on_press=popup.dismiss)


        mydb.commit()

        mydb.close()

        screen_manager.get_screen('register').username.text = ""
        screen_manager.get_screen('register').age.text = ""
        screen_manager.get_screen('register').body_weight.text = ""
        screen_manager.get_screen('register').body_height.text = ""
        screen_manager.get_screen('register').gender.text = ""
        screen_manager.get_screen('register').email.text = ""
        screen_manager.get_screen('register').phone.text = ""
        screen_manager.get_screen('register').passwd.text = ""
        screen_manager.get_screen('register').confirm_passwd.text = ""

    def history(self):
        screen_manager.get_screen('history').history_list.clear_widgets()
        with sqlite3.connect(db_path) as mydb:

            c = mydb.cursor()

            app = App.get_running_app()
            user_details = app.user_details


            sql = f"SELECT * FROM results WHERE email = '{user_details['email']}'"
            c.execute(sql)
            result = c.fetchall()

            if result:
                count = 0
                for i in result:
                    count += 1
                    app.results = {'email': i[0], 'symptom': i[1], 'disease': i[2]}
                    results = app.results
                    screen_manager.get_screen('history').history_list.add_widget(History(text="NO." + str(count) + ":\n" + results['symptom']))
                    screen_manager.get_screen('history').history_list.add_widget(History(text=results['disease']))


            else:
                layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                popupLabel = Label(text="You have no done prediction yet")
                closeButton = Button(text="Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title='Error', content=layout)
                popup.open()
                closeButton.bind(on_press=popup.dismiss, on_release=self.go_to_content)


        mydb.commit()

        mydb.close()

    def profile(self):

        app = App.get_running_app()
        user_details = app.user_details

        screen_manager.get_screen('profile').username.text = f': {user_details["name"]}'
        screen_manager.get_screen('profile').age.text = f': {user_details["age"]}'
        screen_manager.get_screen('profile').body_weight.text = f': {user_details["weight"]}'
        screen_manager.get_screen('profile').body_height.text = f': {user_details["height"]}'
        screen_manager.get_screen('profile').gender.text = f': {user_details["gender"]}'
        screen_manager.get_screen('profile').email.text = f': {user_details["email"]}'
        screen_manager.get_screen('profile').phone.text = f': {user_details["phone"]}'


    def update_profile_detail(self):
        self.root.transition.direction = "left"
        self.root.current = "updatepro"


    def update_profile(self):
        up_username = screen_manager.get_screen('updatepro').username.text
        up_age = screen_manager.get_screen('updatepro').age.text
        up_weight = screen_manager.get_screen('updatepro').body_weight.text
        up_height = screen_manager.get_screen('updatepro').body_height.text
        up_gender = screen_manager.get_screen('updatepro').gender.text
        up_phone = screen_manager.get_screen('updatepro').phone.text

        up_username = re.sub(r"\s+", "", up_username)
        up_age = re.sub(r"\s+", "", up_age)
        up_weight = re.sub(r"\s+", "", up_weight)
        up_height = re.sub(r"\s+", "", up_height)
        up_gender = re.sub(r"\s+", "", up_gender)
        up_phone = re.sub(r"\s+", "", up_phone)


        with sqlite3.connect(db_path) as mydb:

            c = mydb.cursor()

            app = App.get_running_app()
            user_details = app.user_details


            if up_username == "" or up_age == "" or up_weight == "" or up_height == "" or up_gender == "" or up_phone == "":
                layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                popupLabel = Label(text="Please fill all the blank to register a new account")
                closeButton = Button(text="Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title='Error', content=layout)
                popup.open()
                closeButton.bind(on_press=popup.dismiss)
            else:

                sql2 = (f"UPDATE users SET name = %s, age = %s, weight = %s, height = %s, gender = %s, phone = %s WHERE email = '{user_details['email']}'")
                var = (up_username, up_age, up_weight, up_height, up_gender, up_phone)
                c.execute(sql2, var)

                layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                popupLabel = Label(text="Save/Update successful")
                closeButton = Button(text="Close to continue")
                layout.add_widget(popupLabel)
                layout.add_widget(closeButton)
                popup = Popup(title='Edit/Update Details', content=layout)
                popup.open()
                closeButton.bind(on_press=popup.dismiss)


        mydb.commit()

        mydb.close()


    def toggle_visibility(self):
        if screen_manager.get_screen('main').passwd.password == True:
            screen_manager.get_screen('main').passwd.password = False
            screen_manager.get_screen('main').btn_log.text = "Hide"
        elif screen_manager.get_screen('main').passwd.password == False:
            screen_manager.get_screen('main').passwd.password = True
            screen_manager.get_screen('main').btn_log.text = "Show"

        if screen_manager.get_screen('register').passwd.password == True:
            screen_manager.get_screen('register').passwd.password = False
            screen_manager.get_screen('register').btn_p.text = "Hide"
        elif screen_manager.get_screen('register').passwd.password == False:
            screen_manager.get_screen('register').passwd.password = True
            screen_manager.get_screen('register').btn_p.text = "Show"

        if screen_manager.get_screen('register').confirm_passwd.password == True:
            screen_manager.get_screen('register').confirm_passwd.password = False
            screen_manager.get_screen('register').btn_cp.text = "Hide"
        elif screen_manager.get_screen('register').confirm_passwd.password == False:
            screen_manager.get_screen('register').confirm_passwd.password = True
            screen_manager.get_screen('register').btn_cp.text = "Show"

        if screen_manager.get_screen('forget').fg_passwd.password == True:
            screen_manager.get_screen('forget').fg_passwd.password = False
            screen_manager.get_screen('forget').btn_fg_p.text = "Hide"
        elif screen_manager.get_screen('forget').fg_passwd.password == False:
            screen_manager.get_screen('forget').fg_passwd.password = True
            screen_manager.get_screen('forget').btn_fg_p.text = "Show"

        if screen_manager.get_screen('forget').fg_confirm_passwd.password == True:
            screen_manager.get_screen('forget').fg_confirm_passwd.password = False
            screen_manager.get_screen('forget').btn_fg_cp.text = "Hide"
        elif screen_manager.get_screen('forget').fg_confirm_passwd.password == False:
            screen_manager.get_screen('forget').fg_confirm_passwd.password = True
            screen_manager.get_screen('forget').btn_fg_cp.text = "Show"


    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
        return sentence_words

    def bag_of_words(self, sentence):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(words)
        for w in sentence_words:
            for i, word in enumerate(words):
                if word == w:
                    bag[i] = 1
        return np.array(bag)


    def predict_class(self, sentence):
        bow = self.bag_of_words(sentence)
        res = model.pred(np.array([bow]))[0]
        ERROR_THRESHOLD = 0.20
        result = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

        result.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in result:
            return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
        return return_list


    def response(self, intents_list, intents_json, intents_json2, intents_json3):
        tag = intents_list[0]['intent']

        list_intents = intents_json['intents']
        list_intents2 = intents_json2['description_intents']
        list_intents3 = intents_json3['precaution_intents']



        for i in list_intents:
            for j in list_intents2:
                for k in list_intents3:
                    if i['tag'] == tag:
                        result = random.choice(i['responses'])
                        break
                    elif j['tag'] == tag:
                        result = random.choice(j['responses'])
                        break
                    elif k['tag'] == tag:
                        result = random.choice(k['responses'])
        return result


    print("Bot is running!")



    def send(self):
        global size, halign, valign

        with sqlite3.connect(db_path) as mydb:
            c = mydb.cursor()

            app = App.get_running_app()
            user_details = app.user_details


            message = screen_manager.get_screen('content').text_input.text
            ints = self.predict_class(message)
            res = self.response(ints, intents, description_intents, precaution_intents)
            tag = ints[0]['intent']

            if  screen_manager.get_screen('content').text_input != "":
                if len(message) < 6:
                    size = .22, None
                    halign = "center"
                    valign = "middle"
                elif len(message) < 11:
                    size = .32, None
                    halign = "center"
                    valign = "middle"
                elif len(message) < 16:
                    size = .45, None
                    halign = "center"
                    valign = "middle"
                elif len(message) < 21:
                    size = .58, None
                    halign = "center"
                    valign = "middle"
                elif len(message) < 26:
                    size = .71, None
                    halign = "center"
                    valign = "middle"
                else:
                    size = .77, None
                    halign = "left"
                    valign = "middle"


            screen_manager.get_screen('content').chat_list.add_widget(Command(text=message, size_hint=size, halign=halign))


            if tag == 'symptoms':

                list_m = message.split(',')
                psymptoms = [message.replace(' ','_') for message in list_m]


                a = np.array(df1["Symptom"])
                b = np.array(df1["weight"])

                for j in range(len(psymptoms)):
                    for k in range(len(a)):
                        if psymptoms[j] == a[k]:
                            psymptoms[j] = b[k]

                if len(psymptoms) < 2:
                    layout = GridLayout(cols=1, size_hint=(.6, .2), pos_hint={"x": .2, "top": .9}, padding=10)
                    popupLabel = Label(text="Please enter at least two symptoms for prediction.")
                    closeButton = Button(text="Close to continue")
                    layout.add_widget(popupLabel)
                    layout.add_widget(closeButton)
                    popup = Popup(title='Symptom Quantity', content=layout)
                    popup.open()
                    closeButton.bind(on_press=popup.dismiss)
                elif len(psymptoms) == 2:
                    nulls = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 3:
                    nulls = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 4:
                    nulls = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 5:
                    nulls = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 6:
                    nulls = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 7:
                    nulls = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 8:
                    nulls = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 9:
                    nulls = [0, 0, 0, 0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 10:
                    nulls = [0, 0, 0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 11:
                    nulls = [0, 0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 12:
                    nulls = [0, 0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 13:
                    nulls = [0, 0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 14:
                    nulls = [0, 0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 15:
                    nulls = [0, 0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 16:
                    nulls = [0]
                    psymptoms.extend(nulls)
                elif len(psymptoms) == 17:
                    pass

                try:
                    array_symptom = np.array(psymptoms)
                    array_symptom_2d = array_symptom.reshape(1,-1)

                    preds = model2.predict(array_symptom_2d)
                    predstr = ",".join(preds)
                    predstr = predstr.lower().replace("[]","")

                    screen_manager.get_screen('content').chat_list.add_widget(Response(text="Prediction Result: Disease " + str(predstr) + " you got infected.", size_hint=(.65, None)))
                    screen_manager.get_screen('content').chat_list.add_widget(Response(text="Average score for this prediction model: " + "average 95%", size_hint=(.65, None)))

                    sql = """INSERT INTO results (email, symptom, disease) VALUES (?, ?, ?)"""
                    record = (user_details['email'], message, str(predstr))
                    c.execute(sql, record)


                except Exception:
                    symptom_list = ["itching", "skin rash", "nodal skin eruptions", "continuous sneezing", "shivering",
                                    "chills",
                                    "joint pain", "stomach pain", "acidity", "ulcers on tongue", "muscle wasting",
                                    "vomiting",
                                    "burning micturition", "spotting urination", "fatigue", "weight gain", "anxiety",
                                    "cold hands and feets", "mood swings", "weight loss", "restlessness", "lethargy",
                                    "patches in throat", "irregular sugar level", "cough", "high fever", "sunken eyes",
                                    "breathlessness", "sweating", "dehydration", "indigestion",
                                    "headache", "yellowish skin", "dark urine", "nausea", "loss of appetite",
                                    "pain behind the eyes", "back pain", "constipation", "abdominal pain", "diarrhoea",
                                    "mild fever", "yellow urine", "yellowing of eyes", "acute liver failure",
                                    "fluid overload",
                                    "swelling of stomach", "swelled lymph nodes", "malaise", "blurred and distorted vision",
                                    "phlegm", "throat irritation", "redness of eyes", "sinus pressure", "runny nose",
                                    "congestion",
                                    "chest pain", "weakness in limbs", "fast heart rate", "pain during bowel movements",
                                    "pain in anal region", "bloody stool", "irritation in anus", "neck pain", "dizziness",
                                    "cramps",
                                    "bruising", "obesity", "swollen legs", "swollen blood vessels", "puffy face and eyes",
                                    "enlarged thyroid", "brittle nails", "swollen extremeties", "excessive hunger",
                                    "extra marital contacts", "drying and tingling lips", "slurred speech", "knee pain",
                                    "hip joint pain", "muscle weakness", "stiff neck", "swelling joints",
                                    "movement stiffness",
                                    "spinning movements", "loss of balance", "unsteadiness", "weakness of one body side",
                                    "loss of smell", "bladder discomfort", "foul smell ofurine", "continuous feel of urine",
                                    "passage of gases", "internal itching", "toxic look (typhos)", "depression",
                                    "irritability",
                                    "muscle pain", "altered sensorium", "red spots over body", "belly pain",
                                    "abnormal menstruation", "dischromic patches", "watering from eyes",
                                    "increased appetite",
                                    "polyuria", "family history", "mucoid sputum", "rusty sputum", "lack of concentration",
                                    "visual disturbances", "receiving blood transfusion", "receiving unsterile injections",
                                    "coma", "stomach bleeding", "distention of abdomen", "history of alcohol consumption",
                                    "blood in sputum", "prominent veins on calf", "palpitations", "painful walking",
                                    "pus filled pimples", "blackheads", "scurring", "skin peeling", "silver like dusting",
                                    "small dents in nails", "inflammatory nails", "blister", "red sore around nose",
                                    "yellow crust ooze"]
                    symptom_str = ",".join(symptom_list)
                    screen_manager.get_screen('content').chat_list.add_widget(Response(text=str(symptom_str), size_hint=(.80, None)))
                    screen_manager.get_screen('content').chat_list.add_widget(Response(text="Use the given relevant symptom as above provided without space between comma only for prediction. Eg: Itching (Not itchy/itchings)", size_hint=(.80, None)))


            elif tag == 'datetime':
                screen_manager.get_screen('content').chat_list.add_widget(Response(text=now.strftime("%A \n%d %B %Y \n%H:%M:%S"), size_hint=(.65, None)))
            elif len(message) == 0 or tag != ints[0]['intent']:
                screen_manager.get_screen('content').chat_list.add_widget(Response(text="What are you going to ask?", size_hint=(.65, None)))
            elif tag == 'goodbye':
                screen_manager.get_screen('content').chat_list.add_widget(Response(text=res, size_hint=(.65, None)))
                url = "https://docs.google.com/forms/d/e/1FAIpQLScpxmn2ZjA4YlngPctl9sSXLyOReiJmf28nNj-RgGjgSusEgg/viewform?usp=sf_link"
                label = Label(text="Click here to give us feedback", size_hint=(.65, None), color=(0, 0, 1, 1), underline=True)
                label.url = url
                screen_manager.get_screen('content').chat_list.add_widget(label)
            else:
                screen_manager.get_screen('content').chat_list.add_widget(Response(text=res, size_hint=(.65, None)))



            screen_manager.get_screen('content').text_input.text = ""

        mydb.commit()

        mydb.close()



if __name__ == "__main__":
    parentApp().run()
