# Tool behavior

{
  "search_calls": {
    "total": 1203,
    "mean": 24.06,
    "median": 15.0,
    "p25": 7.0,
    "p75": 28.0,
    "p90": 45.100000000000016,
    "p95": 82.64999999999993,
    "max": 117
  },
  "get_document_calls": {
    "total": 151,
    "mean": 3.02,
    "median": 3.0,
    "p25": 2.0,
    "p75": 4.0,
    "p90": 5.100000000000001,
    "p95": 7.0,
    "max": 9
  },
  "total_tool_calls": {
    "total": 1354,
    "mean": 27.08,
    "median": 19.0,
    "p25": 9.5,
    "p75": 31.75,
    "p90": 47.800000000000026,
    "p95": 87.39999999999992,
    "max": 118
  },
  "unique_docids": {
    "total": 4466,
    "mean": 89.32,
    "median": 66.5,
    "p25": 38.25,
    "p75": 97.5,
    "p90": 167.90000000000003,
    "p95": 299.34999999999997,
    "max": 372
  },
  "unique_search_queries": {
    "total": 1202,
    "mean": 24.04,
    "median": 15.0,
    "p25": 7.0,
    "p75": 28.0,
    "p90": 45.100000000000016,
    "p95": 82.64999999999993,
    "max": 117
  },
  "exact_duplicate_queries": {
    "total": 1,
    "mean": 0.02,
    "median": 0.0,
    "p25": 0.0,
    "p75": 0.0,
    "p90": 0.0,
    "p95": 0.0,
    "max": 1
  },
  "repeated_document_reads": {
    "total": 3,
    "mean": 0.06,
    "median": 0.0,
    "p25": 0.0,
    "p75": 0.0,
    "p90": 0.0,
    "p95": 0.5499999999999972,
    "max": 1
  },
  "tool_round_count": {
    "total": 591,
    "mean": 11.82,
    "median": 7.5,
    "p25": 4.0,
    "p75": 14.0,
    "p90": 21.80000000000001,
    "p95": 36.949999999999974,
    "max": 56
  }
}

## 50-worker retrieval capacity observed

The formal batch reached 50 concurrent API requests while all retrieval calls shared one serialized GPU worker. It completed 1,203 Search calls and 151 GetDocument calls without a run failure. Search execution plus queue latency was 0.085 s median, 0.837 s p90, 2.760 s p95, and 11.376 s maximum (including the first model/index load). GetDocument's 148 successful calls had 0.00054 s median and 0.855 s p95. Three additional GetDocument calls had invalid arguments and returned tool errors to the agent.

GetDocument adoption was 50/50; Search-only answer rate was 0/50. One trajectory repeated an exact Search query. Sixteen trajectories exceeded the historical 12-round default; two exceeded 50 rounds; none reached the 200-round emergency cap. These results show the current backend handled this 50-worker batch, but Search remained serialized rather than 50-way parallel.
