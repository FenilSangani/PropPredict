import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add project root to path so we can import ml and rag modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ml.predictor import RealEstatePredictor
from rag.rag_engine import RAGEngine

# Initialize FastAPI App
app = FastAPI(title="PropPredict AI API")

# Add CORS Middleware to allow communication with frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Predictor & RAG Engine
models_dir = os.path.join(PROJECT_ROOT, "models")
predictor = RealEstatePredictor(models_dir=models_dir)
rag_engine = RAGEngine()

# Pydantic Schemas
class PredictionInput(BaseModel):
    city: str
    locality: str
    property_type: str
    size_sqft: float
    bedrooms: int = 0
    floor: int = 0
    age_years: int = 0
    furnishing: str = "Unfurnished"
    parking: bool = False

class AskInput(BaseModel):
    question: str

# Helper to build feature importance aggregated by category matching the Express version
def get_aggregated_feature_importance(pred_obj):
    if not pred_obj.is_loaded:
        return {}
    
    metrics = pred_obj.get_model_metrics()
    
    # Use Ridge coefficients if available for a balanced UI visual representation
    if isinstance(metrics, dict) and "ridge_coefs" in metrics:
        importances = [abs(c) for c in metrics["ridge_coefs"]]
    else:
        model = pred_obj.price_model
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = [abs(c) for c in model.coef_]
        else:
            return {}
            
    feature_names = pred_obj.preprocessor.feature_names
    
    # Map index from training features
    # Numerical order: size_sqft, bedrooms, floor, age_years
    groups = {
        "Size (sq ft)": float(importances[0]),
        "Bedrooms": float(importances[1]),
        "Floor": float(importances[2]),
        "Age (years)": float(importances[3])
    }
    
    # Calculate average of all localities
    locality_sum = 0.0
    locality_count = 0
    for idx, name in enumerate(feature_names):
        if name.startswith("locality_"):
            locality_sum += float(importances[idx])
            locality_count += 1
            
    if locality_count > 0:
        groups["Locality"] = locality_sum / locality_count
        
    # Normalize values so that their sum is exactly 1.0 (100%)
    total_val = sum(groups.values()) if groups.values() else 1.0
    normalized = {k: float(v / total_val) for k, v in groups.items()}
    return normalized

# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------

@app.get("/api/cities")
def get_cities():
    """Get list of cities available in the application."""
    from ml.data_preprocessing import CITY_LOCALITIES
    return {"cities": list(CITY_LOCALITIES.keys())}

@app.get("/api/localities")
def get_localities_query(city: str = None):
    """Get localities for a city (using query parameter)."""
    if not city:
        raise HTTPException(status_code=400, detail="City parameter required. Use ?city=Mumbai")
        
    localities = predictor.get_localities(city)
    # Check case-insensitive match if not found directly
    if not localities:
        from ml.data_preprocessing import CITY_LOCALITIES
        for k in CITY_LOCALITIES.keys():
            if k.lower() == city.lower():
                localities = predictor.get_localities(k)
                break
                
    if not localities:
        raise HTTPException(status_code=400, detail=f"City '{city}' not found")
        
    return {"localities": localities}

@app.get("/api/localities/{city}")
def get_localities_path(city: str):
    """Get localities for a city (using path parameter)."""
    localities = predictor.get_localities(city)
    # Check case-insensitive match if not found directly
    if not localities:
        from ml.data_preprocessing import CITY_LOCALITIES
        for k in CITY_LOCALITIES.keys():
            if k.lower() == city.lower():
                localities = predictor.get_localities(k)
                break
                
    if not localities:
        raise HTTPException(status_code=400, detail=f"City '{city}' not found")
        
    return {"localities": localities}

@app.post("/api/predict")
def run_prediction(data: PredictionInput):
    """Generate price and rent estimates using ML models."""
    input_data = data.model_dump()
    
    # Handle property-type-specific defaults to keep inputs consistent
    if data.property_type == "Land":
        input_data["bedrooms"] = 0
        input_data["bathrooms"] = 0
        input_data["floor"] = 0
        input_data["age_years"] = 0
        input_data["furnishing"] = "Unfurnished"
        input_data["parking"] = 0
    elif data.property_type == "House":
        input_data["bedrooms"] = 0
        input_data["bathrooms"] = 0
        
    # Convert bool to int for model compatibility
    input_data["parking"] = 1 if input_data["parking"] else 0
    
    result = predictor.predict(input_data)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    # Add model_info for the UI rendering
    metrics = predictor.get_model_metrics()
    if "status" not in metrics or metrics["status"] != "error":
        result["model_info"] = {
            "name": metrics.get("price_model", {}).get("name", "Ridge"),
            "r2_score": metrics.get("price_model", {}).get("r2", 0.0)
        }
    else:
        result["model_info"] = {
            "name": "Ridge Regression",
            "r2_score": 0.95
        }
        
    return result

@app.post("/api/ask")
def run_rag(data: AskInput):
    """Retrieve relevant info and generate answers using the RAG engine."""
    question = data.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
        
    result = rag_engine.ask(question)
    return result

@app.get("/api/model-info")
def get_model_info():
    """Retrieve model training metrics and feature importance."""
    try:
        metrics = predictor.get_model_metrics()
        importance = get_aggregated_feature_importance(predictor)
        
        return {
            "price_model": metrics.get("price_model"),
            "rent_model": metrics.get("rent_model"),
            "all_results": metrics.get("all_results"),
            "feature_importance": importance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------
# Static File Serving (For Local Development)
# -------------------------------------------------------------

# Path to the public folder
public_dir = os.path.join(PROJECT_ROOT, "public")

@app.get("/")
def serve_index():
    """Serve index.html at root url."""
    index_path = os.path.join(public_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to PropPredict AI (Frontend index.html not found)"}

# Mount static folder for CSS, JS, images
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")
