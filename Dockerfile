FROM public.ecr.aws/lambda/python:3.11

ENV PYTHONUNBUFFERED 1

# Create a non-root user and set permissions
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    mv /root/.local/bin/poetry /usr/local/bin/

# Config Poetry
COPY --chown=appuser:appuser pyproject.toml poetry.lock ./

# Run Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Install PyTorch and torchvision separately using pip with extra index URL
RUN python3 -m pip install --no-cache-dir \
    torch==2.0.0+cpu torchvision==0.15.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Copy the rest of app files
COPY --chown=appuser:appuser ./app ./
COPY --chown=appuser:appuser model /opt/ml/model

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["lambda_function.lambda_handler"]
