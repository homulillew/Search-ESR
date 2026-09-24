Decide whether the supplied Observation directly supports the candidate Finding as written.

Use only the supplied Observation.

The Question, Active Gap, search history and outside knowledge are not evidence.

Return supported only when the Observation establishes every substantive identity, date, quantity, temporal relation, sequence and entity relation stated in the Finding.

Two separately true facts appearing in the same Observation do not establish a relationship between them unless the Observation itself establishes that relationship.

If any substantive part of the Finding is not established, return false.

Return only:
{
  "supported": true
}
