import uvicorn

if __name__ == "__main__":
    print("Starting PropPredict AI Local Server on http://127.0.0.1:5000")
    uvicorn.run("api.index:app", host="127.0.0.1", port=5000, reload=True)
