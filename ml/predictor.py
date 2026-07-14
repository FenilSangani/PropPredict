"""
Real Estate Predictor — Main Interface
=======================================
Ye class Flask backend ke liye MAIN interface hai.

Flask se direct isko use karenge:
    predictor = RealEstatePredictor()
    result = predictor.predict(input_data)

Ye internally preprocessor aur trained models load karke
prediction return karta hai.
"""

import os
import pickle
import numpy as np


class RealEstatePredictor:
    """
    Real Estate Price & Rent Predictor.
    
    Ye class trained models aur preprocessor ko load karke
    user input se predictions generate karta hai.
    
    Usage:
        predictor = RealEstatePredictor(models_dir='models')
        
        result = predictor.predict({
            'city': 'Mumbai',
            'locality': 'Bandra',
            'property_type': 'Flat',
            'size_sqft': 1200,
            'bedrooms': 2,
            'bathrooms': 2,
            'floor': 5,
            'age_years': 3,
            'furnishing': 'Semi-Furnished',
            'parking': 1
        })
        
        print(result)  # {'price_lakhs': 350.5, 'rent_monthly': 45000.0}
    """
    
    def __init__(self, models_dir='models'):
        """
        Predictor initialize karo.
        
        Args:
            models_dir: Directory jahan trained models saved hain
        
        Instance Variables:
            models_dir: Models directory path
            price_model: Trained price prediction model
            rent_model: Trained rent prediction model
            preprocessor: Fitted DataPreprocessor
            metrics: Saved model metrics
            is_loaded: Kya models load ho chuke hain?
        """
        self.models_dir = models_dir
        self.price_model = None
        self.rent_model = None
        self.preprocessor = None
        self.metrics = None
        self.is_loaded = False
        
        # Try to load models
        self.load_models()
    
    def load_models(self):
        """
        Saved models aur preprocessor load karo.
        
        Files expected:
            - models/price_model.pkl
            - models/rent_model.pkl  
            - models/preprocessor.pkl
            - models/metrics.pkl (optional)
        
        Gracefully handle karta hai agar files nahi milti.
        """
        price_path = os.path.join(self.models_dir, 'price_model.pkl')
        rent_path = os.path.join(self.models_dir, 'rent_model.pkl')
        preprocessor_path = os.path.join(self.models_dir, 'preprocessor.pkl')
        metrics_path = os.path.join(self.models_dir, 'metrics.pkl')
        
        try:
            # Price model load karo
            if not os.path.exists(price_path):
                print(f"⚠️ Price model not found at: {price_path}")
                print("   Please run train.py first to train models.")
                return
            
            with open(price_path, 'rb') as f:
                self.price_model = pickle.load(f)
            print(f"✅ Price model loaded")
            
            # Rent model load karo
            if not os.path.exists(rent_path):
                print(f"⚠️ Rent model not found at: {rent_path}")
                print("   Please run train.py first to train models.")
                return
            
            with open(rent_path, 'rb') as f:
                self.rent_model = pickle.load(f)
            print(f"✅ Rent model loaded")
            
            # Preprocessor load karo
            if not os.path.exists(preprocessor_path):
                print(f"⚠️ Preprocessor not found at: {preprocessor_path}")
                print("   Please run train.py first to train models.")
                return
            
            # Preprocessor ko manually load karo (pickle dict hai)
            with open(preprocessor_path, 'rb') as f:
                preprocessor_data = pickle.load(f)
            
            # DataPreprocessor object banao aur data set karo
            from ml.data_preprocessing import DataPreprocessor
            self.preprocessor = DataPreprocessor()
            self.preprocessor.encoder = preprocessor_data['encoder']
            self.preprocessor.scaler = preprocessor_data['scaler']
            self.preprocessor.feature_names = preprocessor_data['feature_names']
            self.preprocessor.is_fitted = preprocessor_data['is_fitted']
            print(f"✅ Preprocessor loaded")
            
            # Metrics load karo (optional)
            if os.path.exists(metrics_path):
                with open(metrics_path, 'rb') as f:
                    self.metrics = pickle.load(f)
                print(f"✅ Metrics loaded")
            
            self.is_loaded = True
            print(f"\n🎉 All models loaded successfully from '{self.models_dir}/'")
            
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            print("   Please run train.py first to train models.")
            self.is_loaded = False
    
    def predict(self, input_data):
        """
        Property ki price aur rent predict karo.
        
        Args:
            input_data: Dictionary with property details:
                {
                    'city': str,
                    'locality': str,
                    'property_type': str,
                    'size_sqft': int/float,
                    'bedrooms': int,
                    'bathrooms': int,
                    'floor': int,
                    'age_years': int,
                    'furnishing': str,
                    'parking': int (0 or 1)
                }
        
        Returns:
            dict: {
                'price_lakhs': float,
                'rent_monthly': float,
                'status': 'success' or 'error',
                'message': str
            }
        """
        # Check: Models loaded hain ya nahi?
        if not self.is_loaded:
            return {
                'price_lakhs': None,
                'rent_monthly': None,
                'status': 'error',
                'message': '❌ Models not loaded! Please run train.py first to train the models.'
            }
        
        try:
            # Input data ko preprocess karo
            X = self.preprocessor.transform(input_data)
            
            # Price predict karo
            price_pred = self.price_model.predict(X)[0]
            price_pred = max(price_pred, 0)  # Negative price nahi ho sakti
            
            # Rent predict karo
            rent_pred = self.rent_model.predict(X)[0]
            rent_pred = max(rent_pred, 0)  # Negative rent nahi ho sakta
            
            return {
                'price_lakhs': round(float(price_pred), 2),
                'rent_monthly': round(float(rent_pred), 0),
                'status': 'success',
                'message': 'Prediction successful!'
            }
            
        except Exception as e:
            return {
                'price_lakhs': None,
                'rent_monthly': None,
                'status': 'error',
                'message': f'❌ Prediction error: {str(e)}'
            }
    
    def get_localities(self, city):
        """
        City ki localities return karo.
        
        Args:
            city: City name (Mumbai/Delhi/Bangalore)
        
        Returns:
            list: Locality names
        """
        # Agar preprocessor loaded hai toh usse localities lo
        if self.preprocessor:
            return self.preprocessor.get_localities(city)
        
        # Fallback — hardcoded localities
        from ml.data_preprocessing import CITY_LOCALITIES
        return CITY_LOCALITIES.get(city, [])
    
    def get_model_metrics(self):
        """
        Saved model metrics return karo.
        
        Returns:
            dict: Metrics dictionary, ya error message agar nahi hai
        """
        if self.metrics:
            return self.metrics
        
        return {
            'status': 'error',
            'message': 'Metrics not available. Please train models first.'
        }
    
    def get_feature_importance(self):
        """
        Random Forest model se feature importance extract karo.
        
        Feature importance batata hai ki kaunsa feature price/rent
        predict karne mein kitna important hai.
        
        Returns:
            dict: {
                'price_features': {feature_name: importance_score},
                'rent_features': {feature_name: importance_score}
            }
        """
        if not self.is_loaded:
            return {
                'status': 'error',
                'message': 'Models not loaded. Please train models first.'
            }
        
        result = {}
        
        # Price model ki feature importance
        if hasattr(self.price_model, 'feature_importances_'):
            importances = self.price_model.feature_importances_
            feature_names = self.preprocessor.feature_names
            
            # Sort by importance (descending)
            indices = np.argsort(importances)[::-1]
            
            price_features = {}
            for i in indices[:15]:  # Top 15 features
                price_features[feature_names[i]] = round(float(importances[i]), 4)
            
            result['price_features'] = price_features
        else:
            result['price_features'] = {
                'message': 'Feature importance not available for this model type'
            }
        
        # Rent model ki feature importance
        if hasattr(self.rent_model, 'feature_importances_'):
            importances = self.rent_model.feature_importances_
            feature_names = self.preprocessor.feature_names
            
            indices = np.argsort(importances)[::-1]
            
            rent_features = {}
            for i in indices[:15]:
                rent_features[feature_names[i]] = round(float(importances[i]), 4)
            
            result['rent_features'] = rent_features
        else:
            result['rent_features'] = {
                'message': 'Feature importance not available for this model type'
            }
        
        return result
