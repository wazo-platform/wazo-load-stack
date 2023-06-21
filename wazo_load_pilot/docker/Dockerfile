FROM python:3.10-bullseye

COPY etc /etc
COPY . /opt
WORKDIR /opt
RUN pip install --upgrade pip
RUN make install
WORKDIR /
CMD [ "wlpd", "--config-file", "/etc/wazo-load-pilot/config.yml" ]