from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import uvicorn
import json
import nltk
import numpy as np
import random
import os
from starlette.middleware.cors import CORSMiddleware
from nltk.stem import WordNetLemmatizer
from model import TensorFlowModel
from nltk.corpus import wordnet

nltk.download("punkt")
nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())
description_intents = json.loads(open('description_intents.json').read())
precaution_intents = json.loads(open('precaution_intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

now = datetime.now()

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Massage(BaseModel):
    sentence: str


model = TensorFlowModel()
model.load(os.path.join(os.getcwd(), 'model.tflite'))


@app.get('/')
def index():
    return {'message': 'This is the homepage of the API '}


def is_good_word(sentence: str):
    wordnet.ensure_loaded()


def clean_up_sentence(sentence: str):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence: str):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence: str):
    bow = bag_of_words(sentence)
    res = model.pred(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.20
    result = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    result.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in result:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def response(intents_list, intents_json, intents_json2, intents_json3):
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


@app.get('/response')
def get_cat(sentence: str):

    ints = predict_class(sentence)
    res = response(ints, intents, description_intents, precaution_intents)
    tag = ints[0]['intent']

    if tag == 'datetime':
        return {'response': now.strftime("%A \n%d %B %Y \n%H:%M:%S")}
    elif len(sentence) == 0 or tag != ints[0]['intent']:
        return {'response': "What are you going to ask?"}
    elif tag == 'feedback':
        resp = "Thank you for your feedback!\nProvide feedback by clicking the link above.\n"
        return {'response': resp}
    else:
        return {'response': res}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)