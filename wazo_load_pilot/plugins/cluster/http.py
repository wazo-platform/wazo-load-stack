# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import Any, Optional

from fastapi import APIRouter, HTTPException

from .services import registry_client

router = APIRouter()


@router.post('/cluster/registry/images/tags')
async def image_tags(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        if registry_client is None:
            raise HTTPException(
                status_code=500,
                detail={'status': 'internal_error', 'error': 'registry_client is None'},
            )
        tags = registry_client.list_image_tags(payload['image'])
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail={'status': 'internal_error', 'error': str(e)}
        )
    return tags


@router.post('/cluster/registry/manifest/id')
async def manifest_id(payload: dict[str, Any]) -> Optional[str]:
    try:
        if registry_client is None:
            raise HTTPException(
                status_code=500,
                detail={'status': 'internal_error', 'error': 'registry_client is None'},
            )
        manifest_id = registry_client.get_manifest_id(payload['image'], payload['tag'])
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail={'status': 'internal_error', 'error': str(e)}
        )
    return manifest_id


@router.post('/cluster/registry/manifest')
async def manifest(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        if registry_client is None:
            raise HTTPException(
                status_code=500,
                detail={'status': 'internal_error', 'error': 'registry_client is None'},
            )
        manifest = registry_client.get_manifest_id(payload['image'], payload['tag'])
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail={'status': 'internal_error', 'error': str(e)}
        )
    return {"manifest": manifest}


@router.post('/cluster/registry/image/labels')
async def image_label(payload: dict[str, Any]) -> dict[str, Any]:
    """
    This operation can be expensive if the image is not present on the system.
    By default we don't download it.
    """
    try:
        if registry_client is None:
            raise HTTPException(
                status_code=500,
                detail={'status': 'internal_error', 'error': 'registry_client is None'},
            )
        labels = registry_client.get_image_labels(payload['image'], payload['tag'])
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail={'status': 'internal_error', 'error': str(e)}
        )
    if not labels:
        return {
            "error": "the image is not present on system. You can use the --force flag."
        }
    return labels


@router.post('/cluster/registry/image/labels/force')
async def force_image_labels(payload: dict[str, Any]) -> Optional[dict[Any, Any]]:
    """
    This operation can be expensive if the image is not present on the system.
    """
    try:
        if registry_client is None:
            raise HTTPException(
                status_code=500,
                detail={'status': 'internal_error', 'error': 'registry_client is None'},
            )
        labels = registry_client.get_image_labels(
            payload['image'], payload['tag'], force=True
        )
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail={'status': 'internal_error', 'error': str(e)}
        )
    return labels
