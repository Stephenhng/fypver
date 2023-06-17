#FYP Project: A System For Disease Prediction Based On Symptom Using Artificial Intelligence
#H'ng Sheng Wei 69803
from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import uvicorn
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn import model_selection
from starlette.middleware.cors import CORSMiddleware


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


class Symptom(BaseModel):
    symptom1: int
    symptom2: int
    symptom3: int
    symptom4: int
    symptom5: int
    symptom6: int
    symptom7: int
    symptom8: int
    symptom9: int
    symptom10: int
    symptom11: int
    symptom12: int
    symptom13: int
    symptom14: int
    symptom15: int
    symptom16: int
    symptom17: int


with open("rfc_model.pkl", "rb") as f:
    model = pickle.load(f)


@app.get('/')
def index():
    return {'message': 'This is the homepage of the API '}

df = pd.read_csv('Data/dataset.csv')
df1 = pd.read_csv('MasterData/Symptom_Severity.csv')
df.isna().sum()
df.isnull().sum()
cols = df.columns
data = df[cols].values.flatten()

s = pd.Series(data)
s = s.str.strip()
s = s.values.reshape(df.shape)

df = pd.DataFrame(s, columns=df.columns)
df = df.fillna(0)
vals = df.values
symptoms = df1['Symptom'].unique()

for i in range(len(symptoms)):
    vals[vals == symptoms[i]] = df1[df1['Symptom'] == symptoms[i]]['weight'].values[0]
d = pd.DataFrame(vals, columns=cols)
d = d.replace('dischromic _patches', 0)
d = d.replace('spotting_ urination',0)
df = d.replace('foul_smell_of urine',0)
(df[cols] == 0).all()
df['Disease'].value_counts()
df['Disease'].unique()
data = df.iloc[:,1:].values
labels = df['Disease'].values
x_train, x_test, y_train, y_test = model_selection.train_test_split(data, labels, shuffle=True, train_size = 0.85)


model2 = RandomForestClassifier()
model2.fit(x_train,y_train)



@app.post('/prediction')
def get_symptom_category(data: Symptom):
    input = data.json()
    input_dict = json.loads(input)

    symptom1 = input_dict['symptom1']
    symptom2 = input_dict['symptom2']
    symptom3 = input_dict['symptom3']
    symptom4 = input_dict['symptom4']
    symptom5 = input_dict['symptom5']
    symptom6 = input_dict['symptom6']
    symptom7 = input_dict['symptom7']
    symptom8 = input_dict['symptom8']
    symptom9 = input_dict['symptom9']
    symptom10 = input_dict['symptom10']
    symptom11 = input_dict['symptom11']
    symptom12 = input_dict['symptom12']
    symptom13 = input_dict['symptom13']
    symptom14 = input_dict['symptom14']
    symptom15 = input_dict['symptom15']
    symptom16 = input_dict['symptom16']
    symptom17 = input_dict['symptom17']

    input_list = [symptom1, symptom2, symptom3, symptom4, symptom5, symptom6, symptom7, symptom8, symptom9, symptom10, symptom11, symptom12, symptom13, symptom14, symptom15, symptom16, symptom17]

    pred_name = model.predict([[symptom1, symptom2, symptom3, symptom4, symptom5, symptom6, symptom7, symptom8, symptom9, symptom10, symptom11, symptom12, symptom13, symptom14, symptom15, symptom16, symptom17]]).tolist()[0]


    return {'prediction': pred_name}


@app.get('/predict')
def get_cat(symptom1: int, symptom2: int, symptom3: int, symptom4: int, symptom5: int, symptom6: int, symptom7: int, symptom8: int, symptom9: int, symptom10: int, symptom11: int, symptom12: int, symptom13: int, symptom14: int, symptom15: int, symptom16: int, symptom17: int):
    input_list = [symptom1, symptom2, symptom3, symptom4, symptom5, symptom6, symptom7, symptom8, symptom9, symptom10, symptom11, symptom12, symptom13, symptom14, symptom15, symptom16, symptom17]

    pred_name = model.predict([[symptom1, symptom2, symptom3, symptom4, symptom5, symptom6, symptom7, symptom8, symptom9, symptom10, symptom11, symptom12, symptom13, symptom14, symptom15, symptom16, symptom17]]).tolist()[0]

    rfc_result = model2.score(x_test, y_test)
    accuracy_str = str(rfc_result * 100)
    result_string = pred_name + ", Accuracy for this model: " + accuracy_str
    return {'prediction': result_string}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)



