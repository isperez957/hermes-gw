#!/usr/bin/env python3
"""Patch Hermes API server to emit reasoning_content in SSE stream."""
import re

path = '/usr/local/lib/hermes-agent/gateway/platforms/api_server.py'

with open(path) as f:
    content = f.read()

old = '''            else:
                finish_reason = "stop"

            # Finish chunk'''

new = '''            else:
                finish_reason = "stop"

            # Emit reasoning_content if the agent produced thinking text
            try:
                last_reasoning = result.get("last_reasoning") if result else None
            except Exception:
                last_reasoning = None
            if last_reasoning and isinstance(last_reasoning, str) and last_reasoning.strip():
                reasoning_chunk = {
                    "id": completion_id, "object": "chat.completion.chunk",
                    "created": created, "model": model,
                    "choices": [{"index": 0, "delta": {"reasoning_content": last_reasoning}, "finish_reason": None}],
                }
                await response.write(f"data: {json.dumps(reasoning_chunk)}\\n\\n".encode())

            # Finish chunk'''

if old in content:
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    print("PATCHED OK")
else:
    print("PATTERN NOT FOUND")
    for i, line in enumerate(content.split('\n'), 1):
        if 'finish_reason' in line and 'stop' in line:
            print(f"Line {i}: {line}")
