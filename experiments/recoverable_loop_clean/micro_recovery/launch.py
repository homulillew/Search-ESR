"""Preflight v2: distinguish tracked implementation from pinned local BC+ dependency."""
from .common import *
from . import run as experiment


def check_v2():
    f=read(BASE/'FREEZE_v2.json')
    assert subprocess.check_output(['git','show','HEAD:'+str((BASE/'FREEZE_v2.json').relative_to(ROOT))],cwd=ROOT)==(BASE/'FREEZE_v2.json').read_bytes()
    for name,h in f['files'].items():
        assert sha(ROOT/name)==h,('changed frozen bytes',name)
        assert subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)==(ROOT/name).read_bytes()
    for name,info in f['external_source_files'].items():
        assert sha(ROOT/name)==info['sha256']
        assert (ROOT/name).read_bytes()==(ROOT/info['committed_snapshot']).read_bytes()
    for name,meta in f['binary_files'].items():
        st=Path(name).stat();assert {'size':st.st_size,'mtime_ns':st.st_mtime_ns}==meta,name
    return f


if __name__=='__main__':
    experiment.check_freeze=check_v2
    experiment.run()
