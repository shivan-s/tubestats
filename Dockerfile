FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONNUNBUFFERED 1
ENV PIPENV_VERBOSITY -1
ENV PIPENV_VENV_IN_PROJECT 1

WORKDIR /code

# hadolint ignore=DL3013
RUN pip install --no-cache-dir -U pipenv pip
COPY Pipfile Pipfile.lock /code/
RUN pipenv install --system --deploy --dev

COPY src /code/src/
COPY tests /code/tests/

CMD ["streamlit", "run", "main.py", "-p", "8000"]
