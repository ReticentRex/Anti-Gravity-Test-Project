# Tracking Algorithms - Solar Collector Orientations

**Purpose:** Systematic explanation of all tracking algorithms implemented in `solar_model.py`.  
**Source:** Implementation in `generate_annual_profile()` lines 579-683

Each tracking mode determines how the panel's **tilt angle (σ)** and **azimuth (φc)** change throughout the day to track the sun.

---

## Table of Contents

1. [Horizontal (Fixed Flat)](#1-horizontal-fixed-flat)
2. [1-Axis Azimuth Tracking](#2-1-axis-azimuth-tracking)
3. [1-Axis Elevation Tracking](#3-1-axis-elevation-tracking)
4. [2-Axis Tracking (Ideal)](#4-2-axis-tracking-ideal)
5. [1-Axis Polar Tracking](#5-1-axis-polar-tracking)
6. [1-Axis Horizontal Tracking](#6-1-axis-horizontal-tracking)
7. [Fixed Custom Orientation](#7-fixed-custom-orientation)
8. [Fixed East-West (Bifacial)](#8-fixed-east-west-bifacial)
9. [Fixed North-South (Bifacial)](#9-fixed-north-south-bifacial)

---

## 1. Horizontal (Fixed Flat)

![Horizontal Panel](Collector%20Images/horizontal_panel_schematic_1763815355294.png)

### Concept
Panel lies flat on the ground, never moves. Receives maximum diffuse irradiance but poor beam component except near solar noon.

### Panel Orientation
- **Tilt (σ):** `0°` (horizontal)
- **Azimuth (φc):** `0°` (arbitrary, doesn't matter)

### Implementation
```python
Ic_horiz, cos_theta_horiz = self.calculate_incident_irradiance(beta, phi_s, 0, 0, Ib, C)
```

### Angle of Incidence
From Eq 8 with σ=0°:
```
cos(θ) = sin(β)
```
The AOI equals the complement of solar elevation. At solar noon in summer, θ is small (good). At low sun angles, θ is large (poor).

### Performance Characteristics
- ✅ Simple, no moving parts
- ✅ Maximum diffuse collection
- ✅ No shadowing between rows
- ❌ Poor beam capture except near noon
- ❌ Worst performance at high latitudes

---

## 2. 1-Axis Azimuth Tracking

![1-Axis Azimuth Tracker](Collector%20Images/one_axis_azimuth_schematic_1763815278060.png)

### Concept
Panel is tilted at a **fixed angle** (typically equal to latitude or optimal tilt) and **rotates azimuthally** to follow the sun's east-west movement throughout the day.

### Panel Orientation
- **Tilt (σ):** `Fixed` (optimal_tilt, typically ~latitude)
- **Azimuth (φc):** `φs` (matches sun's azimuth)

### Implementation
```python
sigma_az_track = tilt_1axis_az  # Fixed tilt (e.g., 32° for Perth)
phi_c_az_track = phi_s          # Azimuth follows sun
Ic_1axis_az, cos_theta_1axis_az = self.calculate_incident_irradiance(
    beta, phi_s, sigma_az_track, phi_c_az_track, Ib, C
)
```

### Angle of Incidence
From Eq 8 with φc = φs:
```
cos(θ) = cos(β)·cos(0)·sin(σ) + sin(β)·cos(σ)
       = sin(β)·cos(σ)
```
Since panel always faces the sun azimuthally, the azimuth term cancels, leaving only elevation mismatch.

### Performance Characteristics
- ✅ **Best overall performance** among single-axis trackers
- ✅ Good compromise between performance and complexity
- ✅ One motor, simpler than 2-axis
- ✅ Tilt can be optimized for seasonal performance
- ❌ Some elevation angle mismatch remains

---

## 3. 1-Axis Elevation Tracking

![1-Axis Elevation Tracker](Collector%20Images/one_axis_elevation_schematic_1763815294214.png)

### Concept
Panel's **azimuth is fixed** (facing equator in respective hemisphere) and **tilt adjusts** to be perpendicular to sun's rays based on elevation.

### Panel Orientation
- **Tilt (σ):** `90° - β` (complement of sun elevation)
- **Azimuth (φc):** 
  - Between tropics: Switches based on declination
  - Outside tropics: Fixed toward equator
    - Southern Hemisphere: `0°` (North)
    - Northern Hemisphere: `180°` (South)

### Implementation
```python
# Determine panel azimuth
if abs(self.latitude) >= 23.45:
    phi_c_el_track = 0 if self.latitude < 0 else 180
elif abs(self.latitude) < 0.1:
    phi_c_el_track = 0
else:
    # Between tropics: switch based on declination
    if self.latitude < 0:
        if delta > 0 and abs(delta) > abs(self.latitude):
            phi_c_el_track = 0  # Sun more north than latitude
        else:
            phi_c_el_track = 180  # Sun south of latitude
    # ... (similar logic for N. Hemisphere)

sigma_el_track = 90 - beta  # Tilt = complement of elevation
```

### Angle of Incidence
Conceptually, the panel tries to be perpendicular to sun's elevation, but azimuth is fixed. AOI depends on azimuth mismatch:
```
cos(θ) = cos(β)·cos(φs - φc)·sin(90°-β) + sin(β)·cos(90°-β)
       = cos(β)·cos(φs - φc)·cos(β) + sin(β)·sin(β)
       = cos²(β)·cos(φs - φc) + sin²(β)
```

### Performance Characteristics
- ✅ Tracks elevation well
- ✅ One motor
- ❌ Azimuth mismatch causes losses, especially early morning/late afternoon
- ❌ Generally worse than 1-axis azimuth tracking

---

## 4. 2-Axis Tracking (Ideal)

![2-Axis Tracker](Collector%20Images/two_axis_tracking_schematic_1763815319309.png)

### Concept
Panel points **directly at the sun** at all times by adjusting both azimuth and elevation/tilt. This is the **ideal maximum performance** baseline.

### Panel Orientation
- **Tilt (σ):** `90° - β` (perpendicular to sun elevation)
- **Azimuth (φc):** `φs` (matches sun azimuth)

### Implementation
```python
sigma_2axis = 90.0 - beta  # Panel perpendicular to sun
phi_c_2axis = phi_s        # Panel faces sun
Ic_2axis, cos_theta_2axis = self.calculate_incident_irradiance(
    beta, phi_s, sigma_2axis, phi_c_2axis, Ib, C
)
```

### Angle of Incidence
From Eq 8 with σ = 90°-β and φc = φs:
```
cos(θ) = cos(β)·cos(0)·sin(90°-β) + sin(β)·cos(90°-β)
       = cos(β)·cos(β) + sin(β)·sin(β)
       = cos²(β) + sin²(β)
       = 1
```
**Perfect alignment:** θ = 0° always!

### Performance Characteristics
- ✅ **Maximum possible beam capture**
- ✅ AOI always 0°, no cosine losses
- ✅ Benchmark for comparison
- ❌ Two motors required
- ❌ More complex mechanical design
- ❌ Slightly reduced diffuse/reflected (due to vertical-ish orientation)

---

## 5. 1-Axis Polar Tracking

![1-Axis Polar Tracker](Collector%20Images/polar_axis_schematic_v4.png)

### Concept
The rotation axis is **tilted at the latitude angle** and points toward the **celestial pole** (like Earth's axis). Panel rotates about this tilted axis following the **hour angle**. This mimics Earth's rotation, keeping the panel perpendicular to the sun's rays.

### Axis Definition
- **Axis Tilt:** Equal to latitude (e.g., 32° for Perth)
- **Axis Azimuth:** 
  - Southern Hemisphere: `180°` (points South toward Antarctic pole)
  - Northern Hemisphere: `0°` (points North toward Arctic pole)

### Rotation Angle
- **ρ:** Equal to hour angle `H`
- Rotates by 15°/hour throughout the day

### Mathematics

**Axis vector k:**
```python
k_x = cos(axis_tilt) · sin(axis_azimuth)
k_y = cos(axis_tilt) · cos(axis_azimuth)
k_z = sin(axis_tilt)
```

**Initial panel normal n₀ (at solar noon):**
```python
n0_tilt = π/2 - axis_tilt  # Perpendicular to axis
n0_x = cos(n0_tilt) · sin(panel_azimuth_noon)
n0_y = cos(n0_tilt) · cos(panel_azimuth_noon)
n0_z = sin(n0_tilt)
```

**Rotation about axis by hour angle:**

Using Rodrigues' rotation formula (simplified because rotation is about a specific axis):
```python
rho_rad = omega_rad  # Rotation angle = hour angle
v_cross_x = k_y · n0_z - k_z · n0_y  # Cross product component

# Rotated normal vector
n_rot_x = v_cross_x · sin(rho_rad)
n_rot_y = n0_y · cos(rho_rad)
n_rot_z = n0_z · cos(rho_rad)
```

**Extract panel orientation:**
```python
sigma_polar = arccos(n_rot_z)           # Tilt from vertical component
phi_c_polar = arctan2(n_rot_x, n_rot_y) # Azimuth from x,y components
```

### Implementation
```python
# Define axis (tilted at latitude)
axis_tilt_polar = tilt_1axis_polar
axis_azimuth_polar = 180 if self.latitude < 0 else 0

# Axis unit vector
k_x = cos(tilt_rad) * sin(az_rad)
k_y = cos(tilt_rad) * cos(az_rad)
k_z = sin(tilt_rad)

# Initial panel normal (at noon, perpendicular to axis)
n0_tilt_rad = π/2 - tilt_rad
n0_x = cos(n0_tilt_rad) * sin(n0_az_rad)
n0_y = cos(n0_tilt_rad) * cos(n0_az_rad)
n0_z = sin(n0_tilt_rad)

# Rotate by hour angle
omega_rad = radians(hour_angle)
rho_rad = omega_rad if k_y >= 0 else -omega_rad

v_cross_x = k_y * n0_z - k_z * n0_y
n_rot_x = v_cross_x * sin(rho_rad)
n_rot_y = n0_y * cos(rho_rad)
n_rot_z = n0_z * cos(rho_rad)

# Extract orientation
sigma_polar = degrees(arccos(clip(n_rot_z, -1, 1)))
phi_c_polar = degrees(arctan2(n_rot_x, n_rot_y))
```

### Angle of Incidence
Theoretically near-zero for most of the day because the rotation mimics Earth's movement, keeping panel perpendicular to sun.

### Performance Characteristics
- ✅ Near-perfect tracking most of the day
- ✅ Single rotation axis
- ✅ Smooth continuous motion (15°/hour)
- ✅ Very close to 2-axis performance
- ⚠️ Axis must be precisely aligned to latitude/pole
- ❌ Some losses at equinoxes/solstices due to declination changes

---

## 6. 1-Axis Horizontal Tracking

![1-Axis Horizontal Tracker](Collector%20Images/horizontal_axis_schematic.png)

### Concept
The rotation axis lies **horizontal on the ground** oriented **North-South**. Panel rotates about this horizontal axis, tilting East in the morning and West in the afternoon to follow the sun's daily arc.

### Key Insight
The rotation axis is North-South. To face the morning sun (East), the panel rotates such that its **normal vector points East**.

### Panel Orientation
- **Tilt (σ):** `|Hour Angle|` clamped at 90°
  - 0° at solar noon (flat)
  - Up to 90° at sunrise/sunset
- **Azimuth (φc):** 
  - Morning (H > 0): `+90°` (East) - Normal points East toward sun
  - Afternoon (H < 0): `-90°` (West) - Normal points West toward sun

### Implementation
```python
H_deg = geom['hour_angle']

# Tilt = absolute value of hour angle (clamped at 90°)
sigma_horiz = min(abs(H_deg), 90.0)

# Azimuth of panel normal (opposite to tilt direction)
if H_deg < 0:
    phi_c_horiz = -90.0  # Normal points West (panel tilts East in morning)
else:
    phi_c_horiz = 90.0   # Normal points East (panel tilts West in afternoon)

Ic_1axis_horiz, cos_theta_1axis_horiz = self.calculate_incident_irradiance(
    beta, phi_s, sigma_horiz, phi_c_horiz, Ib, C
)
```

### Angle of Incidence
Panel follows hour angle but doesn't adjust for elevation. Good tracking at low latitudes where sun passes nearly overhead, but misses elevation at higher latitudes.

### Performance Characteristics
- ✅ Simple horizontal axis, easy mounting
- ✅ **Excellent Summer Performance:** At mid-latitudes, sun passes near zenith, matching the "roll" motion perfectly.
- ❌ **Poor Winter Performance:** Sun stays low in North/South. Tracker cannot look North/South (azimuth locked to East/West), causing massive misalignment.
- ❌ **Extreme Seasonality:** "Fair weather friend" - great annual average driven by summer peaks, but unreliable in winter.
- ❌ Generally worse than azimuth or polar tracking for consistent year-round power.

---

## 7. Fixed Custom Orientation

![Fixed Custom](Collector%20Images/fixed_custom_schematic_1763815554067.png)

### Concept
Panel is fixed at a user-specified tilt and azimuth. Typically optimized for a specific use case (e.g., roof mount, seasonal optimization).

### Panel Orientation
- **Tilt (σ):** User-defined (default: optimal_tilt)
- **Azimuth (φc):** User-defined (default: equator-facing)

### Implementation
```python
tilt_fixed = fixed_tilt if fixed_tilt is not None else self.tilt
azimuth_fixed = fixed_azimuth if fixed_azimuth is not None else self.azimuth

Ic_fixed, cos_theta_fixed = self.calculate_incident_irradiance(
    beta, phi_s, tilt_fixed, azimuth_fixed, Ib, C
)
```

### Performance Characteristics
- ✅ No moving parts, maximum simplicity
- ✅ Can be optimized for specific goals
- ✅ Good for building integration
- ❌ Static orientation means suboptimal most of the time
- ❌ Performance varies significantly with season

---

## 8. Fixed East-West (Bifacial)

![East-West Configuration](Collector%20Images/East-West%20Collector%20Configuration%20Schematic.png)

### Concept
Two panels in a **bifacial configuration**: one facing East, one facing West, both at shallow tilt (typically 10°). Averages the output of both sides. Good for **load balancing** throughout the day.

### Panel Orientation
- **Tilt (σ):** `10°` (shallow, both sides)
  - **Why 10°?** This is the industry standard "sweet spot":
    1. **Self-Cleaning:** <10° causes water pooling/soiling; ≥10° allows rain to wash away dust.
    2. **Packing Density:** Low tilt minimizes inter-row shading, allowing rows to be placed back-to-back (`/\/\/\`) for maximum land use.
    3. **Wind Load:** Acts less like a sail, reducing structural requirements.
- **Azimuth (φc):** 
  - East panel: `90°`
  - West panel: `270°` or `-90°`

### Implementation
```python
Ic_fixed_E, ct_E = self.calculate_incident_irradiance(beta, phi_s, 10, 90, Ib, C)
Ic_fixed_W, ct_W = self.calculate_incident_irradiance(beta, phi_s, 10, 270, Ib, C)

# Calculate performance for each side
res_fixed_E = self.calculate_pv_performance(Ic_fixed_E, ct_E, T_amb, efficiency)
res_fixed_W = self.calculate_pv_performance(Ic_fixed_W, ct_W, T_amb, efficiency)

# Average the outputs
P_out_EW = (res_fixed_E['P_out'] + res_fixed_W['P_out']) / 2
```

### Performance Characteristics
- ✅ Morning generation (East) + afternoon generation (West)
- ✅ Flatter daily power curve (good for grid)
- ✅ Reduced peak demand on inverters
- ✅ Good space utilization (both sides productive)
- ⚠️ Each side individually poor (facing wrong way half the day)
- ❌ Lower total energy than optimal fixed tilt

---

## 9. Fixed North-South (Bifacial)

![North-South Configuration](Collector%20Images/North-South%20Collector%20Configuration%20Schematic.png)

### Concept
Two panels: one facing North, one facing South, both at shallow tilt. Hemisphere-dependent performance.

### Panel Orientation
- **Tilt (σ):** `10°`
- **Azimuth (φc):**
  - North panel: `0°`
  - South panel: `180°`

### Implementation
```python
Ic_fixed_N, ct_N = self.calculate_incident_irradiance(beta, phi_s, 10, 0, Ib, C)
Ic_fixed_S, ct_S = self.calculate_incident_irradiance(beta, phi_s, 10, 180, Ib, C)

res_fixed_N = self.calculate_pv_performance(Ic_fixed_N, ct_N, T_amb, efficiency)
res_fixed_S = self.calculate_pv_performance(Ic_fixed_S, ct_S, T_amb, efficiency)

P_out_NS = (res_fixed_N['P_out'] + res_fixed_S['P_out']) / 2
```

### Performance Characteristics
In **Southern Hemisphere** (negative latitude):
- ✅ North panel performs well (faces sun)
- ❌ South panel performs poorly (faces away)
- Result: One good side, one bad side, average is mediocre

In **Northern Hemisphere** (positive latitude):
- ✅ South panel performs well
- ❌ North panel performs poorly
- Same mediocre average

**Generally worse than E-W configuration** because one side is always very poor (rather than both sides being moderate).

### Tropical/Equatorial Nuance
While poor at mid-latitudes, this configuration is **highly effective in the tropics (between ±23.45°)**.
- At the **Equator**, the sun spends 6 months in the North sky and 6 months in the South sky.
- The "active" face flips seasonally, utilizing both sides of the bifacial array effectively throughout the year.
- In contrast, at mid-latitudes (e.g., Perth -32°), the sun is *always* in the North sky at noon, rendering the South-facing panel permanently suboptimal.

---

## Performance Ranking (Typical)

At **mid-latitudes** (e.g., -32°S Perth):

1. **2-Axis**: 100% (baseline, ideal)
2. **1-Axis Polar**: ~98-99% (excellent)
3. **1-Axis Azimuth**: ~95-97% (very good)
4. **1-Axis Elevation**: ~90-93%
5. **1-Axis Horizontal**: ~88-92%
6. **Fixed Optimal**: ~85-90%
7. **Fixed E-W**: ~75-80%
8. **Horizontal**: ~70-75%
9. **Fixed N-S**: ~65-70%

*Rankings vary with latitude, season, and local climate*

---

## Summary Table

| Tracker Type | Motors | Tilt (σ) | Azimuth (φc) | Complexity | Performance |
|--------------|--------|----------|--------------|------------|-------------|
| Horizontal | 0 | 0° | 0° | Minimal | Poor |
| Fixed Custom | 0 | Fixed | Fixed | Minimal | Moderate |
| Fixed E-W | 0 | 10° | 90°/270° | Minimal | Moderate |
| Fixed N-S | 0 | 10° | 0°/180° | Minimal | Poor-Moderate |
| 1-Axis Horizontal | 1 | \|H\| | ±90° | Low | Moderate-Good |
| 1-Axis Elevation | 1 | 90°-β | 0° or 180° | Low | Good |
| 1-Axis Azimuth | 1 | Fixed | φs | Low | Very Good |
| 1-Axis Polar | 1 | Varies | Varies | Medium | Excellent |
| 2-Axis | 2 | 90°-β | φs | High | Ideal |

---

**Document Status:** Complete tracking algorithm documentation  
**Last Updated:** 2025-11-29  
**Code Reference:** `solar_model.py` lines 579-723
