FROM python:3.6.7

RUN mkdir /app
WORKDIR /app
ENV PYTHONPATH /app

# Install requirements
COPY ./requirements.txt requirements.txt
COPY ./dependencies dependencies
RUN pip install -r requirements.txt --upgrade
# RUN pip install -e ".[all]"

# Copy project files
COPY . /app

ENTRYPOINT ["python", "/app/pyxel/run.py"]