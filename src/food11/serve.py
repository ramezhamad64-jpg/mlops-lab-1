import io
import os

import mlflow
import mlflow.pyfunc
import numpy as np
from fastapi import FastAPI, File, UploadFile
from PIL import Image


CLASS_NAMES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]


MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

app = FastAPI(title="Food11 API")

model = mlflow.pyfunc.load_model("models:/food11@champion")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()

    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image = image.resize((128, 128))

    array = np.asarray(image).astype("float32") / 255.0
    array = np.transpose(array, (2, 0, 1))
    array = np.expand_dims(array, axis=0)

    result = model.predict(array)
    result = np.asarray(result)

    logits = result[0] if result.ndim == 2 else result

    exp = np.exp(logits - np.max(logits))
    probabilities = exp / exp.sum()

    class_id = int(np.argmax(probabilities))
    confidence = float(probabilities[class_id])

    return {
        "category": CLASS_NAMES[class_id],
        "confidence": confidence,
    }