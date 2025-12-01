
import numpy as np
from solar_model import SolarModel

model = SolarModel(latitude=-32.0, longitude=115.0)

print("--- Winter Noon Check (Day 172, Hour 12) ---")
geom = model.calculate_geometry(172, 12)
beta = geom['elevation']
phi_s = geom['azimuth']
print(f"Sun: Beta={beta:.2f}, Phi_s={phi_s:.2f}")

# 1-Axis Horizontal
omega = geom['hour_angle']
rho = np.clip(np.radians(omega), -np.pi/2, np.pi/2)
n_x = 1 * np.sin(rho)
n_y = 0
n_z = 1 * np.cos(rho)
sigma_h = np.degrees(np.arccos(n_z))
phi_c_h = np.degrees(np.arctan2(n_x, n_y))
print(f"1-Axis Horiz: Sigma={sigma_h:.2f}, Phi_c={phi_c_h:.2f}")

irr = model.calculate_irradiance(172, beta)
Ib = irr['dni']
C = irr['diffuse_factor']
Ic_h, cos_h = model.calculate_incident_irradiance(beta, phi_s, sigma_h, phi_c_h, Ib, C)
print(f"1-Axis Horiz: Ic={Ic_h:.2f}, CosTheta={cos_h:.4f}")

# 2-Axis
sigma_2 = 90 - beta
phi_c_2 = phi_s
Ic_2, cos_2 = model.calculate_incident_irradiance(beta, phi_s, sigma_2, phi_c_2, Ib, C)
print(f"2-Axis: Ic={Ic_2:.2f}, CosTheta={cos_2:.4f}")

print(f"Ratio 1-Axis/2-Axis: {Ic_h/Ic_2:.2f}")

print("\n--- Cooling Benefit Check ---")
# Simulate T_cell calculation
T_amb = 11.0
S_kW = Ic_h / 1000.0
T_cell = T_amb + (45 - 20) / 0.8 * S_kW
print(f"T_amb={T_amb}, S_kW={S_kW:.2f} -> T_cell={T_cell:.2f}")

# Calculate Power
eff = 0.14
P_ref = eff * Ic_h # approx IAM=1
alpha = -0.0045
P_out = P_ref * (1 + alpha * (T_cell - 25))
P_cool = P_ref
Benefit = P_cool - P_out
print(f"P_ref (Cooled)={P_cool:.2f}, P_out (Actual)={P_out:.2f}")
print(f"Benefit={Benefit:.2f} ({Benefit/P_out*100:.1f}%)")
