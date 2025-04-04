from .get_slope_aspect import get_terrain_data
from .get_irradiation import get_interpolated_irradiance_df
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



def _calculate_solar_energy_production(irradiance, slope, aspect, latitude, panel_efficiency=0.2, panel_area=1.0):
    """
    Calculate solar panel energy production based on terrain data.
    
    Parameters:
    - irradiance: Solar irradiance in W/m²
    - slope: Terrain slope in degrees
    - aspect: Terrain aspect in degrees (0=North, 90=East, 180=South, 270=West)
    - latitude: Latitude of the location (determines optimal tilt and aspect)
    - panel_efficiency: Solar panel efficiency (default: 20%)
    - panel_area: Solar panel area in m² (default: 1 m²)
    
    Returns:
    - Energy production in Watts
    """
    # Determine optimal slope and aspect based on hemisphere
    in_northern_hemisphere = latitude > 0
    
    # Optimal tilt is approximately equal to the absolute latitude
    optimal_slope = np.abs(latitude)
    
    # Optimal aspect is South (180°) in Northern hemisphere, North (0° or 360°) in Southern
    optimal_aspect = 180 if in_northern_hemisphere else 0
    
    # Calculate slope factor
    slope_diff = abs(slope - optimal_slope)
    slope_factor = np.cos(np.radians(slope_diff * 0.8))  # More forgiving slope factor
    
    # Calculate aspect factor - but only if slope is significant enough for aspect to matter!
    aspect_diff = np.minimum(abs(aspect - optimal_aspect), 360 - abs(aspect - optimal_aspect))
    
    # Direct radiation component (directional)
    direct_component = 0.8  # 80% of energy is from direct radiation
    
    # East and West still get decent direct radiation (morning/afternoon)
    direct_factor = np.where(
        aspect_diff <= 90,  # Within 90° of optimal (S±90° = E to W in Northern)
        np.cos(np.radians(aspect_diff)),  # Cosine falloff for directions near optimal
        np.cos(np.radians(90)) * (1 - (aspect_diff - 90) / 90) * 0.5  # Gradual decline for other directions
    )
    direct_factor = np.maximum(direct_factor, 0.1)  # Even North gets some direct in summer
    
    # Diffuse radiation component (omnidirectional)
    diffuse_component = 0.2  # 20% of energy is from diffuse radiation
    diffuse_factor = 1.0  # Diffuse radiation comes from all directions
    
    # Combine direct and diffuse components
    aspect_factor_base = direct_component * direct_factor + diffuse_component * diffuse_factor
    
    aspect_weight = np.tanh(slope / 15.0)
    
    # Apply slope-dependent weighting to aspect factor
    aspect_factor = 1.0 - aspect_weight + aspect_weight * aspect_factor_base
    
    # Apply both factors to the irradiance
    adjusted_irradiance = irradiance * slope_factor * aspect_factor
    
    # Calculate energy production
    energy_production = adjusted_irradiance * panel_efficiency * panel_area
    
    return energy_production


raw_irradiance_data = pd.read_csv('data/irradiance_data_full_res2.csv')

def get_energy_production_df(min_lat=-26, max_lat=-25, min_lon=-71, max_lon=-70, resolution=30) -> pd.DataFrame:
    terrain_data = get_terrain_data(min_lat, max_lat, min_lon, max_lon, resolution=resolution)

    irradiance_data = get_interpolated_irradiance_df(raw_irradiance_data, terrain_data)

    # Extract slope and aspect from the terrain dataframe
    slope = terrain_data['slope'].values
    aspect = terrain_data['aspect'].values

    # Use mean latitude from the dataset for optimal tilt calculation
    mean_latitude = (terrain_data['latitude'].min() + terrain_data['latitude'].max()) / 2

    # Calculate energy production with improved model
    # Extract the irradiance values from the DataFrame
    irradiance_values = irradiance_data['irradiance'].values  # Replace 'irradiance' with actual column name
    energy_production = _calculate_solar_energy_production(irradiance_values, slope, aspect, mean_latitude)

    terrain_data['Energy Production (W)'] = energy_production
    return terrain_data


def create_3_plots(terrain_df):
    # Create a figure with 3 subplots (1 row, 3 columns)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Plot 1: Terrain Slope
    scatter1 = axes[0].scatter(
        terrain_df['longitude'], 
        terrain_df['latitude'], 
        c=terrain_df['slope'],
        cmap='viridis', 
        alpha=0.7,
        vmin=0,
        vmax=90
    )
    axes[0].set_title('Terrain Slope')
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')
    cbar1 = plt.colorbar(scatter1, ax=axes[0], label='Slope (degrees)')

    # Plot 2: Terrain Aspect
    scatter2 = axes[1].scatter(
        terrain_df['longitude'], 
        terrain_df['latitude'], 
        c=terrain_df['aspect'],
        cmap='hsv',  # Circular colormap for directional data
        alpha=0.7,
        vmin=0,
        vmax=360
    )
    axes[1].set_title('Terrain Aspect')
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')
    cbar2 = plt.colorbar(scatter2, ax=axes[1], label='Aspect (degrees)')
    cbar2.ax.set_yticks([0, 90, 180, 270, 360])
    cbar2.ax.set_yticklabels(['N (0°)', 'E (90°)', 'S (180°)', 'W (270°)', 'N (360°)'])

    # Plot 3: Solar Energy Production
    scatter3 = axes[2].scatter(
        terrain_df['longitude'], 
        terrain_df['latitude'], 
        c=terrain_df['Energy Production (W)'],
        cmap='hot', 
        alpha=0.7
    )
    axes[2].set_title('Solar Energy Production')
    axes[2].set_xlabel('Longitude')
    axes[2].set_ylabel('Latitude')
    cbar3 = plt.colorbar(scatter3, ax=axes[2], label='Energy Production (W)')

    plt.tight_layout()
    plt.suptitle('Terrain Analysis and Solar Energy Production Potential', fontsize=16, y=1.05)
    plt.savefig('images/terrain_solar_analysis_example.png', dpi=300, bbox_inches='tight')
    plt.show()


