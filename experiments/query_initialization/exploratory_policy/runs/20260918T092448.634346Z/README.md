# v001 接口兼容性诊断（不纳入提示词效果）

完整工具调用被服务端标记为 stop，v001只接受tool_calls，导致未执行检索。原始请求和响应完整保留。结束状态length仍属截断失败。修正仅涉及结束标记适配，另开v002全题重跑，原批不覆写。

{
  "status": "technical_diagnostic_excluded_from_prompt_comparison",
  "reason": "Endpoint returned stop for complete forced search calls; v001 required tool_calls. No retrieval executed. v002 accepts stop only with a complete unique schema-valid call; length remains rejected.",
  "sessions": 80,
  "api_requests": 80,
  "finish_reasons": {
    "stop": 73,
    "length": 7
  },
  "usage": {
    "prompt_tokens": 68196,
    "completion_tokens": 27294,
    "total_tokens": 95490
  },
  "search_calls": 0
}
