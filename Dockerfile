FROM python:3.11.9

WORKDIR /reconciliation-backend/

COPY requirements.txt /reconciliation-backend/

RUN apt-get update \
    && apt-get -y install libpq-dev gcc 

RUN apt-get install -y postgresql postgresql-contrib

RUN pip install -r requirements.txt 

COPY . /reconciliation-backend/

ENV ENV=prod

RUN chmod +x /reconciliation-backend/gen_static_files.sh

RUN /reconciliation-backend/gen_static_files.sh

EXPOSE 8080

CMD ["gunicorn", "--bind", ":8080","reconciliation_backend.wsgi:application"]
