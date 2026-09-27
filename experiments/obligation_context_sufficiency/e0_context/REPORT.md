# Mechanical context reconstruction

{
  "has_previous_checkpoint": 17,
  "delta_eligible": 17,
  "path_eligible": 17,
  "observation_eligible": 15
}

All 27 exact historical states retained. Recent path includes every completed Writer update, even unchanged claims. A path containing only Writer updates has no eligible Search/Find/Open observation. Within a single tool batch, descending array index is a deterministic recency tie-break. No semantic relevance selection.

Exact bounded text comes from the historical tool return and actor_view buffer projection before writers, without reading a later Actor request. Intermediate Writer checkpoints have no contemporaneous Actor call; this limitation is disclosed, not represented as model-consumed text at each checkpoint.
