"""Reproduce the authorized metadata-only repair; no retrieval/model calls."""
import ast,json,pathlib,sys
script=pathlib.Path(sys.argv[1]);metadata=pathlib.Path(sys.argv[2])
tree=ast.parse(script.read_text())
prefix=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and any(isinstance(t,ast.Name) and t.id=='PREFIX' for t in n.targets))
data=json.loads(metadata.read_text())
if 'query_prefix' in data and data['query_prefix']!=prefix:raise ValueError('Refuse to replace a different configured prefix')
data['query_prefix']=prefix
metadata.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
