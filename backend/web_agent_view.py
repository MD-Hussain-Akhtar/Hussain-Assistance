from fastapi import APIRouter, Request
import asyncio
import os
import sys

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_agent import WebAgent

router = APIRouter(prefix="/web", tags=["web_agent"])

# Singleton WebAgent instance
_agent = None


def get_agent():
    """Get or create WebAgent singleton"""
    global _agent
    if _agent is None:
        _agent = WebAgent()
    return _agent


@router.post("/agent/run")
async def run_web_agent(request: Request):
    """Execute a web agent command"""
    try:
        payload = await request.json()
        command = payload.get('command') if isinstance(payload, dict) else None
        
        if not command:
            return {'success': False, 'error': 'No command provided'}

        loop = asyncio.get_running_loop()
        agent = get_agent()

        # Run blocking agent.run() in threadpool to avoid blocking event loop
        result = await loop.run_in_executor(None, agent.run, command)
        
        if not isinstance(result, dict):
            return {'success': False, 'error': 'Invalid response from agent'}
        
        return result
        
    except Exception as e:
        return {'success': False, 'error': f'WebAgent Error: {str(e)}'}
