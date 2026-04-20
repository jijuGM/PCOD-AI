import joblib
import pandas as pd

# Load model
model = joblib.load("pcos_model.joblib")

def predict_pcos(user_data):

    df = pd.DataFrame([user_data])

    df = pd.get_dummies(df)

    prediction = model.predict(df)[0]

    probability = model.predict_proba(df)[0][1]

    return {
        "prediction": int(prediction),
        "probability": float(probability)
    }