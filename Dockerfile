FROM python:3.11.9-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    mv /root/.local/bin/poetry /usr/local/bin/

# Run Poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Install PyTorch and torchvision separately using pip with extra index URL
RUN python3 -m pip install --no-cache-dir \
    torch==2.0.0+cpu torchvision==0.15.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

COPY ./app ./
COPY model /opt/ml/model

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
