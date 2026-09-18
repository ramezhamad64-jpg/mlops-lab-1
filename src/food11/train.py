import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["processed", "mini"], default="mini")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--batch-size", type=int, default=32)
    return parser.parse_args()


def evaluate(model, loader, criterion, device):
    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)

            predictions = outputs.argmax(dim=1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    average_loss = total_loss / total if total > 0 else 0.0
    accuracy = correct / total if total > 0 else 0.0

    return average_loss, accuracy


def main():
    args = parse_args()

    project_root = Path(__file__).resolve().parents[2]

    if args.dataset == "mini":
        data_dir = project_root / "data" / "food11_processed_mini"
    else:
        data_dir = project_root / "data" / "food11_processed"

    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ])

    train_dataset = datasets.ImageFolder(
        data_dir / "training",
        transform=transform,
    )

    val_dataset = datasets.ImageFolder(
        data_dir / "validation",
        transform=transform,
    )

    test_dataset = datasets.ImageFolder(
        data_dir / "evaluation",
        transform=transform,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
    )

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("Using device:", device)

    model = models.resnet18(
        weights=models.ResNet18_Weights.DEFAULT
    )

    model.fc = nn.Linear(
        model.fc.in_features,
        11,
    )

    model = model.to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.lr,
    )

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("food11")

    with mlflow.start_run() as run:
        print("MLflow run ID:", run.info.run_id)

        mlflow.log_params({
            "dataset": args.dataset,
            "epochs": args.epochs,
            "lr": args.lr,
            "batch_size": args.batch_size,
            "device": str(device),
        })

        for epoch in range(args.epochs):
            model.train()

            total_loss = 0.0
            total_samples = 0

            for images, labels in train_loader:
                images = images.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                outputs = model(images)
                loss = criterion(outputs, labels)

                loss.backward()
                optimizer.step()

                total_loss += loss.item() * images.size(0)
                total_samples += images.size(0)

            train_loss = (
                total_loss / total_samples
                if total_samples > 0
                else 0.0
            )

            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device,
            )

            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch,
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} "
                f"- train_loss={train_loss:.4f} "
                f"- val_loss={val_loss:.4f} "
                f"- val_accuracy={val_accuracy:.4f}"
            )

        test_loss, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device,
        )

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy,
        )

        mlflow.pytorch.log_model(
            model,
            name="model",
            serialization_format="pickle",
        )

        print(f"Final test loss: {test_loss:.4f}")
        print(f"Final test accuracy: {test_accuracy:.4f}")
        print("Model saved to MLflow successfully.")


if __name__ == "__main__":
    main()