FROM public.ecr.aws/lambda/python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./

RUN python3.11 -m pip install -r requirements.txt -t .

COPY ./app ./
COPY model /opt/ml/model

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["lambda_function.lambda_handler"]
