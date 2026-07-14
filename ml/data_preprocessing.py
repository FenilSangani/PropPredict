"""
Data Preprocessing Pipeline
============================
Ye module raw real estate data ko ML-ready format mein convert karta hai.

Steps (Stanford ML course ke concepts):
1. Missing values handle karo (fillna)
2. Categorical features ko One-Hot Encode karo
3. Numerical features ko StandardScaler se normalize karo
   (Feature Scaling: x_norm = (x - mean) / std)
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import pickle
import os


# ============================================================
# City-locality mapping
# ============================================================
CITY_LOCALITIES = {
    'Mumbai': ['Bandra', 'Andheri', 'Juhu', 'Powai', 'Worli',
               'Dadar', 'Borivali', 'Malad', 'Thane', 'Navi Mumbai'],
    'Delhi': ['Connaught Place', 'Dwarka', 'Rohini', 'Vasant Kunj',
              'Saket', 'Greater Kailash', 'Janakpuri', 'Lajpat Nagar',
              'Hauz Khas', 'Noida'],
    'Bangalore': ['Whitefield', 'Koramangala', 'Indiranagar', 'HSR Layout',
                  'Electronic City', 'Marathahalli', 'Jayanagar',
                  'Banashankari', 'Hebbal', 'Yelahanka']
}


class DataPreprocessor:
    """
    Data Preprocessing Pipeline for Real Estate Data.
    
    Steps:
    - Categorical encoding (One-Hot)
    - Numerical scaling (StandardScaler)
    - Missing value handling
    """
    
    # Categorical aur numerical columns define karo
    CATEGORICAL_COLS = ['city', 'locality', 'property_type', 'furnishing']
    NUMERICAL_COLS = ['size_sqft', 'bedrooms', 'floor', 'age_years']
    PASSTHROUGH_COLS = ['parking']  # Already 0/1, scaling ki zaroorat nahi
    
    def __init__(self):
        """Preprocessor initialize karo."""
        # OneHotEncoder — unknown categories ko ignore karega
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        
        # StandardScaler — mean=0, std=1 normalization
        # (Feature Scaling from Stanford ML course)
        self.scaler = StandardScaler()
        
        self.feature_names = None
        self.is_fitted = False
        
        print("DataPreprocessor initialized")
    
    def fit_transform(self, df):
        """
        Raw DataFrame pe fit karo aur transform karo.
        
        Returns:
            tuple: (X_price, y_price, X_rent, y_rent)
        """
        print("\nPreprocessing data...")
        df = df.copy()
        
        # Step 1: Missing values handle karo
        for col in self.NUMERICAL_COLS:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        for col in self.CATEGORICAL_COLS:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].mode()[0])
        
        df['parking'] = df['parking'].fillna(0)
        
        print("  Missing values handled")
        
        # Step 2: One-Hot Encoding for categorical features
        # city='Mumbai' -> [1, 0, 0], city='Delhi' -> [0, 1, 0]
        cat_encoded = self.encoder.fit_transform(df[self.CATEGORICAL_COLS])
        cat_feature_names = self.encoder.get_feature_names_out(self.CATEGORICAL_COLS)
        print(f"  One-Hot Encoding done: {len(cat_feature_names)} categorical features")
        
        # Step 3: Standard Scaling for numerical features
        # x_scaled = (x - mean) / std_dev
        num_scaled = self.scaler.fit_transform(df[self.NUMERICAL_COLS])
        print(f"  Standard Scaling done: {len(self.NUMERICAL_COLS)} numerical features")
        
        # Step 4: Sab features combine karo
        passthrough = df[self.PASSTHROUGH_COLS].values
        
        X = np.hstack([num_scaled, cat_encoded, passthrough])
        
        # Feature names store karo
        self.feature_names = (
            list(self.NUMERICAL_COLS) + 
            list(cat_feature_names) + 
            list(self.PASSTHROUGH_COLS)
        )
        
        # Target variables extract karo
        y_price = df['price_lakhs'].values
        y_rent = df['rent_monthly'].values
        
        self.is_fitted = True
        
        print(f"\n  Final feature matrix shape: {X.shape}")
        print(f"  Features: {len(self.feature_names)} total")
        print(f"     - Numerical: {len(self.NUMERICAL_COLS)}")
        print(f"     - Categorical (encoded): {len(cat_feature_names)}")
        print(f"     - Passthrough: {len(self.PASSTHROUGH_COLS)}")
        
        return X, y_price, X, y_rent
    
    def transform(self, input_dict):
        """
        Single input dict ko transform karo (prediction ke liye).
        
        Args:
            input_dict: Dictionary with property details
        
        Returns:
            np.array: Transformed feature vector (1, n_features)
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor is not fitted yet! Pehle fit_transform() call karo.")
        
        # Input dict se DataFrame banao (single row)
        df = pd.DataFrame([input_dict])
        
        # Missing values ke liye defaults
        for col in self.NUMERICAL_COLS:
            if col not in df.columns:
                df[col] = 0
        for col in self.CATEGORICAL_COLS:
            if col not in df.columns:
                df[col] = 'Unknown'
        if 'parking' not in df.columns:
            df['parking'] = 0
        
        # Same transformations apply karo (transform, NOT fit_transform)
        cat_encoded = self.encoder.transform(df[self.CATEGORICAL_COLS])
        num_scaled = self.scaler.transform(df[self.NUMERICAL_COLS])
        passthrough = df[self.PASSTHROUGH_COLS].values
        
        # Combine karo
        X = np.hstack([num_scaled, cat_encoded, passthrough])
        
        return X
    
    def save(self, path):
        """Fitted preprocessor ko pickle file mein save karo."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump({
                'encoder': self.encoder,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'is_fitted': self.is_fitted
            }, f)
        
        print(f"Preprocessor saved to: {path}")
    
    def load(self, path):
        """Saved preprocessor ko load karo."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Preprocessor file not found: {path}")
        
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.encoder = data['encoder']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.is_fitted = data['is_fitted']
        
        print(f"Preprocessor loaded from: {path}")
    
    def get_localities(self, city):
        """Ek city ki saari localities return karta hai."""
        if city in CITY_LOCALITIES:
            return CITY_LOCALITIES[city]
        else:
            print(f"City '{city}' not found. Available: {list(CITY_LOCALITIES.keys())}")
            return []
