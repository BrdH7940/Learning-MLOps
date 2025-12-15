from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import numpy as np
from typing import List
import os
import uvicorn

app = FastAPI(title="Iris Classification API", version="1.0.0")

# Load model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "iris_model.pkl")
model = None


class PredictionInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


class PredictionOutput(BaseModel):
    prediction: int
    class_name: str
    confidence: float


def load_model():
    global model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("Model loaded successfully")


@app.on_event("startup")
async def startup_event():
    load_model()


@app.get("/")
async def root():
    return {
        "message": "Iris Classification API",
        "status": "running",
        "endpoints": {"health": "/health", "predict": "/predict", "docs": "/docs"},
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}


@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Prepare input
    features = np.array(
        [
            [
                input_data.sepal_length,
                input_data.sepal_width,
                input_data.petal_length,
                input_data.petal_width,
            ]
        ]
    )

    # Make prediction
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    confidence = float(max(probabilities))

    # Class names
    class_names = ["setosa", "versicolor", "virginica"]

    return PredictionOutput(
        prediction=int(prediction),
        class_name=class_names[prediction],
        confidence=confidence,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
