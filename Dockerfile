FROM python:3

# Next two lines for faster development
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app
RUN pip install /app

WORKDIR /app
CMD pserve production.ini
