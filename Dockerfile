FROM python:3.10

WORKDIR /

COPY pyproject.toml .

RUN python -m pip install poetry
# do not create a virtual environment
RUN python -m poetry config virtualenvs.create false
RUN python -m poetry install

# copy necessary files
COPY spotify_stats/ ./spotify_stats
COPY static/ ./static
COPY templates/ ./templates
COPY config.py .
COPY streaming_history.csv .
COPY app.py .

# command to run on container start
CMD [ "python", "app.py" ]
