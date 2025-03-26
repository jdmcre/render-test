from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is up and running!"}

@app.post("/run-script")
def run_script():
    return {"result": "Python script executed successfully!"}