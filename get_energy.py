from get_slope_aspect import get_terrain_data
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt

# Get terrain data as a dataframe with columns: latitude, longitude, slope, aspect
data = get_terrain_data(37.7, 37.8, -122.5, -122.4, resolution=30)

def calculate_solar_energy_production(irradiance, slope, aspect, latitude, panel_efficiency=0.2, panel_area=1.0):
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
    optimal_slope = abs(latitude)
    
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
    
    # KEY FIX: For flat terrain (slope near 0), aspect becomes irrelevant
    # Create a weighting that makes aspect factor approach 1.0 as slope approaches 0
    slope_threshold = 5.0  # Below this slope, aspect becomes increasingly irrelevant
    aspect_weight = np.minimum(slope / slope_threshold, 1.0)  # Linear weight from 0 to 1
    
    # Apply slope-dependent weighting to aspect factor
    aspect_factor = 1.0 - aspect_weight + aspect_weight * aspect_factor_base
    
    # Apply both factors to the irradiance
    adjusted_irradiance = irradiance * slope_factor * aspect_factor
    
    # Calculate energy production
    energy_production = adjusted_irradiance * panel_efficiency * panel_area
    
    return energy_production

# Extract slope and aspect from the terrain dataframe
slope = data['slope'].values
aspect = data['aspect'].values

# Use mean latitude from the dataset for optimal tilt calculation
mean_latitude = (data['latitude'].min() + data['latitude'].max()) / 2

# Assuming irradiance data (you might need to get this from another source)
irradiance = 1000  # W/m² (typical peak solar irradiance)

# Calculate energy production with improved model
energy_production = calculate_solar_energy_production(irradiance, slope, aspect, mean_latitude)

# Add energy production to the dataframe
data['Energy Production (W)'] = energy_production

# Create a figure with 3 subplots (1 row, 3 columns)
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Plot 1: Terrain Slope
scatter1 = axes[0].scatter(
    data['longitude'], 
    data['latitude'], 
    c=data['slope'],
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
    data['longitude'], 
    data['latitude'], 
    c=data['aspect'],
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
    data['longitude'], 
    data['latitude'], 
    c=data['Energy Production (W)'],
    cmap='hot', 
    alpha=0.7
)
axes[2].set_title('Solar Energy Production')
axes[2].set_xlabel('Longitude')
axes[2].set_ylabel('Latitude')
cbar3 = plt.colorbar(scatter3, ax=axes[2], label='Energy Production (W)')

plt.tight_layout()
plt.suptitle('Terrain Analysis and Solar Energy Production Potential', fontsize=16, y=1.05)
plt.savefig('terrain_solar_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Create a new visualization showing how flat terrain ignores aspect
plt.figure(figsize=(12, 8))

# Create a grid of slope and aspect values
slopes = np.linspace(0, 45, 10)  # Different slopes from flat to 45 degrees
aspects = np.linspace(0, 359, 36)  # Different aspects all around
slope_grid, aspect_grid = np.meshgrid(slopes, aspects)

# Calculate energy for each combination
energy_grid = np.zeros_like(slope_grid)
for i in range(len(aspects)):
    for j in range(len(slopes)):
        energy_grid[i, j] = calculate_solar_energy_production(
            1000, slopes[j], aspects[i], mean_latitude
        )

# Convert to relative values (percentage of maximum)
energy_rel = energy_grid / np.max(energy_grid) * 100

# Create heatmap
plt.figure(figsize=(12, 10))
im = plt.imshow(energy_rel, origin='lower', aspect='auto', cmap='hot',
               extent=[0, 45, 0, 360])
plt.colorbar(im, label='Relative Energy Potential (%)')
plt.xlabel('Slope (degrees)')
plt.ylabel('Aspect (degrees)')
plt.title('Solar Energy Potential by Slope and Aspect')
plt.yticks([0, 45, 90, 135, 180, 225, 270, 315, 360], 
           ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
plt.grid(False)
plt.savefig('slope_aspect_energy_matrix.png', dpi=300)
plt.show()

# Also plot energy vs aspect for different slopes to show the effect
plt.figure(figsize=(10, 6))

selected_slopes = [0, 5, 15, 30]
for slp in selected_slopes:
    # Find the closest index in our slopes array
    slp_idx = np.abs(slopes - slp).argmin()
    energy_curve = energy_rel[:, slp_idx]
    plt.plot(aspects, energy_curve, label=f'Slope = {slp}°')

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
plt.savefig('slope_aspect_curves.png', dpi=300)
plt.show()