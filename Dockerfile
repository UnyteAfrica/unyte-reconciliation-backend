FROM python:3.11.9

WORKDIR /reconciliation-backend/

COPY requirements.txt /reconciliation-backend/

RUN apt-get update \
    && apt-get -y install libpq-dev gcc 

RUN pip install -r requirements.txt 

COPY . /reconciliation-backend/

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8080", "reconciliation_backend.wsgi:application"]
