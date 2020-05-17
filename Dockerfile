FROM python:3.6

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN apt-get update -y && apt-get install gnuplot -y && pip install pipenv
RUN pipenv install --deploy --system
COPY . /app
RUN mkdir /app/data


RUN useradd appuser
RUN chmod -R 755 /app && chown -R appuser:appuser /app
USER appuser
WORKDIR /app
CMD /usr/local/bin/gunicorn main:app -b 0.0.0.0:8000 

