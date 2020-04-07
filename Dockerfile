FROM python:3

COPY ./app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./

CMD [ "python", "./app/run.py" ]
