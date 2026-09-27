"""Configurable Chat Completions client with transactional conversation history."""
from dataclasses import dataclass, field
from pathlib import Path
import os
from urllib.parse import urlsplit
from collections.abc import Callable
from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]

@dataclass
class Config:
    api_key: str = field(repr=False)
    base_url: str
    model: str
    system_prompt: str = '你是一个可靠的助手。请用清晰、准确的语言回答问题。'
    timeout: float = 120
    enable_thinking: bool | None = None

    @classmethod
    def load(cls, env_file=ROOT / '.env.deepseek', *, model='deepseek-flash', base_url='https://api.deepseek.com'):
        key = os.environ.get('DEEPSEEK_API_KEY') or dotenv_values(env_file).get('DEEPSEEK_API_KEY')
        if not key:
            raise ValueError('DEEPSEEK_API_KEY unavailable')
        if model != 'deepseek-flash' or base_url != 'https://api.deepseek.com':
            raise ValueError('Provider does not match model freeze')
        return cls(key, base_url, model, cls.system_prompt, 900, False)

    def request_options(self):
        # DeepSeek's OpenAI-compatible API uses `thinking`, not DashScope's
        # `enable_thinking`. This experiment freezes non-thinking mode.
        return {'temperature': 0, 'extra_body': {'thinking': {'type': 'disabled'}}}

class ChatSession:
    def __init__(self, config: Config, client=None):
        self.config = config
        self.client = client or OpenAI(api_key=config.api_key, base_url=config.base_url,
                                       timeout=config.timeout, max_retries=0)
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
