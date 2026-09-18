#!/usr/bin/env python
"""OpenAI-compatible interactive chat. Run python chat.py --help."""
import argparse
import json
from pathlib import Path
import sys
from openai import APIConnectionError, APIStatusError, APITimeoutError
from llm_chat.client import ChatSession, Config, ROOT
from llm_chat.observed_agent import ObservedAgentSession


def error_message(exc):
    if isinstance(exc, APITimeoutError):
        return '请求超时，可检查网络或调大 OPENAI_TIMEOUT。'
    if isinstance(exc, APIConnectionError):
        return '无法连接 API，请检查 OPENAI_BASE_URL 和网络。'
    if isinstance(exc, APIStatusError):
        hints = {401: '请检查 API Key。', 403: '请检查账户和模型权限。',
                 404: '请检查 API 地址和模型名称。', 429: '请检查额度或稍后重试。',
                 400: '请检查模型是否支持 Chat Completions 和当前请求参数；也可尝试 --no-stream。'}
        return f'API 返回 HTTP {exc.status_code}。' + hints.get(exc.status_code, '请稍后重试或检查服务端。')
    return str(exc)


def main():
    parser = argparse.ArgumentParser(description='通过 OpenAI 兼容 API 进行多轮对话')
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env')
    parser.add_argument('--model')
    parser.add_argument('--base-url')
    parser.add_argument('--prompt', help='发送单条消息后退出')
    parser.add_argument('--plain', action='store_true', help='普通对话，不使用 BC+ 检索工具')
    parser.add_argument('--max-tool-rounds', type=int, default=64, help='每轮对话最多进行多少轮工具调用')
    parser.add_argument('--no-stream', action='store_true', help='关闭流式输出')
    parser.add_argument('--state-file', type=Path, help='Agent观察数据库；文件存在时恢复上次完成的对话')
    parser.add_argument('--window-variant', choices=['baseline', 'table_entry', 'table_entry_safe'], help='窗口版本；新会话默认baseline，恢复时沿用已保存版本')
    args = parser.parse_args()
    try:
        config = Config.load(args.env_file, model=args.model, base_url=args.base_url)
    except (ValueError, TypeError) as exc:
        print(error_message(exc), file=sys.stderr)
        return 2
    if args.max_tool_rounds < 1:
        parser.error('--max-tool-rounds 必须大于 0')
    if args.plain and (args.state_file or args.window_variant):
        parser.error('--state-file 和 --window-variant 仅适用于Agent模式')
    if args.plain:
        session = ChatSession(config)
    else:
        from datetime import datetime, timezone
        state_file = args.state_file or ROOT / 'chat_logs/observations' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ') + '.sqlite')
        try:
            session = ObservedAgentSession(
                config, state_path=state_file, variant=args.window_variant,
                max_rounds=args.max_tool_rounds,
                on_status=lambda message: print('\n[' + message + ']', file=sys.stderr, flush=True),
            )
        except ValueError as exc:
            print(error_message(exc), file=sys.stderr)
            return 2
        print(f'[观察状态：{state_file}]', file=sys.stderr)
    try:
        if args.prompt is not None:
            session.ask(args.prompt, stream=not args.no_stream, on_text=lambda s: print(s, end='', flush=True))
            print()
            return 0
        print(f'模式：{"普通对话" if args.plain else "BC+ 检索 Agent"}；模型：{config.model}\n输入 /clear 清空上下文，/save 保存记录，/exit 退出。')
        while True:
            try:
                text = input('\n你> ').strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not text:
                continue
            if text in {'/exit', '/quit'}:
                break
            if text == '/clear':
                session.reset()
                print('上下文已清空。')
                continue
            if text == '/save':
                from datetime import datetime
                dest = ROOT / 'chat_logs'
                dest.mkdir(exist_ok=True)
                path = dest / (datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.json')
                path.write_text(json.dumps({'model': config.model, 'messages': session.messages}, ensure_ascii=False, indent=2), encoding='utf-8')
                print(f'已保存：{path}')
                continue
            if text.startswith('/'):
                print('可用命令：/clear、/save、/exit')
                continue
            print('助手> ', end='', flush=True)
            try:
                session.ask(text, stream=not args.no_stream, on_text=lambda s: print(s, end='', flush=True))
                print()
            except KeyboardInterrupt:
                print('\n已中断，本轮未写入历史。')
            except (APIConnectionError, APIStatusError, ValueError) as exc:
                print('\n' + error_message(exc), file=sys.stderr)
        return 0
    except (APIConnectionError, APIStatusError, ValueError) as exc:
        print('\n' + error_message(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('\n已中断。', file=sys.stderr)
        return 130
    finally:
        session.close()

if __name__ == '__main__':
    raise SystemExit(main())
