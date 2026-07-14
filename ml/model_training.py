"""
Model Training Module
======================
3 ML models train karta hai aur compare karta hai.

Models (Stanford ML course se):
1. LinearRegression — Normal Equation (closed-form solution)
2. Ridge Regression — L2 Regularization (overfitting rokne ke liye)
3. Random Forest — Ensemble method (bagging + decision trees)
"""

import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from ml.evaluate import calculate_r2, calculate_mae, calculate_rmse


class ModelTrainer:
    """
    ML Model Trainer for Real Estate Prediction.
    
    3 models train karta hai, evaluate karta hai, aur best model select karta hai.
    """
    
    def __init__(self):
        """ModelTrainer initialize karo."""
        self.models = {}
        print("ModelTrainer initialized")
    
    def train_all_models(self, X_train, y_train, X_test, y_test, target_name='target'):
        """
        3 models train karo aur unke metrics calculate karo.
        
        Models:
        1. LinearRegression — y = Xw + b (closed-form solution)
        2. Ridge(alpha=1.0) — y = Xw + b, with L2 penalty: ||w||^2
        3. RandomForest(n_estimators=300) — Ensemble of decision trees
        
        Args:
            X_train: Training features (n_samples, n_features)
            y_train: Training targets (n_samples,)
            X_test: Test features
            y_test: Test targets
            target_name: Name of target variable (for display)
        
        Returns:
            dict: {model_name: {model, metrics}}
        """
        print(f"\n{'=' * 60}")
        print(f"Training models for: {target_name.upper()}")
        print(f"{'=' * 60}")
        print(f"  Training set size: {X_train.shape[0]}")
        print(f"  Test set size: {X_test.shape[0]}")
        print(f"  Features: {X_train.shape[1]}")
        
        results = {}
        
        # ---- Model 1: Linear Regression (Baseline) ----
        # Normal Equation: w = (X^T X)^(-1) X^T y
        print(f"\n  Model 1: Linear Regression (Baseline)...")
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        lr_metrics = self.evaluate(lr_model, X_test, y_test)
        results['LinearRegression'] = {
            'model': lr_model,
            'metrics': lr_metrics
        }
        print(f"  R2 = {lr_metrics['r2']:.4f}")
        
        # ---- Model 2: Ridge Regression (Regularized) ----
        # Cost function: J(w) = MSE + alpha * ||w||^2
        print(f"\n  Model 2: Ridge Regression (L2 Regularized)...")
        ridge_model = Ridge(alpha=1.0)
        ridge_model.fit(X_train, y_train)
        ridge_metrics = self.evaluate(ridge_model, X_test, y_test)
        results['Ridge'] = {
            'model': ridge_model,
            'metrics': ridge_metrics
        }
        print(f"  R2 = {ridge_metrics['r2']:.4f}")
        
        # ---- Model 3: Random Forest (Ensemble) ----
        # 300 decision trees, max_depth=15, min_samples_split=5
        # Tuned for better accuracy while avoiding overfitting
        print(f"\n  Model 3: Random Forest (Ensemble, tuned)...")
        rf_model = RandomForestRegressor(
            n_estimators=40,
            max_depth=16,
            min_samples_split=4,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        rf_metrics = self.evaluate(rf_model, X_test, y_test)
        results['RandomForest'] = {
            'model': rf_model,
            'metrics': rf_metrics
        }
        print(f"  R2 = {rf_metrics['r2']:.4f}")
        
        # Store models
        self.models[target_name] = results
        
        # Results summary
        separator = '-' * 60
        print(f"\n{separator}")
        print(f"Results Summary for {target_name.upper()}:")
        print(f"{separator}")
        print(f"{'Model':<25} {'R2':>8} {'MAE':>12} {'RMSE':>12}")
        print(f"{separator}")
        for name, data in results.items():
            m = data['metrics']
            print(f"{name:<25} {m['r2']:>8.4f} {m['mae']:>12.4f} {m['rmse']:>12.4f}")
        print(f"{separator}")
        
        return results
    
    def evaluate(self, model, X_test, y_test):
        """
        Ek model ko evaluate karo test data pe.
        
        Returns:
            dict: {r2, mae, rmse}
        """
        y_pred = model.predict(X_test)
        
        return {
            'r2': calculate_r2(y_test, y_pred),
            'mae': calculate_mae(y_test, y_pred),
            'rmse': calculate_rmse(y_test, y_pred)
        }
    
    def select_best_model(self, results):
        """
        Best model select karo based on R2 score.
        R2 = 1.0 means perfect prediction.
        
        Returns:
            tuple: (best_model_name, best_model_object)
        """
        best_name = None
        best_r2 = -float('inf')
        
        for name, data in results.items():
            r2 = data['metrics']['r2']
            if r2 > best_r2:
                best_r2 = r2
                best_name = name
        
        print(f"\nBest Model: {best_name} (R2 = {best_r2:.4f})")
        
        return best_name, results[best_name]['model']
