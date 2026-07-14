"""
=============================================================
train.py — One-Click Training Script
=============================================================
Run this to generate data and train all ML models.

Usage:
    python train.py

Steps:
    1. Generate synthetic real estate data (30,000 records)
    2. Preprocess data (encoding + scaling)
    3. Train 3 models for Price prediction
    4. Train 3 models for Rent prediction
    5. Save best models AND Ridge models (for JS export)
    6. Export model params to JSON (for Node.js/Vercel)
    7. Display evaluation metrics
=============================================================
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def main():
    """Main training pipeline."""
    
    print("\n" + "=" * 60)
    print("  Real Estate ML — Training Pipeline")
    print("=" * 60)
    
    # ----------------------------------------------------------
    # Step 1: Generate Synthetic Data
    # ----------------------------------------------------------
    print("\nSTEP 1: Generating synthetic data...")
    print("-" * 60)
    
    from data.generate_data import main as generate_data
    generate_data()
    
    # ----------------------------------------------------------
    # Step 2: Load the Combined Dataset
    # ----------------------------------------------------------
    print("\nSTEP 2: Loading combined dataset...")
    print("-" * 60)
    
    data_path = os.path.join(PROJECT_ROOT, 'data', 'combined_data.csv')
    df = pd.read_csv(data_path)
    
    print(f"  Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"  Cities: {df['city'].unique().tolist()}")
    print(f"  Price range: {df['price_lakhs'].min():.1f}L - {df['price_lakhs'].max():.1f}L")
    print(f"  Rent range: {df['rent_monthly'].min():.0f} - {df['rent_monthly'].max():.0f}")
    
    # ----------------------------------------------------------
    # Step 3: Preprocess Data
    # ----------------------------------------------------------
    print("\nSTEP 3: Preprocessing data...")
    print("-" * 60)
    
    from ml.data_preprocessing import DataPreprocessor
    
    preprocessor = DataPreprocessor()
    X, y_price, _, y_rent = preprocessor.fit_transform(df)
    
    # ----------------------------------------------------------
    # Step 4: Train/Test Split (80/20)
    # ----------------------------------------------------------
    print("\nSTEP 4: Splitting data (80% train, 20% test)...")
    print("-" * 60)
    
    X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(
        X, y_price, test_size=0.2, random_state=42
    )
    
    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
        X, y_rent, test_size=0.2, random_state=42
    )
    
    print(f"  Training set: {X_train_p.shape[0]} samples")
    print(f"  Test set: {X_test_p.shape[0]} samples")
    
    # ----------------------------------------------------------
    # Step 5: Train Models
    # ----------------------------------------------------------
    print("\nSTEP 5: Training models...")
    print("-" * 60)
    
    from ml.model_training import ModelTrainer
    
    trainer = ModelTrainer()
    
    # Train for Price prediction
    print("\n  --- PRICE PREDICTION ---")
    price_results = trainer.train_all_models(
        X_train_p, y_train_p, X_test_p, y_test_p, target_name="Price (Lakhs)"
    )
    
    # Train for Rent prediction
    print("\n  --- RENT PREDICTION ---")
    rent_results = trainer.train_all_models(
        X_train_r, y_train_r, X_test_r, y_test_r, target_name="Rent (Monthly)"
    )
    
    # ----------------------------------------------------------
    # Step 6: Select Best Models
    # ----------------------------------------------------------
    print("\nSTEP 6: Selecting best models...")
    print("-" * 60)
    
    best_price_name, best_price_model = trainer.select_best_model(price_results)
    best_rent_name, best_rent_model = trainer.select_best_model(rent_results)
    
    best_price_metrics = price_results[best_price_name]['metrics']
    best_rent_metrics = rent_results[best_rent_name]['metrics']
    
    print(f"  Price model: {best_price_name} (R2 = {best_price_metrics['r2']:.4f})")
    print(f"  Rent model: {best_rent_name} (R2 = {best_rent_metrics['r2']:.4f})")
    
    # ----------------------------------------------------------
    # Step 7: Save Models
    # ----------------------------------------------------------
    print("\nSTEP 7: Saving models...")
    print("-" * 60)
    
    models_dir = os.path.join(PROJECT_ROOT, 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Save the best models as primary models
    price_model_path = os.path.join(models_dir, 'price_model.pkl')
    with open(price_model_path, 'wb') as f:
        pickle.dump(best_price_model, f)
    print(f"  Price model saved ({best_price_name}): {price_model_path}")
    
    rent_model_path = os.path.join(models_dir, 'rent_model.pkl')
    with open(rent_model_path, 'wb') as f:
        pickle.dump(best_rent_model, f)
    print(f"  Rent model saved ({best_rent_name}): {rent_model_path}")
    
    # Save preprocessor
    preprocessor_path = os.path.join(models_dir, 'preprocessor.pkl')
    preprocessor.save(preprocessor_path)
    
    # Save metrics
    metrics = {
        'price_model': {
            'name': best_price_name,
            'r2': round(best_price_metrics['r2'], 4),
            'mae': round(best_price_metrics['mae'], 2),
            'rmse': round(best_price_metrics['rmse'], 2)
        },
        'rent_model': {
            'name': best_rent_name,
            'r2': round(best_rent_metrics['r2'], 4),
            'mae': round(best_rent_metrics['mae'], 2),
            'rmse': round(best_rent_metrics['rmse'], 2)
        },
        'ridge_coefs': price_results['Ridge']['model'].coef_.tolist(),
        'all_results': {
            'price': {name: {
                'r2': round(r['metrics']['r2'], 4),
                'mae': round(r['metrics']['mae'], 2),
                'rmse': round(r['metrics']['rmse'], 2)
            } for name, r in price_results.items()},
            'rent': {name: {
                'r2': round(r['metrics']['r2'], 4),
                'mae': round(r['metrics']['mae'], 2),
                'rmse': round(r['metrics']['rmse'], 2)
            } for name, r in rent_results.items()}
        }
    }
    
    metrics_path = os.path.join(models_dir, 'metrics.pkl')
    with open(metrics_path, 'wb') as f:
        pickle.dump(metrics, f)
    print(f"  Metrics saved: {metrics_path}")
    
    # ----------------------------------------------------------
    # Step 8: Print Summary
    # ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("  TRAINING RESULTS SUMMARY")
    print("=" * 60)
    
    # Price models comparison table
    print("\n  Price Prediction Models:")
    print("  " + "-" * 50)
    print(f"  {'Model':<20} {'R2':>8} {'MAE':>10} {'RMSE':>10}")
    print("  " + "-" * 50)
    for name, result in price_results.items():
        m = result['metrics']
        marker = " <-- Saved" if name == best_price_name else ""
        print(f"  {name:<20} {m['r2']:>8.4f} {m['mae']:>10.2f} {m['rmse']:>10.2f}{marker}")
    print("  " + "-" * 50)
    
    # Rent models comparison table
    print(f"\n  Rent Prediction Models:")
    print("  " + "-" * 50)
    print(f"  {'Model':<20} {'R2':>8} {'MAE':>10} {'RMSE':>10}")
    print("  " + "-" * 50)
    for name, result in rent_results.items():
        m = result['metrics']
        marker = " <-- Saved" if name == best_rent_name else ""
        print(f"  {name:<20} {m['r2']:>8.4f} {m['mae']:>10.2f} {m['rmse']:>10.2f}{marker}")
    print("  " + "-" * 50)
    
    print(f"\n  Note: Best models ({best_price_name} & {best_rent_name}) saved for FastAPI deployment")
    
    print("\n" + "=" * 60)
    print("  Training Complete!")
    print(f"  Models saved to: {models_dir}/")
    print("  Run locally: python run.py")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
