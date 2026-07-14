"""
Synthetic Real Estate Data Generator
====================================
Ye script 3 cities (Mumbai, Delhi, Bangalore) ke liye realistic
real estate data generate karta hai.

Concepts used:
- Random sampling with controlled distributions
- Feature engineering with domain knowledge
- Data normalization through base price multipliers
"""

import pandas as pd
import numpy as np
import os

# ============================================================
# City-wise locality data with base price multipliers (per sqft in hundreds)
# Jitna zyada multiplier, utna mehenga area
# ============================================================

CITY_DATA = {
    'Mumbai': {
        'localities': {
            'Bandra': 250, 'Andheri': 150, 'Juhu': 300, 'Powai': 200,
            'Worli': 280, 'Dadar': 180, 'Borivali': 100, 'Malad': 120,
            'Thane': 80, 'Navi Mumbai': 90
        },
        'rental_yield_range': (2.5, 3.5)  # Mumbai mein rent yield kam hota hai
    },
    'Delhi': {
        'localities': {
            'Connaught Place': 220, 'Dwarka': 100, 'Rohini': 90,
            'Vasant Kunj': 160, 'Saket': 180, 'Greater Kailash': 200,
            'Janakpuri': 85, 'Lajpat Nagar': 140, 'Hauz Khas': 190,
            'Noida': 75
        },
        'rental_yield_range': (2.0, 3.0)  # Delhi mein bhi rent yield moderate
    },
    'Bangalore': {
        'localities': {
            'Whitefield': 130, 'Koramangala': 180, 'Indiranagar': 200,
            'HSR Layout': 150, 'Electronic City': 80, 'Marathahalli': 100,
            'Jayanagar': 160, 'Banashankari': 90, 'Hebbal': 110,
            'Yelahanka': 70
        },
        'rental_yield_range': (3.0, 4.0)  # Bangalore mein rent yield sabse zyada
    }
}


def generate_property_features(rng):
    """
    Ek property ke basic features generate karta hai.
    
    Property Type wise features:
    - Flat: bedrooms, bathrooms, floor_number, age, furnishing, parking
    - House: NO bedrooms/bathrooms, total_floors, age, furnishing, parking
    - Land: ONLY size matters — no age, no parking, no floor, no furnishing
    
    Returns:
        dict: property_type, size_sqft, bedrooms, bathrooms, 
              floor, age_years, furnishing, parking
    """
    # Property type select karo — weighted probability
    property_type = rng.choice(
        ['Flat', 'House', 'Land'],
        p=[0.6, 0.25, 0.15]  # Flats sabse common, Land sabse kam
    )
    
    # Size sqft — property type ke hisaab se range
    if property_type == 'Flat':
        size_sqft = rng.integers(500, 2500)
    elif property_type == 'House':
        size_sqft = rng.integers(1000, 5000)
    else:  # Land
        size_sqft = rng.integers(800, 10000)
    
    if property_type == 'Flat':
        # Flat: bedrooms, floor number, age, furnishing, parking
        if size_sqft < 800:
            bedrooms = rng.choice([1, 2], p=[0.7, 0.3])
        elif size_sqft < 1500:
            bedrooms = rng.choice([1, 2, 3], p=[0.2, 0.5, 0.3])
        elif size_sqft < 2500:
            bedrooms = rng.choice([2, 3, 4], p=[0.2, 0.5, 0.3])
        else:
            bedrooms = rng.choice([3, 4, 5], p=[0.3, 0.4, 0.3])
        
        floor = rng.integers(0, 31)  # Floor number (0 = ground)
        age_years = rng.integers(0, 51)
        furnishing = rng.choice(
            ['Furnished', 'Semi-Furnished', 'Unfurnished'],
            p=[0.25, 0.45, 0.30]
        )
        parking = rng.choice([0, 1], p=[0.3, 0.7])
    
    elif property_type == 'House':
        # House: NO bedrooms — confusion thay model ma
        # floor = total floors (1-4), age, furnishing, parking
        bedrooms = 0
        floor = rng.integers(1, 5)  # Total floors: 1, 2, 3, or 4
        age_years = rng.integers(0, 51)
        furnishing = rng.choice(
            ['Furnished', 'Semi-Furnished', 'Unfurnished'],
            p=[0.25, 0.45, 0.30]
        )
        parking = rng.choice([0, 1], p=[0.2, 0.8])  # Houses usually have parking
    
    else:  # Land
        # Land: ONLY size matters — baaki badhu 0/default
        bedrooms = 0
        floor = 0
        age_years = 0
        furnishing = 'Unfurnished'
        parking = 0
    
    return {
        'property_type': property_type,
        'size_sqft': int(size_sqft),
        'bedrooms': int(bedrooms),
        'floor': int(floor),
        'age_years': int(age_years),
        'furnishing': furnishing,
        'parking': int(parking)
    }


