# Post-retrieval sensitivity review of the five frozen-truth misses

The primary gate uses `PRIVATE_TRUTH.json` exactly as frozen before any query or Search. I inspected the full corpus text of all 25 top-five documents in the five cells whose frozen sufficient document was absent. This review is separate from the primary metric; it does not change the source bank or gate.

| Cell | Top-five finding | Review |
|---|---|---|
| A11, q186 | D 3079 lists Albino Frog as credited on Galacta; D 20115 explicitly says Albino Frog was its publisher, though it dates the game 1993; D 3133 has a 1992 table row naming Albino Frog as publisher. | Two new documents support the narrow publisher Gap. The previously observed D 39978 was still not rediscovered. Sensitivity for any sufficient document increases overall recall by one, but old-source rediscovery remains a miss. |
| C09, q186 | D 3079, D 3133 and D 22411 identify Galacta, Albino Frog and 1992 DOS context; D 20115 dates it 1993. | These are useful candidate documents, but none verifies the full November 1992 plus shareware condition of the frozen Gap. The canonical D 39978 was absent. |
| D01, q435 | The top five are obituary, biography, old retrospective, artist page and headlines; the old retrospective is rank 3. | None attributes the album count to the May 2017 Forbes Africa feature. The old related source consumed a top-five slot. |
| C01, q435 | The top five include an unrelated musician, the negative Miriam Makeba source, generic activists and an Oliver obituary saying 67 lifetime albums. | None supplies the count in the May 2017 Forbes Africa feature. This is a query/entity-disambiguation or ranking failure; this design cannot isolate which. |
| C12, q1094 | The top five are Ligue 1, French league history, Olympique Lyonnais, FC St. Pauli and defunct clubs. | None states that PSG was formed by a merger of Paris Football Club and Stade Saint-Germain. The frozen sufficient source D 24763 was absent. |

Thus the conservative frozen-truth overall document recall is 35/40. If A11's new publisher source is accepted for the narrow Gap, any-sufficient-document recall is 36/40. The preregistered old-source rate remains 19/20 and new-source rate remains 16/20, so the gate decision remains a stop. Other cells already contained a frozen sufficient document in top five; alternative sources in those cells were not exhaustively adjudicated because they cannot change binary recall or the gate.
