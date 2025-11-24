# Representative Residential Load Profiles for Australia
# 
# These are SYNTHETIC hourly load patterns based on general consumption trends
# identified in Australian residential electricity research.
#
# Based on published research on Australian residential electricity consumption:
# - CSIRO household energy monitoring studies
# - Australian Energy Market Operator (AEMO) load profile data
# - General research findings: Peak consumption 5-9pm, morning peak 6-9am,
#   seasonal variations (Winter/Summer higher than Spring/Autumn)
#
# Note: These profiles are approximations for demonstration purposes.
# Actual household consumption varies based on:
# - Number of occupants
# - Appliance ownership (AC, pool pumps, EVs)
# - Climate/location
# - Occupancy patterns (work from home, etc.)
#
# Weights represent the fraction of daily consumption occurring in each hour (0-23)

REPRESENTATIVE_PROFILES = {
    'Summer': [
        0.025, 0.020, 0.020, 0.020, 0.020, 0.025, # 0-5 (Night/Early Morning)
        0.035, 0.045, 0.040, 0.035, 0.035, 0.035, # 6-11 (Morning - Low peak)
        0.040, 0.045, 0.050, 0.055, 0.065, 0.075, # 12-17 (Afternoon - AC ramp up)
        0.085, 0.080, 0.070, 0.060, 0.045, 0.035  # 18-23 (Evening - Peak Cooling/Cooking)
    ],
    'Winter': [
        0.020, 0.015, 0.015, 0.015, 0.020, 0.030, # 0-5 (Night)
        0.055, 0.075, 0.065, 0.045, 0.040, 0.035, # 6-11 (Morning Peak - Heating/Showers)
        0.035, 0.035, 0.035, 0.040, 0.055, 0.090, # 12-17 (Afternoon - Early Heating)
        0.100, 0.090, 0.075, 0.060, 0.040, 0.025  # 18-23 (Evening Peak - Heating/Cooking)
    ],
    'Shoulder': [ # Autumn/Spring
        0.020, 0.015, 0.015, 0.015, 0.020, 0.025, # 0-5
        0.045, 0.065, 0.050, 0.040, 0.035, 0.035, # 6-11 (Morning Peak)
        0.035, 0.035, 0.035, 0.040, 0.050, 0.080, # 12-17
        0.095, 0.085, 0.070, 0.055, 0.040, 0.030  # 18-23 (Evening Peak)
    ]
}

def get_profile(season):
    """Returns the hourly weights for a given season."""
    if season in ['Autumn', 'Spring']:
        return REPRESENTATIVE_PROFILES['Shoulder']
    return REPRESENTATIVE_PROFILES.get(season, REPRESENTATIVE_PROFILES['Shoulder'])
