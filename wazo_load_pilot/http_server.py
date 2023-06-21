# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import FastAPI
from gunicorn.app.base import BaseApplication
from typing import Dict



api = FastAPI(title='wazo-load-pilot', openapi_url='/api/api.yml')

class SysconfdApplication(BaseApplication):
    def __init__(self, *args, config: Dict = {}, **kwargs):
        self.config = config or {}
        self.options = {
            'ssl_certfile': config['certs']['cert'],
            'ssl_keyfile': config['certs']['key'],
        }
        super().__init__(*args, **kwargs)

    def load_config(self):
        print(f"config: {self.config}")
        host = self.config['rest_api']['listen']
        port = self.config['rest_api']['port']
        self.cfg.set('bind', [f'{host}:{port}'])
        self.cfg.set('default_proc_name', 'sysconfd-api')
        self.cfg.set('loglevel', self.config['log_level'])
        self.cfg.set('accesslog', '-')
        self.cfg.set('errorlog', '-')
        # NOTE: We must set this to one worker, since each worker is its own process,
        # and if we have more than one
        # they will each get their own queue and then not respect the execution order
        # which creates concurrency issues.
        self.cfg.set('workers', 1)
        # NOTE(afournier): that's the magic class that makes gunicorn ASGI
        self.cfg.set('worker_class', 'uvicorn.workers.UvicornWorker')

    def load(self):
        return api
