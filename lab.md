# Lab 1 - Git/DVC and Data Preparation

## Questions and Answers

### Question 1
**Observe the files created by `uv init`. What do you think they contain?**

The `uv init` command initializes a Python project and creates the basic project structure.

The main files are:

- `pyproject.toml`: contains project metadata such as the project name, Python version requirement, and dependencies.
- `.python-version`: specifies the default Python version used by the project.
- `README.md`: contains documentation about the project.
- `src/`: contains the Python source code of the project.

Some files such as `uv.lock` and the `.venv` virtual environment may be created later when dependencies are installed or when the project is first run.

---

### Question 2
**What files are created by `dvc init`? What are they used for? Which ones should be pushed to Git?**

The `dvc init` command initializes DVC inside the Git repository.

It creates:

- `.dvc/`: contains DVC configuration and internal project information.
- `.dvc/config`: contains repository-level DVC configuration, such as the configured remote.
- `.dvc/.gitignore`: prevents DVC internal cache and temporary files from being tracked by Git.
- `.dvcignore`: tells DVC which files or directories it should ignore.

The DVC configuration files should be committed to Git so that the DVC setup can be shared with other developers.

Temporary files, caches, and sensitive credentials should not be committed.

---

### Question 3
**Where are the credentials stored? What options are available other than `--global`? Should the credentials be pushed to GitHub?**

When the `--global` option is used, the DVC credentials are stored in the user's global DVC configuration on the local machine instead of inside the Git repository.

Other configuration scopes include:

- Repository configuration: stored in `.dvc/config`.
- `--local`: stores machine-specific repository configuration in `.dvc/config.local`.
- `--global`: stores configuration for the current user.
- `--system`: stores system-wide configuration.

Credentials such as usernames, passwords, or access tokens should never be committed or pushed to GitHub.

Only non-sensitive configuration, such as the default DVC remote name, should be committed.

---

### Question 4
**Take a look at the `.gitignore` file. Explain what happened after running `dvc add data`.**

After running:

`dvc add data`

DVC starts tracking the `data` directory.

DVC adds the actual data directory to `.gitignore` so that Git does not track the dataset files directly.

This is necessary because Git should track the source code and DVC metadata, while DVC is responsible for storing and versioning the large data files.

Therefore:

- Git tracks `data.dvc`.
- DVC tracks the actual contents of the `data` directory.

---

### Question 5
**Do you see a `.dvc` file? What does it contain?**

Yes. After running:

`dvc add data`

DVC creates a file called:

`data.dvc`

This file is a small metadata file that represents the tracked `data` directory.

It contains information such as:

- the path of the tracked data,
- a hash that identifies the exact version of the data,
- the total size of the data,
- and possibly the number of files.

The actual images are not stored inside `data.dvc`.

The file acts as a pointer to a specific version of the data stored in the DVC cache and remote storage.

---

### Question 6
**What do you see on GitHub and DagsHub? Is the code there? Is the data there? Is there a file that points to the data?**

On GitHub, I can see the project source code, Git configuration files, and the `data.dvc` metadata file.

The actual dataset files are not stored in GitHub because the `data` directory is ignored by Git.

The `data.dvc` file identifies the exact version of the dataset tracked by DVC.

After running:

`dvc push`

the actual data is uploaded to the configured DVC remote on DagsHub.

Therefore:

- GitHub stores the code and DVC metadata.
- DagsHub's DVC storage contains the actual dataset objects.
- `data.dvc` connects a Git commit to the corresponding version of the data.

---

### Question 7
**After cloning the repository into a new temporary folder, do you see the data folder? What DVC command is needed to get the data?**

After cloning the GitHub repository, the actual dataset is not downloaded automatically.

The repository contains the source code and the `data.dvc` metadata file, but not the dataset files themselves.

To download the data from the configured DVC remote and restore it into the working directory, the following command is used:

`dvc pull`

This downloads the required data from DagsHub and restores the `data` directory.

---

### Question 8
**After checking out an old commit and running `dvc checkout`, do you still see `food11_processed` and `food11_processed_mini`?**

No.

After checking out an older Git commit, the older version of `data.dvc` becomes active.

When I run:

`dvc checkout`

DVC updates the local data directory so that it matches the version described by that older `data.dvc` file.

Since the older dataset version was created before `food11_processed` and `food11_processed_mini` were added, these two folders disappear.

After returning to the `main` branch and running:

`dvc checkout`

again, DVC restores the latest version of the data, including:

- `food11_raw`
- `food11_processed`
- `food11_processed_mini`

