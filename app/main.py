from fastapi import FastAPI

app = FastAPI(title="Consensus Weighting API")

@app.get("/health")
def health_check():
    return {"status": "ok"}
