# Lab 5 - CI/CD with GitHub Actions

## Question 1
A unit test should not load the real model from MLflow because that makes the test depend on external infrastructure instead of only the code being tested.

The test could fail even when the code is correct if:
- the MLflow server is down or unreachable
- the network connection fails
- the registered model or alias is missing
- the model artifact cannot be downloaded
- loading the real model takes too long or requires unavailable resources

Using a fake model keeps the unit test fast and deterministic.

## Question 2
`test_predict_returns_valid_json` proves that the API can accept an uploaded image, decode and preprocess it, call a model object, choose a class, and return valid JSON containing a category and confidence.

It does not prove that the real ML model is accurate, that the real model can be loaded from MLflow, or that the real model predicts Bread correctly.

## Question 3
The duplicate-content hash check caught the copied image.

A train/test duplicate is dangerous because it creates data leakage. The model may see the same image during training and evaluation, which can make the reported test accuracy look better than the model's real generalization performance.

A corrupted image is easier to notice because it usually causes an explicit failure. A duplicate can silently produce misleading evaluation results.

## Question 4
The data validation should run in places where the DVC data is actually available.

Two useful places are:
1. locally before pushing or training, after the developer has pulled the DVC data
2. on a training or data-processing machine that has access to the DVC remote and runs validation after downloading the dataset

A cloud CI runner cannot validate data that it cannot access.

## Question 5
Because `smoke` has `needs: test`, the smoke job is skipped when the test job fails.

Without `needs: test`, both jobs could run independently, so Docker build and smoke testing could still run even when the unit tests already failed.

We observed this during the branch-protection test: the failing test caused the smoke job to be skipped.

## Question 6
The first successful CI run took about 1 minute 33 seconds.

The second run took about 1 minute 15 seconds.

The second run was around 18 seconds faster. The setup uses caching, so dependencies that were already cached did not need to be downloaded and prepared again.

## Question 7
Tagging the image with the commit SHA gives every image an immutable connection to an exact source-code version.

Using only `latest` can be ambiguous. For example, machine A may pull `latest` before a new image is pushed, while machine B pulls `latest` afterward. Both machines appear to run `latest`, but they are actually running different code.

With commit-SHA tags, the exact version is explicit and reproducible.

## Question 8
The push job explicitly requests only the permissions it needs:

- `contents: read`
- `packages: write`

This follows the principle of least privilege.

If a compromised workflow step had a token with broad write access, it could potentially modify repository contents, create or modify releases, change packages, or perform other unauthorized actions using the repository credentials.

## Question 9
The pull request showed that the required CI checks failed, and the merge was blocked by the branch ruleset.

After fixing the test and pushing again, the required `test` and `smoke` checks passed and the merge became available.

For a team, this means testing is enforced centrally by GitHub instead of depending on each developer remembering to run tests manually before pushing.

## Question 10
Two candidate model versions were evaluated by the promotion gate.

### Candidate version 2
- candidate accuracy: 0.0844
- champion accuracy: 0.7473
- test samples: 1054
- 2 * SE: 0.0268
- promotion threshold: 0.7740
- decision: keep the existing champion; version 2 became challenger

### Candidate version 3
- candidate accuracy: 0.7552
- champion accuracy: 0.7473
- test samples: 1054
- 2 * SE: 0.0268
- promotion threshold: 0.7740
- decision: keep the existing champion; version 3 became challenger

Although version 3 had a slightly higher raw accuracy than the champion, it did not exceed the required statistical threshold.

`2 * SE = 0.0268`, which represents approximately 2.68 accuracy percentage points.

## Question 11
Two ways to automate `promote.py` are:

1. use a self-hosted GitHub Actions runner on a machine or network that can reach the local MLflow server
2. use a hosted MLflow server such as the MLflow service provided by DagsHub, so a cloud runner can reach it

## Question 12

Pipeline:

```text
git push
   |
   v
GitHub Actions
   |
   +--> test job
   |      |
   |      +--> uv sync
   |      +--> ruff
   |      +--> pytest
   |
   v
smoke job
   |
   +--> build Docker image
   +--> start container with SKIP_MODEL=1
   +--> probe /health
   |
   v
push job (main only)
   |
   +--> login to GHCR
   +--> build/push image
   +--> tag image with git commit SHA
   |
   v
GHCR image
   |
   v
deployment / running container

Automatic steps:
- linting
- unit tests
- API tests
- Docker build
- smoke test
- GHCR image push on `main`

Human-controlled steps:
- opening and merging pull requests
- choosing or training candidate models
- running the promotion process while MLflow is local

Code version:
- decided by the Git commit SHA used as the container-image tag

Model version:
- decided independently in the MLflow Model Registry using the `champion` alias and the promotion quality gate