This demonstrates how Git versions the DVC metadata while DVC versions the actual data.
# Lab 2 - Model Training and Experiment Tracking with MLflow

## Questions and Answers

### Question 1
**Look at `pyproject.toml` and `uv.lock`. What changed?**

After running:

`uv add mlflow torch torchvision scikit-learn`

the `pyproject.toml` file was updated to include these new project dependencies.

The `uv.lock` file was also updated. It contains the exact resolved versions of the direct dependencies and their transitive dependencies, which helps make the environment reproducible.

---

### Question 2
**What is `--backend-store-uri` used for? What is `--default-artifact-root` used for? What is the difference between the metadata MLflow stores and the artifacts it stores?**

`--backend-store-uri` defines where MLflow stores structured tracking metadata.

In this lab:

`sqlite:///mlflow.db`

means that MLflow stores metadata in a local SQLite database called `mlflow.db`.

This metadata includes information such as:

- experiments,
- runs,
- parameters,
- metrics,
- tags,
- run status,
- timestamps.

`--default-artifact-root` defines where MLflow stores artifacts generated by runs.

In this lab:

`./mlruns`

is used as the local artifact storage location.

Artifacts are actual files produced by a run, such as:

- trained models,
- plots,
- images,
- configuration files,
- other output files.

Therefore, metadata is structured tracking information about a run, while artifacts are the actual files produced by that run.

---

### Question 3
**Why shouldn't `mlflow.db` and `mlruns/` be tracked by Git, and why shouldn't they be tracked by DVC either?**

`mlflow.db` and `mlruns/` are local runtime outputs generated by MLflow.

They should not be tracked by Git because they can change after every training run, can become large, and are not part of the project source code.

They should also not be tracked by DVC because DVC is being used in this project to version the datasets, while MLflow is responsible for experiment tracking and model artifacts.

Therefore, these files are kept local and added to `.gitignore`.

---

### Question 4
**What happens the first time you call `set_experiment` with a name that doesn't exist yet?**

When the following command is called:

`mlflow.set_experiment("food11")`

and the experiment does not already exist, MLflow automatically creates a new experiment named `food11`.

After the first training run, the `food11` experiment appeared in the MLflow UI and the training runs were logged under it.

---

### Question 5
**What is the difference between `mlflow.log_param` and `mlflow.log_metric`? Why does `log_metric` take a `step` argument and `log_param` doesn't?**

`mlflow.log_param` is used for values that are fixed for the entire run.

Examples include:

- learning rate,
- batch size,
- number of epochs,
- dataset choice.

These values are normally defined before training begins and do not change during the run.

`mlflow.log_metric` is used for values produced during training or evaluation.

Examples include:

- training loss,
- validation loss,
- validation accuracy,
- test accuracy.

Metrics can change over time.

The `step` argument is used with metrics to identify the training step or epoch at which the value was recorded.

For example, validation accuracy can be logged once for each epoch.

Parameters do not need a `step` because they remain constant throughout the run.

---

### Question 6
**Open the run in the MLflow UI. Find the params, the metric charts, and the logged model artifact. Where does the model artifact actually live on disk?**

In the MLflow UI, the run contains the logged parameters, metrics, and trained model.

The parameters include:

- `dataset`
- `epochs`
- `lr`
- `batch_size`
- `device`

The metrics include:

- `train_loss`
- `val_loss`
- `val_accuracy`
- `test_accuracy`

The trained model is also visible as a logged model artifact.

Because the MLflow server was started with:

`--default-artifact-root ./mlruns`

the model artifact is stored locally inside the project's `mlruns` directory, under MLflow's experiment and run-specific artifact structure.

---

### Question 7
**Which learning rate gave the best `val_accuracy`? Is higher always better?**

Among the tested learning rates, `0.0001` gave the best final validation accuracy.

The run with:

- learning rate: `0.0001`
- batch size: `32`

reached a final validation accuracy of approximately:

`0.7199`

The higher learning rate `0.01` performed much worse and reached only approximately:

`0.1560`

validation accuracy.

Therefore, a higher learning rate is not always better. If the learning rate is too high, the optimizer can make updates that are too large and training performance can become worse.

---

### Question 8
**What pattern do you see in the parallel coordinates plot for `lr`, `batch_size`, and `val_accuracy`?**

The results show that the learning rate had a strong effect on validation accuracy.

The tested configurations produced approximately the following results:

- `lr = 0.01`, batch size `32` → `val_accuracy = 0.1560`
- `lr = 0.001`, batch size `32` → `val_accuracy = 0.5776`
- `lr = 0.0001`, batch size `32` → `val_accuracy = 0.7199`
- `lr = 0.001`, batch size `64` → `val_accuracy = 0.5547`

