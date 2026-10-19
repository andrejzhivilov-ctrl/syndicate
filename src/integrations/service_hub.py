"""Per-agent optional integrations. No implicit grants or request-controlled endpoints."""
from __future__ import annotations

import asyncio
import json
import re
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

import httpx

from src.agent_platform.skill_library import SkillLibrary
from src.agents.director_base import DirectorStore
from src.data_paths import data_dir
from src.integrations.service_transport import JSONTransport, run_process
from src.pii import PIIRedactor

ROOT = Path(__file__).resolve().parents[2]


def bounded_text(value: object, limit: int = 20000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError('invalid_text')
    return value


class ServiceHub:
    """Host-selected agent identity and grants; payload cannot change either."""

    OPERATIONS = {
        'skills.list': '_skills', 'skills.read': '_skills',
        'hindsight.recall': '_hindsight', 'hindsight.retain': '_hindsight',
        'hindsight.reflect': '_hindsight', 'omniroute.chat': '_chat',
        'actual.snapshot': '_actual', 'hyperframes.render': '_render',
        'knowledge.search': '_knowledge', 'knowledge.read': '_knowledge',
        'mcp.pool.search': '_mcp_pool', 'mcp.pool.read': '_mcp_pool',
        'mcp.list': '_mcp', 'mcp.call': '_mcp',
    }

    def __init__(self, agent_id: str, config: dict, *, transport=None, process_runner=run_process):
        if not re.fullmatch(r'[a-z][a-z0-9_]{0,31}', agent_id):
            raise ValueError('invalid_agent')
        if not (ROOT / 'config/agents' / f'{agent_id}.profile.json').is_file():
            raise ValueError('unknown_agent')
        self.agent_id = agent_id
        self.config = config
        self.grants = frozenset(config.get('grants', []))
        if not self.grants <= self.OPERATIONS.keys():
            raise ValueError('unknown_integration_grant')
        self.transport = transport
        self.run_process = process_runner
        self.redactor = PIIRedactor()
        self.store = DirectorStore('integrations_' + agent_id)
        self._lock = asyncio.Lock()

    async def execute(self, operation: str, payload: dict) -> dict:
        if operation not in self.grants:
            return {'agent': self.agent_id, 'status': 'denied', 'reason': 'integration_not_granted'}
        if not isinstance(payload, dict):
            return {'agent': self.agent_id, 'status': 'error', 'error': 'payload_must_be_object'}
        # Write audit intent before any side effect; never log secrets or content.
        try:
            intent = self.store.add('integration_intent', {'operation': operation, 'agent': self.agent_id})
            async with self._lock:
                value = await getattr(self, self.OPERATIONS[operation])(operation, payload)
            result = {'status': 'ok', 'value': value, 'agent': self.agent_id}
            self.store.add('integration_result', {'intent': intent['id'], 'status': 'ok'})
            return result
        except (OSError, ValueError, KeyError, TypeError, IndexError, ImportError, httpx.HTTPError, TimeoutError, sqlite3.Error, ExceptionGroup):
            return {'agent': self.agent_id, 'status': 'unavailable', 'value': None, 'warning': 'integration_failed_or_not_configured'}

    def _client(self, service: str) -> JSONTransport:
        cfg = self.config[service]
        return JSONTransport(cfg['url'], cfg.get('api_key', ''), transport=self.transport)

    async def _skills(self, operation: str, payload: dict):
        library = SkillLibrary()
        if operation == 'skills.list':
            return library.for_agent(self.agent_id)
        return library.read(self.agent_id, payload['skill'], payload.get('resource', 'SKILL.md'))

    async def _knowledge(self, operation: str, payload: dict):
        from src.agent_platform.knowledge_pool import KnowledgePool

        access = self.config.get('knowledge_pool_access')
        if not isinstance(access, dict):
            access = {}
        pool = KnowledgePool(
            approval_key=self.config.get('knowledge_pool_approval_key'),
            review_agents=access.get('review_agents', []),
            shared_agents=access.get('shared_agents', []),
        )
        if operation == 'knowledge.search':
            query = bounded_text(payload.get('query'), 512)
            return pool.search(
                self.agent_id,
                query,
                limit=payload.get('limit', 3),
                kind=payload.get('kind'),
            )
        item_id = bounded_text(payload.get('item_id'), 64)
        return pool.read(self.agent_id, item_id)

    async def _hindsight(self, operation: str, payload: dict):
        mode = operation.split('.')[1]
        bank = 'syndicate-' + self.agent_id
        text = self.redactor.redact(bounded_text(payload['text']))[0]
        if mode == 'retain':
            body = {'items': [{'content': text, 'timestamp': datetime.now(timezone.utc).isoformat()}], 'async': False}
            path = f'/v1/default/banks/{bank}/memories'
        else:
            body = {'query': text, 'budget': 'low', 'max_tokens': 2048}
            suffix = 'memories/recall' if mode == 'recall' else 'reflect'
            path = f'/v1/default/banks/{bank}/{suffix}'
        return await self._client('hindsight').request(path, body)

    async def _chat(self, operation: str, payload: dict):
        cfg = self.config['omniroute']
        model = payload.get('model', cfg['model'])
        if model not in cfg.get('allowed_models', [cfg['model']]):
            raise ValueError('model_not_granted')
        content = self.redactor.redact(bounded_text(payload['text']))[0]
        response = await self._client('omniroute').request('/chat/completions', {
            'model': model, 'messages': [{'role': 'user', 'content': content}],
            'max_tokens': 2048, 'stream': False,
        })
        return {'text': bounded_text(response['choices'][0]['message']['content'], 100000),
                'usage': response.get('usage'), 'model': response.get('model', model)}

    async def _actual(self, operation: str, payload: dict):
        cfg = self.config['actual']
        start, end = date.fromisoformat(payload['start']), date.fromisoformat(payload['end'])
        if start > end or (end - start).days > 366:
            raise ValueError('invalid_date_range')
        account = bounded_text(payload['account'], 128)
        if account not in cfg['accounts']:
            raise ValueError('account_not_granted')
        folder = data_dir('actual', 'integrations/actual') / self.agent_id
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        raw = await self.run_process([
            cfg.get('node', 'node'), str(ROOT / 'deploy/integrations/actual_snapshot.mjs'),
        ], {**cfg, 'dataDir': str(folder), 'account': account,
            'start': start.isoformat(), 'end': end.isoformat()}, cwd=str(ROOT))
        response = json.loads(raw)
        if response.get('status') != 'ok' or not isinstance(response.get('transactions'), list):
            raise ValueError('invalid_actual_response')
        return response

    async def _render(self, operation: str, payload: dict):
        cfg = self.config['hyperframes']
        project = bounded_text(payload['project'], 64)
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', project):
            raise ValueError('invalid_project')
        root = (data_dir('render_projects', 'integrations/render_projects') / self.agent_id).resolve()
        folder = root / project
        if folder.is_symlink() or not folder.resolve().is_relative_to(root) or not folder.is_dir():
            raise ValueError('unknown_project')
        # Projects are operator-staged, trusted code; never accept HTML/JS in API input.
        output = folder / 'syndicate-render.mp4'
        if output.exists() or output.is_symlink():
            raise ValueError('output_already_exists')
        await self.run_process([cfg['binary'], 'render', '--output', str(output)], {},
                               cwd=str(folder), timeout=600)
        if output.is_symlink() or not output.is_file() or output.stat().st_size == 0:
            raise ValueError('missing_render_output')
        return {'artifact': str(output.relative_to(root)), 'bytes': output.stat().st_size,
                'published': False}

    async def _mcp_pool(self, operation: str, payload: dict):
        from src.agent_platform.mcp_server_pool import MCPServerPool

        access = self.config.get('mcp_pool_access')
        if not isinstance(access, dict):
            access = {}
        pool = MCPServerPool(reader_agents=access.get('reader_agents', []))
        if operation == 'mcp.pool.search':
            query = bounded_text(payload.get('query'), 512)
            category = payload.get('category')
            if category is not None:
                category = bounded_text(category, 128)
            return pool.search(
                self.agent_id,
                query,
                limit=payload.get('limit', 3),
                category=category,
            )
        item_id = bounded_text(payload.get('item_id'), 80)
        return pool.read(self.agent_id, item_id)

    async def _mcp(self, operation: str, payload: dict):
        from src.integrations.stdio_mcp import call_mcp
        server = self.config['mcp'][payload['server']]
        tool = bounded_text(payload['tool'], 128) if operation == 'mcp.call' else None
        if tool is not None and tool not in server.get('tools', []):
            raise ValueError('mcp_tool_not_granted')
        return await call_mcp(server, tool, self.redactor.redact_dict(payload.get('arguments', {})))
