import os
import logging
import pathlib
import json
import sqlite3
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...)):
    logger.info(f"Receive item: {name}")
    # Connect the database mercari.sqlite3
    conn = sqlite3.connect('../db/mercari.sqlite3')

    # Make a cursor
    c = conn.cursor()

    # Add a new item
    c.execute("INSERT INTO items (name, category) VALUES (?,?)", (name, category))

    # Commit our command
    conn.commit()

    # Close our connection
    conn.close()

    return {"message": f"item received: {name}"}

@app.get("/items")
def get_item():

    # Connect the database mercari.sqlite3
    conn = sqlite3.connect('../db/mercari.sqlite3')

    # Make a cursor
    c = conn.cursor()

    # select all the data in "items" table
    c.execute('''SELECT * FROM items''')
    stored_items = c.fetchall()

    # make a list of all the data taken from "items" table
    data = {"items": [{"id": id, "name": name, "category": category} for (id, name, category) in stored_items] }

    # Commit our command
    conn.commit()

    # Close our connection
    conn.close()

    return data

@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