The best result was obtained with the smallest tested learning rate, `0.0001`.

For the two runs using learning rate `0.001`, increasing the batch size from `32` to `64` slightly reduced the final validation accuracy.

These experiments suggest that the learning rate had a larger effect on validation accuracy than the tested batch size change. However, only a small number of configurations were tested, so this pattern should not be considered a general rule.

---

### Question 9
**Which run is the best one? Note its run ID.**

After comparing the runs and sorting them by final `val_accuracy`, the best run was:

- Run name: `omniscient-frog-486`
- Learning rate: `0.0001`
- Batch size: `32`
- Epochs: `5`
- Final validation accuracy: approximately `0.7199`
- Final test accuracy: approximately `0.7473`
- Run ID: `7694b83f9fa545c88333680f639bbfca`

This run had the highest final validation accuracy among the tested configurations.
# Lab 3 - Model Serving with FastAPI and Docker

## Q1
The best model was registered in the MLflow Model Registry under the name `food11`.

Registered model version: **Version 1**

A logged model artifact is associated with a specific MLflow run and contains the saved model files. A registered model is a model managed through the MLflow Model Registry, where it can have versions and aliases and can be used for deployment.

## Q2
I assigned the alias `champion` to Version 1 of the `food11` registered model.

An MLflow model version is a numbered, immutable version of a registered model. An alias is a human-readable pointer such as `champion` that can be reassigned to another model version later.

Using an alias makes deployment easier because the serving code does not need to be changed when a newer model becomes the production model.

## Q3
The FastAPI service loads the model using:

`models:/food11@champion`

This URI is useful because the serving application refers to the `champion` alias instead of a fixed version number. If the alias is moved to a newer model version, the serving code can remain unchanged.

The API provides:

- `GET /health`
- `POST /predict`

The `/health` endpoint returned:

`{"status":"ok"}`

The `/predict` endpoint was tested with a Food-11 image and returned:

`{"category":"Egg","confidence":0.6829885244369507}`

The prediction being different from the true class does not indicate a serving failure; the API successfully loaded the model and returned an inference result.

## Q4
The Dockerfile uses a multi-stage build.

The builder stage installs the Python dependencies and creates the virtual environment. The runtime stage copies only the virtual environment and application source code needed to run the API.

Docker layer caching is improved by copying dependency files such as `pyproject.toml` and `uv.lock` before copying the application source code. Therefore, changing only the source code does not require all dependencies to be installed again.

## Q5
The final Docker image was inspected with:

`docker images food11-api`

The resulting image was:

- Image: `food11-api:latest`
- Disk usage: **2.08 GB**
- Content size: **443 MB**

`docker history food11-api:latest` showed that the largest layer was the copied virtual environment:

`COPY /app/.venv /app/.venv`

This layer used approximately **1.5 GB** according to Docker history.

The multi-stage build prevents builder-only files and tools from being copied into the runtime stage. I did not record a separate final size for a naive single-stage image, so I do not report an unmeasured comparison value.

## Q6
The `.dockerignore` file excludes files and directories that do not need to be sent to the Docker build context, including:

- `.venv`
- `data`
- `mlruns`
- `mlflow.db`
- `.git`
- `__pycache__`
- `*.pyc`

This reduces the build context, avoids copying unnecessary large files, and helps make Docker builds faster and cleaner.

## Q7
Inside a Docker container, `localhost` refers to the container itself, not the Windows host machine.

Therefore the container uses:

`http://host.docker.internal:5000`

to communicate with the MLflow server running on the host machine.

The container was run with the environment variable:

`MLFLOW_TRACKING_URI=http://host.docker.internal:5000`

## Q8
I restarted the same Docker container and verified that it started successfully again.

After restart, the container logs showed:

`Application startup complete.`

and:

`Uvicorn running on http://0.0.0.0:8000`

The health endpoint again returned:

`{"status":"ok"}`

The model is loaded at application startup using:

`mlflow.pyfunc.load_model("models:/food11@champion")`

Therefore, when the container starts, it resolves the `champion` alias through MLflow and loads the registered model.

For the local MLflow artifact store used in this lab, the `mlruns` directory also had to be mounted into the container so that the container could access the model artifacts.

## Q9
The remaining step for a real deployment workflow would be to publish the Docker image to a remote container registry such as Docker Hub, GitHub Container Registry, or a cloud container registry.

The image should be tagged with meaningful versions, for example:

`food11-api:v1`

A registry allows the image to be pulled and deployed on another machine. Immutable image digests can also be used to identify the exact container image that was deployed.