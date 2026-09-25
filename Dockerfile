FROM python:3.10-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

ENV UV_HTTP_TIMEOUT=600
ENV UV_HTTP_RETRIES=10
ENV UV_CONCURRENT_DOWNLOADS=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY src/mlops_lab_1 ./src/mlops_lab_1
COPY wheels/ ./wheels/

RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-package torch

RUN uv pip install --python /app/.venv/bin/python --no-deps ./wheels/torch-2.14.0+cpu-cp310-cp310-manylinux_2_28_x86_64.whl


FROM python:3.10-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "src.food11.serve:app", "--host", "0.0.0.0", "--port", "8000"]
