from fastapi import FastAPI, File, UploadFile, Form, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from config.database_setup import get_db, Base, engine
from models.database_model import UploadedImage
import uuid
import os
from io import BytesIO
from PIL import Image
import pickle
import numpy as np
from fastapi import Request
from sqlalchemy import desc

# === Application Setup ===
app = FastAPI()

# Static file and template configurations
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")

# Ensure `images` folder exists
os.makedirs("images", exist_ok=True)

# Database initialization
Base.metadata.create_all(bind=engine)

# === Load Model ===
with open("my_model.pickle", "rb") as model_file:
    model = pickle.load(model_file)

# Load the model globally
# model = keras.load_model("my_model_smile_or_not.h5")


# === Utility Functions ===
def preprocess_image(image: Image.Image):
    """
    Preprocess the input image to prepare it for model prediction.
    """
    image = image.convert("RGB")  # Convert to RGB
    image = image.resize((64, 64))  # Resize image to 64x64
    image_array = np.array(image) / 255.0  # Normalize pixel values
    image_array = np.expand_dims(image_array, axis=0)  # Expand dims for batch size (1)
    return image_array

# === Routes ===
## Home Route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Render the home page.
    """
    return templates.TemplateResponse("home.html", {"request": request, "message": "Hello world!"})

## Classify Page
@app.get("/classify", response_class=HTMLResponse)
async def classify(request: Request):
    """
    Render the classify page.
    """
    return templates.TemplateResponse("classify.html", {"request": request})

## History Page
@app.get("/history", response_class=HTMLResponse)
async def history(request: Request, db: Session = Depends(get_db)):
    """
    Fetch and render classification history from the database.
    """
    # entries = db.query(UploadedImage).all()
    entries = db.query(UploadedImage).order_by(desc(UploadedImage.upload_date)).all()
    return templates.TemplateResponse("history.html", {"request": request, "entries": entries})

## Image Upload and Prediction")
@app.post("/upload")
async def upload_image(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Extract the file extension
    try:
        # Extract file extension and generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join("images", unique_filename)

        # Read and save the file
        file_content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        # Validate the image using PIL
        try:
            image = Image.open(BytesIO(file_content))
            image.verify()
        except Exception as e:
            return templates.TemplateResponse(
                "classify.html", 
                {"request": request, "error": f"Uploaded file is not a valid image: {e}"}
            )

        # Reload and preprocess the image
        image = Image.open(BytesIO(file_content))
        preprocessed_image = preprocess_image(image)

        # Predict using the model
        prediction = model.predict(preprocessed_image)
        smiling_probability = prediction[0][0]
        prediction_label = "Smiling" if smiling_probability > 0.5 else "Not Smiling"

        # Save to database
        db_image = UploadedImage(image_path=f"images/{unique_filename}", class_name=prediction_label)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        # Render the template with a success message
        return templates.TemplateResponse(
            "classify.html", 
            {"request": request, "success": "Image uploaded successfully!", "label": prediction_label}
        )

    except Exception as e:
        return templates.TemplateResponse(
            "classify.html", 
            {"request": request, "error": f"An error occurred: {e}"}
        )
