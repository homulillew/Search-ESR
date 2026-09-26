"""Separate frozen P3 technical correction, preserving every original rejection."""
import sys
from pathlib import Path
import runtime as rt
original=rt.make_request
def patched(case,stage,issue=None,prompt_override=None):
 if stage=='P3A':prompt_override=rt.P/'prompts/P3A_transport.txt'
 return original(case,stage,issue,prompt_override)
rt.make_request=patched
folder=rt.P/'round_0_p3_format_repair'
if sys.argv[1]=='freeze':
 rt.freeze(folder,[{'case_id':c['case_id'],'arm':'P3'} for c in rt.rd(rt.P/'bank/RUNTIME_INPUTS.json')],[Path(__file__).resolve(),rt.P/'P3_FORMAT_CORRECTION.md'])
else:rt.run(folder)
