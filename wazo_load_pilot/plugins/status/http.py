# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter

router = APIRouter()

@router.get('/status', status_code=200)
async def get_status():
    return {"message": "OK"}
