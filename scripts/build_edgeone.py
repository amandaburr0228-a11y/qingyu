"""Stage shared Python modules into EdgeOne's cloud-functions bundle."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
for src,dst in [('engine.py','engine.py'),('app.py','_qingyu_app.py')]:
 shutil.copyfile(root/src,root/'cloud-functions'/dst)
print('EdgeOne Python modules staged; static output: web')
