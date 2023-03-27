# Base image
FROM python:3.9-slim-buster

# Arguments
ARG AIRFLOW_VERSION=2.5.2
ARG AIRFLOW_USER_HOME=/usr/local/airflow
ARG AIRFLOW_DEPS="postgres"
ARG PYTHON_DEPS="psycopg2, requests, pandas"

# Environment variables
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}
ENV PYTHONPATH=${PYTHONPATH}:${AIRFLOW_HOME}
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Update and install dependencies
RUN apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        apt-utils \
        build-essential \
        locales \
        pytz \
        python-pip \
        curl \
        rsync \
        netcat \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Airflow with extras
RUN pip install --upgrade pip \
    && pip install apache-airflow[${AIRFLOW_DEPS}]==${AIRFLOW_VERSION} \
    && if [ -n "${PYTHON_DEPS}" ]; then pip install ${PYTHON_DEPS}; fi

# Initialize Airflow database
RUN airflow db init

# Create a new user and group to run Airflow
RUN groupadd -g 1000 airflow \
    && useradd -u 1000 -g airflow -ms /bin/bash -d ${AIRFLOW_USER_HOME} airflow \
    && chown -R airflow: ${AIRFLOW_USER_HOME}

# Copy project files into the container
WORKDIR ${AIRFLOW_USER_HOME}
COPY dags ${AIRFLOW_USER_HOME}/dags
COPY plugins ${AIRFLOW_USER_HOME}/plugins

# Expose Airflow port
EXPOSE 8080

# Start Airflow
USER airflow
CMD ["airflow", "webserver", "--port", "8080"]