def create_information_plots(mean_latitude=-45, save_fig=False):
    # Create a grid of slope and aspect values
    slopes = np.linspace(0, 45, 10)  # Different slopes from flat to 45 degrees
    aspects = np.linspace(0, 359, 36)  # Different aspects all around
    slope_grid, aspect_grid = np.meshgrid(slopes, aspects)

    # Calculate energy for each combination
    energy_grid = np.zeros_like(slope_grid)
    for i in range(len(aspects)):
        for j in range(len(slopes)):
            energy_grid[i, j] = _calculate_solar_energy_production(
                1000, slopes[j], aspects[i], mean_latitude
            )

    # Convert to relative values (percentage of maximum)
    energy_rel = energy_grid / np.max(energy_grid) * 100

    # Create heatmap - Figure 1
    fig1 = plt.figure(figsize=(12, 10))
    im = plt.imshow(energy_rel, origin='lower', aspect='auto', cmap='hot',
                extent=[0, 45, 0, 360])
    plt.colorbar(im, label='Relative Energy Potential (%)')
    plt.xlabel('Slope (degrees)')
    plt.ylabel('Aspect (degrees)')
    plt.title('Solar Energy Potential by Slope and Aspect')
    plt.yticks([0, 45, 90, 135, 180, 225, 270, 315, 360], 
            ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    plt.grid(False)
    if save_fig:
        plt.savefig('images/slope_aspect_energy_matrix.png', dpi=300)

    # Create line plot - Figure 2
    fig2 = plt.figure(figsize=(10, 6))
    selected_slopes = [0, 5, 15, 30]
    for slp in selected_slopes:
        # Find the closest index in our slopes array
        slp_idx = np.abs(slopes - slp).argmin()
        energy_curve = energy_rel[:, slp_idx]
        plt.plot(aspects, energy_curve, label=f'Slope = {slp}Â°')

    plt.axvline(x=0, color='blue', linestyle='--', alpha=0.3)
    plt.axvline(x=90, color='green', linestyle='--', alpha=0.3)
    plt.axvline(x=180, color='red', linestyle='--', alpha=0.3)
    plt.axvline(x=270, color='purple', linestyle='--', alpha=0.3)
    plt.xlabel('Aspect (degrees)')
    plt.ylabel('Relative Energy Potential (%)')
    plt.title('Effect of Slope and Aspect on Solar Energy Production')
    plt.xlim(0, 359)
    plt.xticks([0, 45, 90, 135, 180, 225, 270, 315, 359], 
            ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    plt.legend()
    plt.grid(True)
    if save_fig:
        plt.savefig('images/slope_aspect_curves.png', dpi=300)
    
    return fig1, fig2  # Return both figures


import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def create_3_plots_st(terrain_df):
    # Create a figure with 3 subplots (1 row, 3 columns)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Plot 1: Terrain Slope
    scatter1 = axes[0].scatter(
        terrain_df['longitude'], 
        terrain_df['latitude'], 
        c=terrain_df['slope'],
        cmap='viridis', 
        alpha=0.7,
        vmin=0,
        vmax=90
    )
    axes[0].set_title('Terrain Slope')
    axes[0].set_xlabel('Longitude')
    axes[0].set_ylabel('Latitude')
    cbar1 = fig.colorbar(scatter1, ax=axes[0], label='Slope (degrees)')

    # Plot 2: Terrain Aspect
    scatter2 = axes[1].scatter(
        terrain_df['longitude'], 
        terrain_df['latitude'], 
        c=terrain_df['aspect'],
        cmap='hsv',  # Circular colormap for directional data
        alpha=0.7,
        vmin=0,
        vmax=360
    )
    axes[1].set_title('Terrain Aspect')
    axes[1].set_xlabel('Longitude')
    axes[1].set_ylabel('Latitude')
    cbar2 = fig.colorbar(scatter2, ax=axes[1], label='Aspect (degrees)')
    cbar2.ax.set_yticks([0, 90, 180, 270, 360])
    cbar2.ax.set_yticklabels(['N (0°)', 'E (90°)', 'S (180°)', 'W (270°)', 'N (360°)'])

    # Plot 3: Solar Energy Production
    scatter3 = axes[2].scatter(
        terrain_df['longitude'], 
        terrain_df['latitude'], 
        c=terrain_df['Energy Production (W)'],
        cmap='hot', 
        alpha=0.7
    )
    axes[2].set_title('Solar Energy Production')
    axes[2].set_xlabel('Longitude')
    axes[2].set_ylabel('Latitude')
    cbar3 = fig.colorbar(scatter3, ax=axes[2], label='Energy Production (W)')

    plt.tight_layout()
    st.pyplot(fig)



if __name__ == '__main__':
    min_lat=-26
    max_lat=-25
    min_lon=-71
    max_lon=-70

    terrain_df = get_energy_production_df(min_lat, max_lat, min_lon, max_lon)
    create_3_plots(terrain_df)
    create_information_plots()