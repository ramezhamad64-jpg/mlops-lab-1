import mlflow
import mlflow.pytorch
from mlflow import MlflowClient

OLD_MODEL = "/old_mlruns/1/models/m-297b7ecb4f3d4ca586691f5d787f36bb/artifacts"

mlflow.set_tracking_uri("http://mlflow:5000")

print("Loading old model...")
model = mlflow.pytorch.load_model(OLD_MODEL)

mlflow.set_experiment("food11-compose")

with mlflow.start_run() as run:
    info = mlflow.pytorch.log_model(
        model,
        name="model",
        serialization_format="pickle",
    )
    print("Logged:", info.model_uri)

registered = mlflow.register_model(info.model_uri, "food11")

client = MlflowClient()
client.set_registered_model_alias(
    "food11",
    "champion",
    registered.version,
)

print("DONE")
print("food11 version:", registered.version)
print("alias: champion")
