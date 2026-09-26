import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analysis'))
import mark_review as m
m.b=m.TOP/'admission_exploration';m.packets={r['review_id']:r for r in m.read(m.b/'OUTPUT_REVIEW_PACKETS.json')};m.reviews=m.read(m.b/'REVIEWS.json')
m.mark('4cbc772fa6806913',['SRN','SRN'],[1,2,3],hyp='correct_set')
m.mark('c9a1c8be038e28eb',['SRN','SRN'],[1])
m.mark('4f5122004614086e',['SRN'],[1,2])
m.mark('d319fc897c14d307',['SRN'],[1],hyp='correct_clear')
m.mark('f3b378b47f1d5e63',['SRN'],[1],hyp='correct_clear')
m.save()
