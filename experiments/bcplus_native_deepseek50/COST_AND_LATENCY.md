# Cost and latency

{
  "model_response_count": {
    "total": 641,
    "mean": 12.82,
    "median": 8.5,
    "p25": 5.0,
    "p75": 15.0,
    "p90": 22.80000000000001,
    "p95": 37.949999999999974,
    "max": 57
  },
  "api_requests": {
    "total": 641,
    "mean": 12.82,
    "median": 8.5,
    "p25": 5.0,
    "p75": 15.0,
    "p90": 22.80000000000001,
    "p95": 37.949999999999974,
    "max": 57
  },
  "prompt_tokens": {
    "total": 78191456,
    "mean": 1563829.12,
    "median": 384882.0,
    "p25": 95903.75,
    "p75": 1477885.75,
    "p90": 2824642.800000001,
    "p95": 8867261.449999979,
    "max": 14776375
  },
  "completion_tokens": {
    "total": 1180545,
    "mean": 23610.9,
    "median": 10078.0,
    "p25": 4238.5,
    "p75": 29995.0,
    "p90": 56829.40000000002,
    "p95": 79637.44999999998,
    "max": 151549
  },
  "total_tokens": {
    "total": 79372001,
    "mean": 1587440.02,
    "median": 416879.0,
    "p25": 99649.5,
    "p75": 1518743.5,
    "p90": 2907017.100000001,
    "p95": 8900247.99999998,
    "max": 14815077
  },
  "elapsed_seconds": {
    "total": 6317.627848185599,
    "mean": 126.35255696371198,
    "median": 73.17617100197822,
    "p25": 40.54792803898454,
    "p75": 161.78718567686155,
    "p90": 287.38767979089175,
    "p95": 426.6384112713854,
    "max": 603.9256082363427
  },
  "api_latency_seconds": {
    "total": 5599.642511855811,
    "mean": 8.735791750165072,
    "median": 4.154993271455169,
    "p25": 2.1770490035414696,
    "p75": 9.751256169751287,
    "p90": 18.8330856282264,
    "p95": 27.109006380662322,
    "max": 210.8547667618841
  }
}

Total wall-clock seconds: 604.457742
Estimated cost CNY: 11.65782032

Formal batch: 641 model requests, 78,191,456 prompt tokens, 1,180,545 completion tokens, 79,372,001 total tokens. Cache hit accounting was complete on all 641 responses: 72,710,016 / 78,191,456 prompt tokens (92.99%). Wall-clock time was 604.5 s; per-question latency median 73.2 s, p90 287.4 s, maximum 603.9 s. Peak simultaneous API requests was 50. The ¥11.6578 value uses frozen DeepSeek peak/off-peak prices and response usage; it is an estimate, not a billed amount.

The user-aborted six-worker attempt is excluded from all formal statistics above. It recorded 101 requests, 95 responses, 5,446,242 prompt tokens, 84,472 completion tokens, and an additional estimated ¥1.1932 on returned usage. Six requests were in flight without recorded responses when stopped; their actual charge, if any, cannot be derived from this archive. The known estimated usage across both attempts is therefore at least ¥12.8510, not a billed total.
