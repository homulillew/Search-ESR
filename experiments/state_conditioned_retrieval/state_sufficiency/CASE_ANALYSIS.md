# S1 case analysis

Ranks are first frozen sufficient documents; `>50` is a miss. No truth was expanded after retrieval.

| Case | qid | Type | S0 | S1 | S2 | S3 | S3 vs S0 | Bridge S0→S3 |
|---|---:|---|---:|---:|---:|---:|---|---|
| U1_B01 | 517 | B | 1 | 1 | 1 | 1 | tie | >50→>50 |
| U1_B02 | 387 | B | 1 | 1 | 1 | 1 | tie | >50→>50 |
| U1_B03 | 435 | B | 1 | 1 | 1 | 1 | tie | >50→>50 |
| U1_B04 | 1094 | B | 4 | 4 | 4 | 4 | tie | >50→>50 |
| U1_B05 | 311 | B | 2 | 2 | 2 | 1 | improved | >50→>50 |
| U1_B06 | 186 | B | 13 | 1 | 1 | 1 | improved | >50→>50 |
| U1_B07 | 1034 | B | 1 | 1 | 1 | 1 | tie | >50→>50 |
| U1_B08 | 546 | B | 1 | 1 | 1 | 1 | tie | >50→>50 |
| U1_C01 | 435 | C | 9 | 4 | 4 | 4 | improved | 36→2 |
| U1_C02 | 435 | C | 1 | 1 | 1 | 1 | tie | 5→4 |
| U1_C03 | 435 | C | 1 | 1 | 1 | 1 | tie | 13→3 |
| U1_C05 | 177 | C | 1 | 1 | 1 | 1 | tie | 10→4 |
| U1_C06 | 580 | C | 1 | 1 | 1 | 1 | tie | 2→4 |
| U1_C07 | 580 | C | 1 | 1 | 1 | 1 | tie | 50→26 |
| U1_C11 | 546 | C | 3 | 1 | 1 | 1 | improved | 17→8 |
| U1_C12 | 1094 | C | >50 | >50 | >50 | >50 | tie | >50→>50 |
| U1_D01 | 435 | D | 2 | 1 | 4 | 2 | tie | 4→4 |
| U1_D02 | 435 | D | 1 | 1 | 1 | 1 | tie | 4→4 |
| U1_D03 | 177 | D | 2 | 1 | 1 | 1 | improved | 7→7 |
| U1_D04 | 177 | D | 2 | 2 | 2 | 2 | tie | 7→7 |
| U1_D05 | 177 | D | 1 | 1 | 1 | 1 | tie | 4→4 |
| U1_D06 | 580 | D | 1 | 1 | 1 | 1 | tie | 2→4 |
| U1_D07 | 580 | D | 1 | 1 | 1 | 1 | tie | 48→26 |
| U1_D08 | 546 | D | 1 | 1 | 1 | 1 | tie | 2→2 |

## Query examples

### U1_B06

- S0: `"Galacta" "second episode" planned name` (rank 13)
- S1: `"Galacta: The Battle for Saturn" "second episode" planned name` (rank 1)
- S2: `"Galacta: The Battle for Saturn" second episode planned name` (rank 1)
- S3: `"Galacta: The Battle for Saturn" second episode planned name` (rank 1)

### U1_C01

- S0: `Forbes Africa May 2017 musician albums human rights activist "Why do we sing, why is there art?"` (rank 9)
- S1: `Oliver Mtukudzi Forbes Africa May 2017 albums` (rank 4)
- S2: `Oliver Mtukudzi Forbes Africa May 2017 albums` (rank 4)
- S3: `Oliver Mtukudzi Forbes Africa May 2017 albums` (rank 4)

### U1_B04

- S0: `PSG Lille 4-3 second goal scorer match report` (rank 4)
- S1: `Paris Saint-Germain Lille 4-3 second goal scorer` (rank 4)
- S2: `Paris Saint-Germain Lille 4-3 second goal scorer` (rank 4)
- S3: `Paris Saint-Germain 4-3 Lille match report second PSG goal scorer 95th minute Messi free kick` (rank 4)

### U1_C05

- S0: `2016 Nigeria Professional Football League winner champions` (rank 1)
- S1: `2016 Nigeria Professional Football League winner champions Rangers` (rank 1)
- S2: `2016 Nigeria Professional Football League winner Rangers International Enugu` (rank 1)
- S3: `2016 Nigeria Professional Football League champions Rangers Enugu` (rank 1)

### U1_C06

- S0: `"Gretchen" "Jimmy" friends convince him to take her on a date season 1 episode` (rank 1)
- S1: `"You're the Worst" season 1 episode Gretchen friends convince Jimmy to take her on a date` (rank 1)
- S2: `"You're the Worst" season 1 Gretchen friends convince Jimmy take her on a date` (rank 1)
- S3: `You're the Worst season 1 Gretchen friends convince Jimmy to take her on a date episode` (rank 1)
