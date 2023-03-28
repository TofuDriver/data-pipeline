# Base image
FROM python:3.9-slim-buster

# Arguments
ARG AIRFLOW_VERSION=2.5.2
ARG AIRFLOW_USER_HOME=/usr/local/airflow
ARG AIRFLOW_DEPS="postgres"
ARG PYTHON_DEPS="psycopg2 requests pandas pytz"

# Environment variables
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}
ENV PYTHONPATH=${PYTHONPATH}:${AIRFLOW_HOME}
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux
ENV AIRFLOW__WEBSERVER__AUTHENTICATE=True
ENV AIRFLOW__WEBSERVER__AUTH_BACKEND=airflow.contrib.auth.backends.password_auth
ENV AIRFLOW__WEBSERVER__USERNAME=airflow
ENV AIRFLOW__WEBSERVER__PASSWORD=airflow

# Update and install dependencies
RUN set -ex \
    && buildDeps=' \
        freetds-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        git \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        apt-utils \
        build-essential \
        libpq-dev \
        python-pip \
        curl \
        rsync \
        netcat \
        locales \
    && touch /etc/locale.gen \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && useradd -ms /bin/bash -d ${AIRFLOW_USER_HOME} airflow
        
# Install Airflow with extras and clean temporary packages and files
RUN pip install --upgrade pip \
    && pip install apache-airflow[${AIRFLOW_DEPS}]==${AIRFLOW_VERSION} \
    && if [ -n "${PYTHON_DEPS}" ]; then pip install ${PYTHON_DEPS}; fi \
    && pip install -U pip setuptools wheel \
    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

# Initialize Airflow database
RUN airflow db init \
    && airflow users create \
        --username $AIRFLOW__WEBSERVER__USERNAME \
        --password $AIRFLOW__WEBSERVER__PASSWORD \
        --firstname Airflow \
        --lastname Admin \
        --role Admin \
        --email admin@example.com

RUN chown -R airflow: ${AIRFLOW_USER_HOME}

# Expose Airflow port
EXPOSE 8080

# Start Airflow
USER airflow
WORKDIR ${AIRFLOW_USER_HOME}
CMD ["airflow", "webserver"]