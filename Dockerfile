FROM python:3.6.3

RUN mkdir /app
WORKDIR /app
ENV PYTHONPATH /app

# Install requirements
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt --upgrade

# Copy project files
COPY . /app

#ENTRYPOINT ["python", "/app/pyxel/web2/runweb.py"]
ENTRYPOINT ["python", "/app/pyxel/run.py"]