FROM python:3.10.12-alpine3.18

ENV PYTHONUNBUFFERED 1
ENV PYTHONMALLOC pymalloc_debug

RUN apk add --update --no-cache\
    build-base jpeg-dev zlib-dev libjpeg\
    gettext\
    py3-lxml\
    py3-pillow\
    openldap-dev\
    python3-dev\
    gcompat\
    nano \
    dcron \
    && rm -rf /var/cache/apk/*

RUN apk add --no-cache libaio libnsl libc6-compat curl bash

WORKDIR /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/2110000/instantclient-basiclite-linux.x64-21.10.0.0.0dbru.zip && \
    unzip instantclient-basiclite-linux.x64-21.10.0.0.0dbru.zip && \
    rm -f instantclient-basiclite-linux.x64-21.10.0.0.0dbru.zip && \
    cd instantclient* && \
    rm -f *jdbc* *occi* *mysql* *jar uidrvci genezi adrci && \
    mkdir /etc/ld.so.conf.d && \
    echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf
RUN ldconfig /etc/ld.so.conf.d
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_10
ENV PATH=/opt/oracle/instantclient_21_10:$PATH
ENV ORACLE_HOME=/opt/oracle/instantclient_21_10
ENV TNS_ADMIN=/opt/oracle/instantclient_21_10/network/admin
RUN echo 'INPUT ( libldap.so )' > /usr/lib/libldap_r.so


WORKDIR /app

# Crear directorio de logs y establecer permisos
RUN mkdir /app/logs && chmod 777 /app/logs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]