FROM python:3.10-bullseye

RUN mkdir /tests
COPY etc/wazo-load-pilot/private.key /tests/private.key
COPY etc/wazo-load-pilot/certificate.pem /tests/certificate.pem
COPY etc/wazo-load-pilot/certificate.csr /tests/certificate.csr
COPY tests/simple_serve.py /simple_serve.py

CMD [ "python3", "/simple_serve.py" ]
