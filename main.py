from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API is live!"}

@app.post("/run-script")
def run_script():
    # Call your Python logic here
    result = your_script_function()
    return {"result": result}

def your_script_function():
    # Your actual logic
    return "Script ran successfully!"