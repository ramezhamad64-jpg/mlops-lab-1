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