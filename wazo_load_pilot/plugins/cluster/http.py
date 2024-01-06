# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, HTTPException
from .services import registry_client

router = APIRouter()


@router.get('/cluster', status_code=200)
async def cluster():
    return {"message": "OK"}

@router.post('/cluster/registry/images/tags')
async def cluster(payload):
    try:
        tags = registry_client.list_image_tags(payload['image'])
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail={'status': 'internal_error', 'error': str(e)}
        )
    return tags

    
@router.post('/cluster/registry/manifest/id')
async def cluster(payload):
    try:
        manifest_id = registry_client.get_manifest_id(payload['image'], payload['tag'])
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail={'status': 'internal_error', 'error': str(e)}
        )
    return manifest_id