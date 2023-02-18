FROM python:3.10-slim-buster

# Inside container
# make a new folder inside container
WORKDIR /backend-flask

# Outside Container -> Inside Container
# this contains the libraries want to install to run the app
COPY requirements.txt requirements.txt

# inside Container
# Install the python libraries used for the app
RUN pip3 install -r requirements.txt

# . means everything in the current directory
# first period /backend-flask (outside container)
# second period /backend-flask (inside container)
COPY . .

# Environment variables (Env vars)
ENV FLASK_ENV=development

EXPOSE ${PORT}

# python3 -m flask run --host=0.0.0.0 --port=4567
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
