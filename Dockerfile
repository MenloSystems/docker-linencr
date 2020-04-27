#FROM menlosystems/python27
FROM python:3.7

COPY . /app

WORKDIR /app

RUN pip install -e "."

CMD pserve development.ini
#CMD pserve production.ini

# oder:
# CMD bash
