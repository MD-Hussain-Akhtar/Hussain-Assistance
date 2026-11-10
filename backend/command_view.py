from fastapi import APIRouter, Request
import asyncio
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from command_router import get_command_router

router = APIRouter(prefix="/cmd", tags=["command_router"])


@router.post("/run")
async def run_command(request: Request):
    try:
        payload = await request.json()
        command = payload.get('command') if isinstance(payload, dict) else None
        if not command:
            return {'success': False, 'error': 'No command provided'}

        router_obj = get_command_router()
        # route is async and will internally run blocking work in threadpool
        return await router_obj.route(command)

    except Exception as e:
        return {'success': False, 'error': str(e)}
