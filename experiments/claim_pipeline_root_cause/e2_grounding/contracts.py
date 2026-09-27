"""E2 scope wrapper; unchanged V2 evidence projection/schema and semantic prompts."""
from pathlib import Path
from ..contract_rerun.contracts import (ROOT, BASE, read, save, digest, file_hash,
    request, validate, project_payload, schema_for)
HERE=Path(__file__).resolve().parent
E2_ROLES={'g0_current_grounding','g1_evidence_inventory','g1_candidate_coverage'}
