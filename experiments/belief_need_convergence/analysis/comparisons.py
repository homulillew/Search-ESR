from aggregate import P,rd,wr
R=rd(P/'round_0/REVIEW.json');M={(r['case_id'],r['arm']):r for r in R};dev=rd(P/'bank/MEMBERSHIP.json')['development'];rows=[]
for a,b in [('P0','P1'),('P1','P2'),('P1','P3')]:
 both=[c for c in dev if M[c,a]['output'] and M[c,b]['output']];rows.append({'A':a,'B':b,'same_case_both_returned':len(both),'case_ids':both,'A_strict':sum(M[c,a]['STRICT_VALID'] for c in both),'B_strict':sum(M[c,b]['STRICT_VALID'] for c in both),'A_fail_B_pass':[c for c in both if not M[c,a]['STRICT_VALID'] and M[c,b]['STRICT_VALID']],'A_pass_B_fail':[c for c in both if M[c,a]['STRICT_VALID'] and not M[c,b]['STRICT_VALID']],'limitation':'Conditioning on completion creates selection bias; descriptive only, not an unbiased path-effect estimate.'})
wr(P/'analysis/PAIRED_COMPLETION_COMPARISON.json',rows)
print(rows)
