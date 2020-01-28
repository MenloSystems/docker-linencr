FROM menlosystems/python27


COPY . /app

WORKDIR /app

RUN pip install -e "."

CMD pserve development.ini 
#CMD pserve production.ini 

# oder:
# CMD bash
