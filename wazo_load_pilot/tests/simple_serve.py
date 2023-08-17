# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import http.server
import ssl


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        print("JSON reçu :")
        print(post_data)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'POST request received')


address = '0.0.0.0'
port = 443

certfile = 'tests/certificate.pem'
keyfile = 'tests/private.key'

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile, keyfile)

httpd = http.server.HTTPServer((address, port), CustomHandler)
httpd.socket = context.wrap_socket(httpd.socket)

print(f'HTTP server running {address}:{port}')

httpd.serve_forever()
