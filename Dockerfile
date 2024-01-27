FROM python:3.10-slim-bullseye
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install virtualenv &&\
    python -m virtualenv --python=/usr/local/bin/python $VIRTUAL_ENV
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt &&\
    find $VIRTUAL_ENV | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
FROM python:3.10-slim-bullseye
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --from=0 $VIRTUAL_ENV $VIRTUAL_ENV
WORKDIR /app
RUN apt update && apt install -y libpq-dev \
    -o APT::Install-Recommends=false -o APT::Install-Suggests=false && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    useradd -ms /bin/bash app &&\
    chown app:app /app
USER app
COPY --chown=app . /app
CMD gunicorn -c settings/gunicorn_config.py settings.wsgi
