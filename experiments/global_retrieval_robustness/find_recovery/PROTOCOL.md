# F1 and F2 Find diagnostic

F1: each of 40 canonical sufficient documents is verified in the frozen corpus by SHA-256 and exact evidence anchor before Find. Register only that D and call the existing `SearchFindTools.find` once with the frozen U1 find query. Review returned W for useful, fully sufficient, partial, no gain, and exact anchor hit. No retry or rewritten query.

F2: after F1 and ranking selection, compare Top1 Find with the same query on Top1 and Top2 in one predetermined parallel batch. Maximum two independent Find calls. The Top2 batch does not adapt to the Top1 result. Review every window separately; diagnostic U1 top5 may be used if no ranking policy passes, without deployment claims.
