from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import json

with open("intents.json") as file:
    data = json.load(file)

texts = []
labels = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        texts.append(pattern)
        labels.append(intent["tag"])

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

def predict_intent(user_input):
    X_test = vectorizer.transform([user_input])
    probs = model.predict_proba(X_test)[0]
    return model.classes_[probs.argmax()], max(probs)