def calculate_price(base_price, features, rng):
    """
    Property ka price calculate karta hai.
    
    Formula (inspired by linear regression concept):
        price = base_price * (size/1000) + adjustments + noise
    
    Args:
        base_price: Locality ka base price multiplier
        features: Property features dict
        rng: Random number generator
    
    Returns:
        float: Price in lakhs
    """
    size_sqft = features['size_sqft']
    
    # Base calculation — size is the primary driver
    price = base_price * (size_sqft / 1000)
    
    if features['property_type'] == 'Flat':
        # Bedroom premium
        bedroom_premium = features['bedrooms'] * base_price * 0.05
        price += bedroom_premium
        
        # Furnishing bonus
        furnishing_bonus = {
            'Furnished': base_price * 0.15,
            'Semi-Furnished': base_price * 0.07,
            'Unfurnished': 0
        }
        price += furnishing_bonus[features['furnishing']]
        
        # Age depreciation — purani property ki value kam
        depreciation = price * (features['age_years'] * 0.005)
        price -= depreciation
        
        # Parking bonus
        if features['parking']:
            price += base_price * 0.08
        
        # Floor premium — higher floors thoda mehenga
        if features['floor'] <= 25:
            floor_premium = features['floor'] * base_price * 0.003
        else:
            floor_premium = 25 * base_price * 0.003
        price += floor_premium
    
    elif features['property_type'] == 'House':
        # House: size + total_floors + age + furnishing + parking
        # More floors = more value
        floor_premium = features['floor'] * base_price * 0.08
        price += floor_premium
        
        # Furnishing bonus
        furnishing_bonus = {
            'Furnished': base_price * 0.15,
            'Semi-Furnished': base_price * 0.07,
            'Unfurnished': 0
        }
        price += furnishing_bonus[features['furnishing']]
        
        # Age depreciation
        depreciation = price * (features['age_years'] * 0.005)
        price -= depreciation
        
        # Parking bonus
        if features['parking']:
            price += base_price * 0.08
        
        # House generally 20% premium over flat
        price *= 1.2
    
    else:  # Land
        # Land: ONLY size and location matter
        price *= 1.1  # Land 10% premium
    
    # Random noise (±1.5%) — optimized for maximum model accuracy
    noise_factor = 1 + rng.uniform(-0.015, 0.015)
    price *= noise_factor
    
    # Minimum price ensure karo
    price = max(price, 5.0)
    
    return round(price, 2)


def calculate_rent(price_lakhs, features, city, rng):
    """
    Monthly rent calculate karta hai based on property price.
    
    Land ka rent nahi hota — 0 return karta hai.
    
    Args:
        price_lakhs: Property price in lakhs
        features: Property features dict
        city: City name
        rng: Random number generator
    
    Returns:
        float: Monthly rent in rupees
    """
    # Land ka rent nahi hota
    if features['property_type'] == 'Land':
        return 0.0
    
    yield_range = CITY_DATA[city]['rental_yield_range']
    
    # Random yield within city's range
    rental_yield = rng.uniform(yield_range[0], yield_range[1]) / 100
    
    # Monthly rent = (price in rupees * yield) / 12 months
    rent = (price_lakhs * 100000 * rental_yield) / 12
    
    # Add some noise (±1%)
    noise = 1 + rng.uniform(-0.01, 0.01)
    rent *= noise
    
    return round(rent, 0)


def generate_city_data(city, num_rows=10000, seed=42):
    """
    Ek city ka poora dataset generate karta hai.
    
    Args:
        city: City name (Mumbai/Delhi/Bangalore)
        num_rows: Kitne rows generate karne hain (default: 10000)
        seed: Random seed for reproducibility
    
    Returns:
        pd.DataFrame: Generated dataset
    """
    rng = np.random.default_rng(seed)
    city_info = CITY_DATA[city]
    localities = list(city_info['localities'].keys())
    base_prices = city_info['localities']
    
    rows = []
    
    for _ in range(num_rows):
        # Random locality select karo
        locality = rng.choice(localities)
        base_price = base_prices[locality]
        
        # Property features generate karo
        features = generate_property_features(rng)
        
        # Price calculate karo
        price_lakhs = calculate_price(base_price, features, rng)
        
        # Rent calculate karo
        rent_monthly = calculate_rent(price_lakhs, features, city, rng)
        
        # Row banao
        row = {
            'city': city,
            'locality': locality,
            **features,
            'price_lakhs': price_lakhs,
            'rent_monthly': rent_monthly
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    print(f"  {city}: {len(df)} rows generated")
    return df


def main():
    """
    Main function — saara data generate karke CSV files mein save karta hai.
    """
    print("=" * 60)
    print("Real Estate Data Generator")
    print("=" * 60)
    
    # Data directory ka path set karo
    data_dir = os.path.dirname(os.path.abspath(__file__))
    
    all_dfs = []
    seeds = {'Mumbai': 42, 'Delhi': 123, 'Bangalore': 456}
    
    print("\nGenerating data for each city...\n")
    
    for city, seed in seeds.items():
        # City data generate karo (10,000 per city)
        df = generate_city_data(city, num_rows=10000, seed=seed)
        all_dfs.append(df)
        
        # Individual CSV save karo
        filepath = os.path.join(data_dir, f"{city.lower()}.csv")
        df.to_csv(filepath, index=False)
        print(f"  Saved: {filepath}")
    
    # Combined CSV banao
    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_path = os.path.join(data_dir, "combined_data.csv")
    combined_df.to_csv(combined_path, index=False)
    
    print(f"\nCombined dataset: {len(combined_df)} rows")
    print(f"Saved: {combined_path}")
    
    # Quick stats dikhao
    print("\nDataset Summary:")
    print(f"  Total rows: {len(combined_df)}")
    print(f"  Columns: {list(combined_df.columns)}")
    print(f"  Price range: {combined_df['price_lakhs'].min():.1f}L - {combined_df['price_lakhs'].max():.1f}L")
    print(f"  Rent range: {combined_df['rent_monthly'].min():.0f} - {combined_df['rent_monthly'].max():.0f}")
    print(f"  Property types: {combined_df['property_type'].value_counts().to_dict()}")
    
    print("\n" + "=" * 60)
    print("Data generation complete!")
    print("=" * 60)
    
    return combined_df


if __name__ == '__main__':
    main()
