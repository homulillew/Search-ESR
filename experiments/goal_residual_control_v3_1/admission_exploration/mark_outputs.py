import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analysis'))
import mark_review as m
m.b=m.TOP/'admission_exploration'
m.packets={r['review_id']:r for r in m.read(m.b/'OUTPUT_REVIEW_PACKETS.json')}
m.reviews=m.read(m.b/'REVIEWS.json')
mark=m.mark
mark('e505b8224c4462aa',['SN'])
mark('0a886d6e439ca6ab',['SRN'],[1])
mark('8afe915e1300aec7',[])
mark('33ecd7ccba73aed6',['SRN','S'],[1],reason='Developer binding is new. Former Night Sky and Florida/October1993 formation already present; combining them does not add new decision information.')
mark('35e16d396eb7b5eb',['SRN','SRN'],[1,2])
mark('faed4a5afbe46c9a',['SRN','SRN'],[1,2,3],hyp='correct_set')
mark('d6e0874e36e2d806',['SRN','SRN'],[1],hyp='unsupported_temporal_binding',reason='Claim pair preserves secondary 2017 source context. Hypothesis separately asserts 65 by the May listing, stronger than the literal source date/count relation; provisional layer does not make that binding supported.')
mark('75f1288f01fe3f8f',[])
mark('d88ea2e3a8b0e83e',[])
mark('52a9dd575d11335d',['SN'],hyp='unsupported_upper_bound_inference',reason='Highest season mentioned in the current cast excerpt is five, but this provides no upper bound for total series seasons. Hypothesis promotes local coverage absence into apparent support for the requested less-than-ten condition.')
mark('5921d6243156d1f1',[])
m.save()
