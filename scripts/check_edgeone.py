"""Smoke test staged Flask routes before EdgeOne deployment."""
import importlib.util,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'cloud-functions'))
spec=importlib.util.spec_from_file_location('qingyu_edgeone',root/'cloud-functions/api/index.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
client=module.app.test_client()
for path in ['/health','/status','/knowledge']:
 response=client.get(path)
 assert response.status_code==200,(path,response.status_code)
response=client.post('/chat',json={'text':'考试没考好，我觉得自己很失败','intensity':5})
assert response.status_code==200,response.get_data(as_text=True)
assert response.json['knowledge'][0]['id']=='CBT-01'
print('EdgeOne Flask route smoke checks passed')
