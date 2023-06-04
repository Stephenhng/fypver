import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn import model_selection

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

print("for rfc: ")
rfc_result = model2.score(x_test, y_test)
print(rfc_result)
rfc_score = cross_val_score(model2, x_test, y_test, cv=10)
print(rfc_score)


filename = 'rfc_model.pkl'
pickle.dump(model2, open(filename,'wb'))



print("Done")