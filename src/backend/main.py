from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import search_by_location as sl

app = FastAPI()

# This is the list of "origins" (websites) that are allowed to make requests.
# Even if you aren't using it yet, it's good practice to have.
origins = [
    "https://kellen-sullivan.github.io", # Your GitHub Pages URL
    "http://localhost:5173",         # Your local dev environment (Vite default)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/location-data/")
def location_root():
    response_json = {
        "response": [],
        "county": "",
        "error": False,
        "err_msg" : ""
    }
    
    sl.set_county(response_json, "44.56, -123.26")
    
    if response_json["error"]:
        return response_json
    
    sl.create_df(response_json)
    
    sl.summary_stats(response_json)
    
    return response_json