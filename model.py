import pandas as pd
import numpy as np

# Preprocessing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Models
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# Evaluation
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

import warnings
warnings.simplefilter("ignore")


df = pd.read_csv(r"C:\Users\GUDIYA\Downloads\Loan_Prediction.csv")


X = df[["age","income","loan_amount","credit_score","employment_years","existing_loans","marital_status","education"]]

y = df["loan_approved"]

marital_le = LabelEncoder()
education_le = LabelEncoder()

X["marital_status"] = marital_le.fit_transform(X["marital_status"])
X["education"] = education_le.fit_transform(X["education"])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)



scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

import pickle

# After training the model
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))

y_pred = model.predict(X_test)



print("Accuracy:", accuracy_score(y_test, y_pred))

print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

print("\nClassification Report:\n", classification_report(y_test, y_pred))


sample = [[30, 60000, 15000, 700, 5, 1, 1, 2]]

sample = scaler.transform(sample)

prediction = model.predict(sample)

if prediction[0] == 1:
    print("Loan Approved")
else:
    print("Loan Rejected")


