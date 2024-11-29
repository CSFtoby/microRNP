FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONMALLOC pymalloc_debug

RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    gettext \
    python3-lxml \
    python3-pil \
    libldap2-dev \
    python3-dev \
    nano \
    cron \
    wget \
    unzip \
    curl \
    libaio1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/2110000/instantclient-basiclite-linux.x64-21.10.0.0.0dbru.zip && \
    unzip instantclient-basiclite-linux.x64-21.10.0.0.0dbru.zip && \
    rm -f instantclient-basiclite-linux.x64-21.10.0.0.0dbru.zip && \
    cd instantclient* && \
    rm -f *jdbc* *occi* *mysql* *jar uidrvci genezi adrci && \
    mkdir -p /etc/ld.so.conf.d && \
    echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_10
ENV PATH=/opt/oracle/instantclient_21_10:$PATH
ENV ORACLE_HOME=/opt/oracle/instantclient_21_10
ENV TNS_ADMIN=/opt/oracle/instantclient_21_10/network/admin

WORKDIR /app

# Crear directorio de logs y establecer permisos
RUN mkdir /app/logs && chmod 777 /app/logs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]