from pathlib import Path
import pytest
from experiments.recoverable_loop_clean.h_fix.replay_failures import RUN, replay_case


@pytest.mark.parametrize('trajectory', sorted(p.name for p in RUN.iterdir() if p.is_dir()))
def test_all_run001_invalid_outputs_exact_bytes_continue(trajectory, tmp_path):
    report = replay_case(trajectory, tmp_path/trajectory)
    assert report['next_scripted_actor_reached'] and report['paid_calls'] == 0


@pytest.mark.parametrize('trajectory', sorted(p.name for p in RUN.glob('R1_*')))
def test_run001_r1_production_skips_without_consuming_old_h_output(trajectory, tmp_path):
    report = replay_case(trajectory, tmp_path/trajectory, False)
    assert report['historical_steps'][-1]['hypothesis_outcome'] == 'skipped'
