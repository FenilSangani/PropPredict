"""
Model Evaluation Metrics
========================
Ye module ML models ke performance metrics calculate karta hai.

Metrics used (Stanford ML course se):
- R² Score: Model kitna variance explain karta hai (1.0 = perfect)
- MAE: Average absolute error (interpretable in same units)
- RMSE: Root mean squared error (penalizes large errors more)
"""

import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


def calculate_r2(y_true, y_pred):
    """
    R² (Coefficient of Determination) calculate karta hai.
    
    R² = 1 - (SS_res / SS_tot)
    - 1.0 means perfect prediction
    - 0.0 means model is as good as predicting the mean
    - Negative means model is worse than mean
    
    Args:
        y_true: Actual values (ground truth)
        y_pred: Predicted values
    
    Returns:
        float: R² score
    """
    return r2_score(y_true, y_pred)


def calculate_mae(y_true, y_pred):
    """
    Mean Absolute Error calculate karta hai.
    
    MAE = (1/n) * Σ|y_true - y_pred|
    
    Easy to interpret — average kitna off hai prediction.
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
    
    Returns:
        float: MAE value
    """
    return mean_absolute_error(y_true, y_pred)


def calculate_rmse(y_true, y_pred):
    """
    Root Mean Squared Error calculate karta hai.
    
    RMSE = sqrt((1/n) * Σ(y_true - y_pred)²)
    
    Bade errors ko zyada penalize karta hai (squared term ki wajah se).
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
    
    Returns:
        float: RMSE value
    """
    return np.sqrt(mean_squared_error(y_true, y_pred))


def print_metrics(metrics_dict):
    """
    Metrics ko ek clean table format mein print karta hai.
    
    Args:
        metrics_dict: Dictionary with keys 'r2', 'mae', 'rmse'
    """
    print("\n" + "-" * 40)
    print(f"  R² Score : {metrics_dict['r2']:.4f}")
    print(f"  MAE      : {metrics_dict['mae']:.4f}")
    print(f"  RMSE     : {metrics_dict['rmse']:.4f}")
    print("-" * 40)
