"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    path = agent.root / 'state/session.json'
    if data['action'] == 'save':
        answer = await agent.ask('remember', 'Remember this fact in this conversation.', data['fact'], 'I will remember Python.')
        record = {'session_id': agent.session_id or 'offline-fixture', 'live': agent.live, 'cwd': str(agent.root)}
        atomic_json(path, record)
    elif data['action'] == 'resume':
        record = json.loads(path.read_text(encoding='utf8'))
        if record['live'] != agent.live or record['cwd'] != str(agent.root):
            raise ValueError('Saved session belongs to a different mode or workspace')
        answer = await agent.ask('recall', 'What is my favorite programming language?', {}, 'Python',
                                 sdk={'resume': record['session_id']} if agent.live else None)
    else:
        raise ValueError('action must be save or resume')
    return {'action': data['action'], 'answer': answer, 'state_file': str(path), 'history_note': 'The identifier is not the SDK transcript.'}
