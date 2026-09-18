"""Configurable Chat Completions client with transactional conversation history."""
from dataclasses import dataclass, field
from pathlib import Path
import os
from urllib.parse import urlsplit
from collections.abc import Callable
from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]

@dataclass
class Config:
    api_key: str = field(repr=False)
    base_url: str
    model: str
    system_prompt: str = '你是一个可靠的助手。请用清晰、准确的语言回答问题。'
    timeout: float = 120
    enable_thinking: bool | None = None

    @classmethod
    def load(cls, env_file=ROOT / '.env', *, model=None, base_url=None):
        values = {**dotenv_values(env_file), **os.environ}
        key = next((str(v).strip() for v in (os.environ.get('OPENAI_API_KEY'), os.environ.get('DASHSCOPE_API_KEY'), values.get('OPENAI_API_KEY'), values.get('DASHSCOPE_API_KEY')) if v and str(v).strip()), '')
        model = model or values.get('OPENAI_MODEL', '').strip()
        url = (base_url or values.get('OPENAI_BASE_URL', '')).strip().rstrip('/')
        if not key or not model or not url:
            raise ValueError('请配置 OPENAI_API_KEY 或 DASHSCOPE_API_KEY，并填写 OPENAI_BASE_URL 和 OPENAI_MODEL。')
        parts = urlsplit(url)
        if parts.scheme not in {'http', 'https'} or not parts.netloc or parts.query or parts.fragment or parts.username:
            raise ValueError('OPENAI_BASE_URL 必须是有效的 HTTP(S) API 基础地址。')
        if parts.path.endswith('/chat/completions'):
            raise ValueError('OPENAI_BASE_URL 请填写 API 基础地址（通常以 /v1 结尾），不要包含 /chat/completions。')
        timeout = float(values.get('OPENAI_TIMEOUT') or 120)
        if timeout <= 0:
            raise ValueError('OPENAI_TIMEOUT 必须大于 0。')
        thinking = (values.get('DASHSCOPE_ENABLE_THINKING') or '').strip().lower()
        if thinking not in {'', 'true', 'false'}:
            raise ValueError('DASHSCOPE_ENABLE_THINKING 应为 true、false 或空。')
        return cls(key, url, model, values.get('CHAT_SYSTEM_PROMPT') or cls.system_prompt, timeout,
                   None if not thinking else thinking == 'true')

    def request_options(self):
        if self.enable_thinking is None:
            return {}
        return {'extra_body': {'enable_thinking': self.enable_thinking}}

class ChatSession:
    def __init__(self, config: Config, client=None):
        self.config = config
        self.client = client or OpenAI(api_key=config.api_key, base_url=config.base_url,
                                       timeout=config.timeout, max_retries=2)
        self.reset()

    def reset(self):
        self.messages = [{'role': 'system', 'content': self.config.system_prompt}]

    def ask(self, text: str, *, stream=True, on_text: Callable[[str], None] | None = None):
        if not text.strip():
            raise ValueError('消息不能为空。')
        pending = self.messages + [{'role': 'user', 'content': text}]
        response = self.client.chat.completions.create(model=self.config.model, messages=pending, stream=stream, **self.config.request_options())
        content = []
        finished = False
        if stream:
            try:
                for chunk in response:
                    if not chunk.choices:
                        continue
                    choice = chunk.choices[0]
                    part = choice.delta.content or getattr(choice.delta, 'refusal', None)
                    if part:
                        content.append(part)
                        if on_text:
                            on_text(part)
                    if choice.finish_reason is not None:
                        if choice.finish_reason != 'stop':
                            raise ValueError(f'回复未正常结束（{choice.finish_reason}），本轮未写入历史。')
                        finished = True
            finally:
                response.close()
        else:
            if not response.choices:
                raise ValueError('API 未返回 choices。')
            choice = response.choices[0]
            if choice.finish_reason != 'stop':
                raise ValueError(f'回复未正常结束（{choice.finish_reason}），本轮未写入历史。')
            part = choice.message.content or choice.message.refusal
            if part:
                content.append(part)
                if on_text:
                    on_text(part)
            finished = True
        if not finished or not content:
            raise ValueError('API 返回空回复或流提前结束，本轮未写入历史。')
        answer = ''.join(content)
        self.messages = pending + [{'role': 'assistant', 'content': answer}]
        return answer

    def close(self):
        self.client.close()
