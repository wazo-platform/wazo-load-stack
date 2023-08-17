FROM python:3.10-bullseye

COPY etc /etc
COPY . /opt
COPY tests/start-wlpd.sh /start-wlpd.sh

WORKDIR /opt
RUN pip install --upgrade pip
RUN make install
WORKDIR /
CMD [ "sh", "/start-wlpd.sh" ]
