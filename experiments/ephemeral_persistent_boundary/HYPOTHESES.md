# Frozen hypotheses

- H1: An unsupported exact term in a one-time query can improve, harm, or leave
  unchanged retrieval utility; query text alone is not an outcome.
- H2: Showing query history to a Binder may increase copied or unsupported
  proposals even when the prompt says query text is not evidence.
- H3: Removing action arguments from persistence input reduces this path of
  contamination, but does not guarantee semantically correct binding.
- H4: Literal extraction blocks absent values; a query-blind semantic verifier
  remains necessary because incidental mentions can satisfy literal matching.
- H5: After NoGain, old guesses can persist through recent action context
  despite a clean persistent TestCard; an explicit expiry label or context
  projection may change the next query.
