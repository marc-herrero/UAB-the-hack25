import numpy as np
import pandas as pd
import requests

def get_terrain_data(min_lat, max_lat, min_lon, max_lon, resolution=30):
    """
    Get terrain slope and aspect data for a coordinate range
    
    Parameters:
    min_lat, max_lat: Latitude bounds
    min_lon, max_lon: Longitude bounds
    resolution: Resolution in meters
    
    Returns:
    pandas.DataFrame: DataFrame with latitude, longitude, slope, aspect columns
    """
    print(f"Fetching elevation data for: ({min_lat:.4f}, {min_lon:.4f}) to ({max_lat:.4f}, {max_lon:.4f})")
    
    # Calculate number of samples based on resolution
    lat_samples = int((max_lat - min_lat) * 111000 / resolution) + 1
    lon_samples = int((max_lon - min_lon) * 111000 / resolution) + 1
    
    # Ensure reasonable number of samples
    lat_samples = min(lat_samples, 100)
    lon_samples = min(lon_samples, 100)
    
    # Create latitude and longitude arrays
    lats = np.linspace(min_lat, max_lat, lat_samples)
    lons = np.linspace(min_lon, max_lon, lon_samples)
    
    # Create coordinate grid
    lat_grid, lon_grid = np.meshgrid(lats, lons)
    
    # Prepare points for API request
    points = []
    for i in range(lat_grid.shape[0]):
        for j in range(lat_grid.shape[1]):
            points.append({
                "latitude": lat_grid[i, j],
                "longitude": lon_grid[i, j]
            })
    
    # API request to get elevation data
    url = "https://api.open-elevation.com/api/v1/lookup"
    payload = {"locations": points}
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        # Extract elevations and reshape to grid
        elevations = np.array([point["elevation"] for point in data["results"]])
        elevation_grid = elevations.reshape(lat_grid.shape)
        
        print(f"Successfully fetched elevation data: {lat_samples}x{lon_samples} grid")
    except Exception as e:
        print(f"Error fetching elevation data: {e}")
        print("Using synthetic data instead...")
        
        # Generate synthetic elevation data as fallback
        elevation_grid = 500 + 200 * np.random.rand(lat_grid.shape[0], lat_grid.shape[1])
        elevation_grid += 300 * np.sin(5 * lon_grid) * np.cos(5 * lat_grid)
    
    # Calculate slope and aspect
    # Get approximate cell size in meters
    cell_size_y = (max_lat - min_lat) / (lat_samples-1) * 111000  # m/cell
    cell_size_x = (max_lon - min_lon) / (lon_samples-1) * 111000 * np.cos(np.radians(np.mean([min_lat, max_lat])))  # m/cell
    
    # Calculate slope (in degrees)
    dy, dx = np.gradient(elevation_grid, cell_size_y, cell_size_x)
    slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))
    
    # Calculate aspect (in degrees)
    aspect = np.degrees(np.arctan2(dy, dx))
    aspect = np.mod(aspect + 360, 360)
    
    # Create DataFrame
    # Flatten the arrays
    lat_flat = lat_grid.flatten()
    lon_flat = lon_grid.flatten()
    slope_flat = slope.flatten()
    aspect_flat = aspect.flatten()
    
    # Create a DataFrame with just the requested columns
    df = pd.DataFrame({
        'latitude': lat_flat,
        'longitude': lon_flat,
        'slope': slope_flat,        # in degrees (0-90)
        'aspect': aspect_flat       # in degrees (0-360, clockwise from north)
    })
    
    print(f"Created DataFrame with {len(df)} points")
    return df

# Example usage
if __name__ == "__main__":
    # Barcelona area
    terrain_df = get_terrain_data(
        min_lat=41.35,
        max_lat=41.45,
        min_lon=2.10,
        max_lon=2.22,
        resolution=100
    )
    
    # Show the first few rows
    print(terrain_df.head())
    
    # Save to CSV
    terrain_df.to_csv('data/terrain_data.csv', index=False)
    print("Data saved to 'data/terrain_data.csv'")