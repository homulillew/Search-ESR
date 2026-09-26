import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from runtime import *
base=TOP/'transport_correction';verify_freeze(base/'freeze.json')
batch(base,rd(base/'requests.json'),tag='corrected')
