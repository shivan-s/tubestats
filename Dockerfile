FROM python:3.8-slim

ENV PYTHONDONTWEITEBYTECODE 1
ENV PYTHONNUNBUFFERED 1

WORKDIR /code

RUN pip install pipenv
COPY Pipfile Pipfile.lock /code/
RUN pipenv install

COPY . /code/

RUN chmod +x ./entrypoint.sh

ENTRYPOINT [ "sh", "-c", "./entrypoint.sh" ]
