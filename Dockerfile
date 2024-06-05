FROM public.ecr.aws/lambda/python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    mv /root/.local/bin/poetry /usr/local/bin/

# Run Poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# Install PyTorch and torchvision separately using pip with extra index URL
RUN python3 -m pip install --no-cache-dir \
    torch==2.0.0+cpu torchvision==0.15.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

COPY ./app ./
COPY model /opt/ml/model

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["lambda_function.lambda_handler"]
