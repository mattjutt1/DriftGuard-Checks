from fastapi import FastAPI
app=FastAPI(title='DriftGuard API',version='0.1.0')
@app.get('/')
def ok(): return {'ok':True}
