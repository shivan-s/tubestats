FROM python:3.8-slim

ARG YOUR_ENV
ENV YOUR_ENV=${YOUR_ENV} \
	PYTHONDONTWRITEBYTECODE=1\
	PYTHONUNBUFFERED=1 \
	PYTHONHASHSEED=random \
	PIP_NO_CACHE_DIR=off \
	PIP_DISABLE_PIP_VERSION_CHECK=on \
	PIP_DEFAULT_TIMEOUT=100 \
	STREAMLIT_SERVER_PORT=8999

COPY ./requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt

COPY ./.streamlit .

COPY . /usr/src/

WORKDIR /usr/src/

RUN chmod a+rx setup.sh

ENTRYPOINT [ "sh", "-c", "./setup.sh" ]

