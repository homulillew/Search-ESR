# Q1 complementary query test

K0 Single Query@10 failed its frozen gate (36/40). Generate exactly one complementary Query2 with DeepSeek `deepseek-flash` for each of all 40 cases, without exposing truth or Query1 success to the writer. Persist each raw request/response/error. Commit all outputs before embedding Query2. Compare Single Query top10 with deduplicated Query1 top5 + Query2 top5 under the same ten-document candidate budget. RRF uses constant 60 and only each top5 rank. Invalid responses remain failures; no retry or repair.
