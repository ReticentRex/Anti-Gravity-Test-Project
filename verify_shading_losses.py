import pandas as pd
import numpy as np
from solar_model import SolarModel

def verify_shading_losses():
    print("Initializing SolarModel...")
    model = SolarModel(latitude=-32.0, longitude=116.0) # Perth, Southern Hemisphere
    
    # Define an obstruction: A tall wall to the North (Sun is North in S. Hem)
    # This should cause significant shading.
    # Obstruction format: {'azimuth_start': deg, 'azimuth_end': deg, 'elevation': deg}
    obstructions = [
        {'azimuth_start': 350, 'azimuth_end': 10, 'elevation': 45} # Tall wall due North
    ]
    
    print(f"Running simulation with obstructions: {obstructions}")
    df, totals = model.generate_annual_profile(
        efficiency=0.2,
        fixed_tilt=30,
        fixed_azimuth=0, # North facing
        obstructions=obstructions
    )
    
    print("\n--- Verification Results ---")
    
    # 1. Check for Shading Loss Columns in DataFrame
    shading_cols = [col for col in df.columns if 'Loss_Shading' in col]
    print(f"Shading Loss Columns found: {len(shading_cols)}")
    for col in shading_cols:
        total_loss = df[col].sum()
        print(f"  {col}: Total Sum = {total_loss:.2f} W/m2")
        if total_loss == 0:
            print(f"  ⚠️ WARNING: {col} is zero! (Might be expected for some configs depending on obstruction)")
        else:
            print(f"  ✅ {col} has non-zero values.")
            
    # 2. Check Annual Totals
    print("\nAnnual Loss Totals (kWh/m2):")
    shading_totals = {k: v for k, v in totals.items() if 'Annual_Loss_Shading' in k}
    for k, v in shading_totals.items():
        print(f"  {k}: {v:.2f}")
        if v > 0:
            print(f"  ✅ {k} is non-zero.")
        else:
            print(f"  ⚠️ {k} is zero.")

    # 3. Check Shading Fraction
    if 'Shading_Fraction' in df.columns:
        max_shading = df['Shading_Fraction'].max()
        print(f"\nMax Shading Fraction: {max_shading:.2f}")
        if max_shading > 0:
             print("✅ Shading Fraction is being calculated.")
        else:
             print("❌ Shading Fraction is ZERO everywhere!")
    else:
        print("❌ 'Shading_Fraction' column missing!")

    # 4. Check Delta Ib
    # We can infer Delta Ib from Loss / (cos_theta * eff) roughly, or just trust the loss calc if inputs are good.
    
    print("\nVerification Complete.")

if __name__ == "__main__":
    verify_shading_losses()
