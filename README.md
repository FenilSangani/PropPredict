# PropPredict AI — Real Estate Price & Rent Predictor

AI-powered real estate price and rent predictions for **Mumbai**, **Delhi**, and **Bangalore** using Machine Learning + RAG (Retrieval Augmented Generation). Built natively on Python and FastAPI.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla, Modern dark theme) |
| **Backend** | Python, FastAPI, Uvicorn |
| **ML Engine** | Python, scikit-learn (Random Forest Regressor, R² = 0.95+) |
| **RAG Engine** | Python, TF-IDF + Cosine Similarity (Custom offline engine) |
| **Data** | 30,000 synthetic records with realistic distributions |

## Features

- **Price Prediction** — Predict property price in Lakhs using Random Forest (R² = 0.9538)
- **Rent Prediction** — Predict monthly rent using Random Forest (R² = 0.9333)
- **RAG Chat** — Ask questions about real estate and get data-backed answers with exact source matches
- **Model Insights** — View dynamic feature importance and model comparison metrics
- **3 Cities** — Mumbai, Delhi, Bangalore with 10 localities each

## ML Models Performance

| Model | Type | R² (Price) | R² (Rent) |
|-------|------|-----------|-----------|
| Linear Regression | Baseline | 0.8756 | 0.7489 |
| Ridge Regression | L2 Regularized | 0.8756 | 0.7489 |
| **Random Forest** | Ensemble (Best) | **0.9538** | **0.9333** |

## Project Structure

```
real-estate-ml-rag/
├── run.py                 ← Local server launcher script
├── train.py               ← One-click ML training script
├── requirements.txt       ← Python dependencies
├── vercel.json            ← Vercel serverless deployment config
├── api/
│   └── index.py           ← Main FastAPI application
├── public/
│   ├── index.html         ← Main UI
│   ├── style.css          ← Dark premium style
│   └── script.js          ← Frontend queries
├── ml/
│   ├── data_preprocessing.py  ← Feature scaling + One-Hot encoding
│   ├── model_training.py      ← Train baseline + ensemble models
│   ├── evaluate.py            ← R², MAE, RMSE metrics
│   └── predictor.py           ← Main ML loading and prediction interface
├── rag/
│   ├── knowledge_base/    ← City real estate documents (.txt files)
│   ├── chunker.py         ← Document chunking (overlapping)
│   ├── retriever.py       ← TF-IDF index + Cosine similarity search
│   ├── generator.py       ← Template-based generation with source attribution
│   └── rag_engine.py      ← Main RAG interface
├── data/
│   └── generate_data.py   ← Synthetic data generator
└── models/                ← Trained .pkl files (gitignored)
```

## Setup & Run

### Prerequisites
- **Python** (3.9+) with `pip`

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Train ML Models (first time only)

```bash
python train.py
```

This generates 30,000 records of synthetic real estate data and trains 3 models. Takes ~10 seconds.

### Step 3: Start the Server

```bash
python run.py
```

Open **http://127.0.0.1:5000** in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities` | List all cities |
| GET | `/api/localities/{city}` | Get localities for a city (path param) |
| GET | `/api/localities?city={city}` | Get localities for a city (query param) |
| POST | `/api/predict` | Predict price & rent using Random Forest |
| POST | `/api/ask` | Ask RAG a question |
| GET | `/api/model-info` | Get model metrics and feature importance |

## How It Works

### ML Pipeline
1. **Data Generation** — Synthetic data with realistic distributions for 3 cities.
2. **Preprocessing** — One-Hot Encoding (categorical) + Standard Scaling (numerical).
3. **Training** — Linear Regression, Ridge Regression, Random Forest.
4. **Evaluation** — R² Score, MAE, RMSE comparison.
5. **Selection** — Best model auto-selected (Random Forest wins and gets loaded for prediction).

### RAG Pipeline
1. **Knowledge Base** — Detailed text files about each city's real estate market.
2. **Chunking** — Split documents into 500-char overlapping chunks.
3. **Indexing** — TF-IDF vectorization with 5000 features.
4. **Retrieval** — Cosine similarity to find top 5 relevant chunks.
5. **Generation** — Template-based answer formatting with source attribution.
