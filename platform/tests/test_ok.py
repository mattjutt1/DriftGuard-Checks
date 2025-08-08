from fastapi.testclient import TestClient
from driftguard.main import app
c=TestClient(app)
def test_ok():
 r=c.get('/')
 assert r.status_code==200 and r.json()['ok'] is True
