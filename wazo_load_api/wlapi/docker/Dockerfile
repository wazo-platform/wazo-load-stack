FROM python:3.10-bullseye AS builder

RUN python3.10 -m venv /opt/venv
# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"
#
RUN mkdir -p /usr/src/wlapi/wlapi

WORKDIR /usr/src/wlapi

COPY wlapi/etc /etc
COPY wlapi/tests/start-wlapi.sh /usr/local/bin/start-wlapi
COPY . wlapi/
RUN apt update && apt -y upgrade && apt-get install -y vim

RUN pip install --upgrade pip
WORKDIR /usr/src/wlapi/wlapi
RUN make install


FROM wda-load-testing:0.0.23

RUN apt update && apt -y upgrade && \
    apt -y install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev python3-pip && \
    wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz && \
    tar -xf Python-3.10.*.tgz && cd Python-3.10.*/ && \
    ./configure --prefix=/usr/local --enable-optimizations --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib" && \
    make -j $(nproc) && make altinstall

ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/local/bin/start-wlapi /usr/local/bin/start-wlapi
COPY --from=builder /usr/src/wlapi /usr/src/wlapi
COPY --from=builder /etc /etc

WORKDIR /usr/src/app
CMD [ "sh", "/usr/local/bin/start-wlapi" ]
