
import numpy as np

# Constants
lat = -32.0
day = 172 # Winter
hour = 12 # Noon

# Geometry
declination = 23.45 * np.sin(2 * np.pi / 365 * (day - 81))
# Winter solstice approx declination is +23.45
declination = 23.45 # Force winter solstice
lat_rad = np.radians(lat)
dec_rad = np.radians(declination)

# Noon Elevation
# sin(beta) = cos(lat)cos(dec)cos(0) + sin(lat)sin(dec)
sin_beta = np.cos(lat_rad) * np.cos(dec_rad) * 1 + np.sin(lat_rad) * np.sin(dec_rad)
beta_rad = np.arcsin(sin_beta)
beta_deg = np.degrees(beta_rad)
print(f"Beta: {beta_deg:.2f}")

# 1-Axis Horizontal (Noon)
# Omega = 0 -> Rho = 0
# n_x = 0, n_y = 0, n_z = 1
# Sigma = arccos(1) = 0 (Flat)
sigma_h = 0
# Incidence: cos(theta) = sin(beta) * cos(0) + ... = sin(beta)
cos_theta_h = np.sin(beta_rad)
print(f"1-Axis Horiz CosTheta: {cos_theta_h:.4f}")

# 2-Axis (Noon)
# Points at sun -> CosTheta = 1
cos_theta_2 = 1.0
print(f"2-Axis CosTheta: {cos_theta_2:.4f}")

print(f"Ratio: {cos_theta_h/cos_theta_2:.4f}")

# Cooling Benefit Check
# Assume Ic = 1000 W/m2 (Summer)
Ic = 1000
T_amb = 25
NOCT = 45
S_kW = Ic / 1000
T_cell = T_amb + (NOCT - 20) / 0.8 * S_kW
print(f"Summer T_cell: {T_cell:.2f}")
P_ref = 1000 * 0.14
alpha = -0.0045
P_out = P_ref * (1 + alpha * (T_cell - 25))
benefit = P_ref - P_out
print(f"Summer Benefit: {benefit:.2f} ({benefit/P_out*100:.1f}%)")

# Winter Check
# Assume Ic = 600 W/m2 (Winter Noon)
Ic = 600
T_amb = 11
S_kW = Ic / 1000
T_cell = T_amb + (NOCT - 20) / 0.8 * S_kW
print(f"Winter T_cell: {T_cell:.2f}")
P_ref = 600 * 0.14
P_out = P_ref * (1 + alpha * (T_cell - 25))
benefit = P_ref - P_out
print(f"Winter Benefit: {benefit:.2f} ({benefit/P_out*100:.1f}%)")
