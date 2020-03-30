FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./app/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./config.ini /app/config.ini
COPY ./app /app
