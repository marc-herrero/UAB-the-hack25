import numpy as np
import pandas as pd
from scipy.interpolate import griddata


def get_interpolated_irradiance_df(irradiance_df: pd.DataFrame, terrain_df: pd.DataFrame) -> pd.DataFrame:
    points = irradiance_df[['latitude', 'longitude']].values
    values = irradiance_df['irradiance'].values

    target_points = terrain_df[['latitude', 'longitude']].values

    interpolated_values = griddata(points, values, target_points, method='cubic')

    nan_mask = np.isnan(interpolated_values)
    if np.any(nan_mask):
        print(f"Found {np.sum(nan_mask)} NaN values in interpolated data.")
        interpolated_nn = griddata(points, values, target_points, method='nearest')
        interpolated_values[nan_mask] = interpolated_nn[nan_mask]
        print("Replaced NaN values with nearest neighbor interpolation")

    interpolated_df = pd.DataFrame({
        'latitude': terrain_df['latitude'],
        'longitude': terrain_df['longitude'],
        'irradiance': interpolated_values
    })
    
    return interpolated_df