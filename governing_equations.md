# Governing Equations - Solar Model Implementation

**Purpose:** Document all governing equations used in `solar_model.py` (excluding tracking algorithms).  
**Source:** Ryan Coble-Neal Thesis - "Identifying the Factors Impacting the Performance of Two-Axis Sun-Tracking Photovoltaic Systems on Mobile Platforms"

---

## 1. Solar Geometry Calculations

These equations determine the Sun's position in the sky for any location and time.

### 1.1 Solar Declination [Eq 1]
**Purpose:** Angle of the sun relative to the equatorial plane throughout the year.

```
δ = 23.45 · sin[360/365 · (n - 81)]
```

**Implementation:** [`calculate_geometry()` lines 103-105]
```python
delta_rad = np.radians(23.45) * np.sin(2 * np.pi / 365 * (day_of_year - 81))
delta_deg = np.degrees(delta_rad)
```

- `δ`: Solar declination (degrees)
- `n`: Day of year (1-365)
- Ranges from -23.45° (winter solstice) to +23.45° (summer solstice)

**Note on Eq 1.1 and 1.2 (Not Implemented):**

The thesis also presents Equations 1.1 and 1.2 for calculating the two days per year when the sun is directly overhead at tropical latitudes:

```
n1, n2 = 81 + (365/360) · sin⁻¹(L/23.45)
```

These equations are described as "useful for sanity checking" azimuth calculations between the tropics. **They are not implemented** in the code because:
- The actual elevation/azimuth calculations (Eq 5, 6, 6.1) already handle all latitudes correctly
- The quadrant check (Eq 6.1) properly determines sun position without pre-calculation
- These are manual verification tools for human understanding, not required for computation

---

### 1.2 Hour Angle [Eq 2]
**Purpose:** Sun's east-west position relative to solar noon.

```
H = 15°/hour × (12 - Solar Time)
```

**Implementation:** [`calculate_geometry()` lines 150-151]
```python
H_deg = 15 * (12 - solar_time_hours)
```

- `H`: Hour angle (degrees)
- Positive before solar noon, negative after
- 15° per hour because Earth rotates 360° in 24 hours

---

### 1.3 Solar Time Conversion [Eq 3, 3.1]
**Purpose:** Convert clock time to solar time accounting for longitude and Earth's elliptical orbit.

**Thesis Equations:**
- **Eq 3 (West of Prime Meridian):** `ST = CT + 4·(Meridian - Longitude) + E`
- **Eq 3.1 (East of Prime Meridian):** `ST = CT + 4·(Longitude - Meridian) + E`

**Implementation:** [`calculate_geometry()` lines 115-116]
```python
# Uses signed longitude convention, so Eq 3.1 works for both East and West
time_correction_min = 4 * (self.longitude - self.local_time_meridian) + E_min
solar_time_hours = hour + time_correction_min / 60
```

**Signed Longitude Convention:**
- East of Prime Meridian: **positive** (e.g., Perth = +115.89°, UTC +8)
- West of Prime Meridian: **negative** (e.g., Boston = -71°, UTC -5)

**Why Eq 3.1 works for both:**
- **Perth example:** longitude=+115.89°, meridian=+120° → (115.89 - 120) = -4.11° → -16.44 min
  - Solar time is **earlier** than clock time ✓
- **Boston example:** longitude=-71°, meridian=-75° → (-71 - (-75)) = +4° → +16 min
  - Solar time is **later** than clock time ✓

With signed longitudes, Eq 3.1 `(Longitude - Meridian)` automatically handles both directions correctly.

**Variables:**
- `ST`: Solar time (hours)
- `CT`: Clock time (hours)  
- `E`: Equation of time (minutes)
- Meridian = UTC offset × 15° (e.g., UTC+8 → 120°E, UTC-5 → -75°W)

---

### 1.4 Equation of Time [Eq 4, 4.1]
**Purpose:** Accounts for Earth's elliptical orbit causing solar day length variation.

```
E = 9.87·sin(2B) - 7.53·cos(B) - 1.5·sin(B)  (minutes)
B = 360/364 · (n - 81)  (degrees)
```

**Implementation:** [`calculate_geometry()` lines 111-121]
```python
B_deg = (360.0 / 364.0) * (day_of_year - 81)
B_rad = np.radians(B_deg)
E_minutes = 9.87 * np.sin(2 * B_rad) - 7.53 * np.cos(B_rad) - 1.5 * np.sin(B_rad)
```

---

### 1.5 Solar Elevation (Altitude) [Eq 5]
**Purpose:** Vertical angle from horizon to sun.

```
sin(β) = cos(L)·cos(δ)·cos(H) + sin(L)·sin(δ)
```

**Implementation:** [`calculate_geometry()` lines 108-109]
```python
sin_beta = np.cos(L_rad) * np.cos(delta_rad) * np.cos(H_rad) + np.sin(L_rad) * np.sin(delta_rad)
beta_deg = np.degrees(np.arcsin(np.clip(sin_beta, -1, 1)))
```

- `β`: Solar elevation (degrees, 0° to 90°)
- `L`: Latitude (positive North, negative South)
- Negative elevation means sun is below horizon

---

### 1.6 Solar Azimuth [Eq 6, 6.1]
**Purpose:** Horizontal angle from North to the sun.

```
sin(φs) = cos(δ)·sin(H) / cos(β)
```

**Check condition [Eq 6.1]:**
```
If cos(H) < tan(δ)/tan(L):
    Adjust φs to account for quadrant (|φs| > 90°)
```

**Implementation:** [`calculate_geometry()` lines 131-183]
```python
sin_phi = np.cos(delta_rad) * np.sin(H_rad) / np.cos(beta_rad)
phi_s_deg = np.degrees(np.arcsin(np.clip(sin_phi, -1, 1)))

# Quadrant check
check_val = np.tan(delta_rad) / np.tan(L_rad)
condition_met = np.cos(H_rad) >= check_val

# Hemisphere-specific logic to determine if |φs| > 90°
```

- `φs`: Solar azimuth (degrees, -180° to +180°)
- 0° = North, +90° = East, -90° = West, ±180° = South

---

## 2. Angle of Incidence (AOI) Calculations

### 2.1 AOI for Horizontal Surface [Eq 7]
**Purpose:** Angle between sun's rays and normal of horizontal panel.

```
θ = 90° - β
or equivalently: cos(θ) = sin(β)
```

**Note:** For horizontal panels, AOI is simply the complement of elevation.

---

### 2.2 AOI for Tilted Surface [Eq 8]
**Purpose:** Angle between sun's rays and normal of tilted/oriented panel.

```
cos(θ) = cos(β)·cos(φs - φc)·sin(Σ) + sin(β)·cos(Σ)
```

**Implementation:** [`calculate_incident_irradiance()` lines 284-289]
```python
cos_theta = np.cos(beta) * np.cos(phi_s - phi_c) * np.sin(sigma) + \
            np.sin(beta) * np.cos(sigma)
cos_theta = max(0, cos_theta)  # Clamp to 0 if sun behind panel
```

- `θ`: Angle of incidence (degrees)
- `β`: Solar elevation
- `φs`: Solar azimuth
- `φc`: Panel azimuth
- `Σ` (sigma): Panel tilt from horizontal (0° = horizontal, 90° = vertical)

**Critical:** This is the fundamental equation linking sun position to panel orientation!

---

## 3. Solar Irradiance Calculations

### 3.1 Apparent Extraterrestrial Flux [Eq 9]
**Purpose:** Solar intensity at top of atmosphere, varies with Earth-Sun distance.

```
A = 1160 + 75·sin[360/365 · (n - 275)]  (W/m²)
```

**Implementation:** [`calculate_irradiance()` lines 220]
```python
A = 1160 + 75 * np.sin(2 * np.pi / 365 * (n - 275))
```

---

### 3.2 Optical Depth [Eq 10]
**Purpose:** Atmospheric attenuation factor varying seasonally.

```
k = 0.174 + 0.035·sin[360/365 · (n - 100)]  (unitless)
```

**Implementation:** [`calculate_irradiance()` lines 223]
```python
k = 0.174 + 0.035 * np.sin(2 * np.pi / 365 * (n - 100))
```

---

### 3.3 Air Mass [Eq 11]
**Purpose:** Amount of atmosphere sunlight must traverse.

```
m = 1 / sin(β)  (unitless)
```

**Implementation:** [`calculate_irradiance()` lines 226-231]
```python
sin_beta = np.sin(beta_rad)
if sin_beta < 0.01:  # Cap for very low angles
    m = 1 / 0.01
else:
    m = 1 / sin_beta
```

- Higher at sunrise/sunset (more atmosphere)
- Minimum at solar noon (less atmosphere)

---

### 3.4 Direct Normal Irradiance (DNI) [Eq 12]
**Purpose:** Direct beam intensity after atmospheric attenuation.

```
IB = A · e^(-k·m)  (W/m²)
```

**Implementation:** [`calculate_irradiance()` lines 235]
```python
Ib = A * np.exp(-k * m)
```

- Measured perpendicular to sun's rays
- This is the strongest irradiance component

---

### 3.5 Sky Diffuse Factor [Eq 15]
**Purpose:** Proportion of diffuse to beam irradiance.

```
C = 0.095 + 0.04·sin[360/365 · (n - 100)]  (unitless)
```

**Implementation:** [`calculate_irradiance()` lines 238]
```python
C = 0.095 + 0.04 * np.sin(2 * np.pi / 365 * (n - 100))
```

---

### 3.6 Diffuse Horizontal Irradiance [Eq 16]
**Purpose:** Diffuse (scattered) light on horizontal surface.

```
IDH = C · IB  (W/m²)
```

**Implementation:** [`calculate_irradiance()` lines 244]
```python
Idh = C * Ib
```

---

### 3.7 Beam Component on Tilted Surface [Eq 14]
**Purpose:** Direct beam on tilted panel.

```
IBC = IB · cos(θ)  (W/m²)
```

**Implementation:** [`calculate_incident_irradiance()` lines 291-292]
```python
Ibc = Ib * cos_theta
```

---

### 3.8 Diffuse Component on Tilted Surface [Eq 17]
**Purpose:** Diffuse irradiance on tilted panel.

```
IDC = C · IB · (1 + cos(Σ)) / 2  (W/m²)
```

**Implementation:** [`calculate_incident_irradiance()` lines 296]
```python
Idc = C * Ib * (1 + np.cos(sigma)) / 2
```

- Assumes isotropic (uniform) sky diffuse
- Horizontal panel (Σ=0°) receives full diffuse
- Vertical panel (Σ=90°) receives half diffuse

---

### 3.9 Reflected Component [Eq 18]
**Purpose:** Ground-reflected irradiance on tilted panel.

```
IRC = ρ · IB · [sin(β) + C] · (1 - cos(Σ)) / 2  (W/m²)
```

**Implementation:** [`calculate_incident_irradiance()` lines 299-300]
```python
Irc = rho * Ib * (np.sin(beta) + C) * (1 - np.cos(sigma)) / 2
```

- `ρ` (rho): Ground reflectance/albedo (0.2 default for grass)
- Zero for horizontal panels (Σ=0°)
- Maximum for vertical panels (Σ=90°)

---

### 3.10 Total Incident Irradiance [Eq 19]
**Purpose:** Sum of all irradiance components.

```
IC = IBC + IDC + IRC  (W/m²)
```

**Implementation:** [`calculate_incident_irradiance()` lines 302-304]
```python
Ic = Ibc + Idc + Irc
return Ic, cos_theta
```

---

## 4. PV Performance Calculations

### 4.1 Angular Loss (Reflection) [Eq 20]
**Purpose:** Irradiance lost to reflection at high angles of incidence.

```
AL(θ) = 1 - [1 - exp(-cos(θ)/αr)] / [1 - exp(-1/αr)]
```

**Where:**
- Incidence Angle Modifier (IAM) = 1 - AL
- Effective Irradiance S = IC · IAM

**Implementation:** [`calculate_pv_performance()` lines 329-338]
```python
ALPHA_R = 0.17  # Angular loss coefficient
if cos_theta <= 0:
    IAM = 0
else:
    numerator = 1 - np.exp(-cos_theta / ALPHA_R)
    denominator = 1 - np.exp(-1 / ALPHA_R)
    IAM = numerator / denominator

S_W_m2 = Ic * IAM
Loss_Angular = Ic - S_W_m2
```

- `αr` = 0.17 for polycrystalline silicon with anti-reflective coating
- Loss increases exponentially for θ > 55°
- For θ = 0° (perfect alignment): AL = 0, IAM = 1 (no loss)
- For θ = 90° (grazing): AL ≈ 1, IAM ≈ 0 (total loss)

---

### 4.2 Cell Temperature [Eq 22]
**Purpose:** Calculate PV cell temperature from ambient and irradiance.

```
Tcell = Tamb + (NOCT - 20°C) / 0.8 kW/m² · S (kW/m²)
```

**Implementation:** [`calculate_pv_performance()` lines 343-345]
```python
NOCT = 45.0  # Nominal Operating Cell Temperature (°C)
S_kW_m2 = S_W_m2 / 1000.0
T_cell = T_amb + (NOCT - 20) / 0.8 * S_kW_m2
```

- NOCT = 45°C (typical for standard modules)
- NOCT test conditions: 800 W/m², 20°C ambient, 1 m/s wind
- Cell temp rises ~31°C above ambient per kW/m² of irradiance

---

### 4.3 Temperature-Dependent Power [Eq 25 concept]
**Purpose:** Power decreases with temperature above 25°C (STC).

```
Pout = Pref(25°C) · [1 + αp·(Tcell - 25°C)]
```

**Implementation:** [`calculate_pv_performance()` lines 347-357]
```python
ALPHA_P = -0.0045  # Power temp coefficient (-0.45%/°C)
EFF_STC = efficiency  # Efficiency at STC (25°C, 1000 W/m²)

# Reference power at 25°C (after angular loss)
P_ref_25C = EFF_STC * S_W_m2

# Actual power at cell temperature
temp_factor = 1 + ALPHA_P * (T_cell - 25)
P_out = P_ref_25C * temp_factor

# Thermal loss
Loss_Thermal = P_ref_25C - P_out
```

- `αp` = -0.0045 per °C (typical for silicon)
- Power decreases ~0.45% per degree above 25°C
- Power increases slightly below 25°C

---

### 4.4 Ambient Temperature Model
**Purpose:** Synthetic ambient temperature varying with season and time of day.

**Implementation:** [`calculate_ambient_temperature()` lines 45-87]
```python
# Annual cycle
day_angle = 2 * np.pi * (day_of_year - 1) / 365
annual_amplitude = base_swing * (1 + 0.3 * abs(self.latitude) / 90)
T_annual = avg_temp + annual_amplitude * np.cos(day_angle - np.pi)

# Diurnal cycle
hour_angle = 2 * np.pi * (hour - 6) / 24  # Minimum at 6am
diurnal_amplitude = base_daily_swing * (1 + annual_amplitude * np.cos(day_angle - np.pi) / 15)
T_diurnal = diurnal_amplitude * np.cos(hour_angle - np.pi)

# Combined
T_amb = T_annual + T_diurnal
```

**Parameters (scales with latitude):**
- Base annual swing: 8°C
- Base daily swing: 5°C
- Increases with distance from equator
- Coldest at 6am, warmest around 2-3pm

---

## 5. Summary of Data Flow

```
[Time & Location]
    ↓
[Solar Geometry: δ, H, β, φs] (Eq 1-6)
    ↓
[Panel Orientation: Σ, φc] + [Sun Position]
    ↓
[Angle of Incidence: θ] (Eq 8)
    ↓
[Atmospheric Conditions: A, k, m] (Eq 9-11)
    ↓
[Direct Normal Irradiance: IB] (Eq 12)
    ↓
[Components: IBC, IDC, IRC] (Eq 14, 17, 18)
    ↓
[Total Incident: IC] (Eq 19)
    ↓
[Angular Loss: IAM] (Eq 20)
    ↓
[Effective Irradiance: S = IC · IAM]
    ↓
[Cell Temperature: Tcell] (Eq 22)
    ↓
[Power Output: Pout] (Eq 25 concept)
```

---

## 6. Key Implementation Notes

1. **Coordinate Systems:**
   - Latitude: Positive North, Negative South
   - Azimuth: 0° = North, ±90° = East/West, ±180° = South
   - Tilt (Σ): 0° = horizontal, 90° = vertical
   - All angles internally converted to radians for trig functions

2. **Sign Conventions:**
   - Hour angle: Positive before noon, negative after
   - This affects tracking algorithm implementations

3. **Numerical Stability:**
   - `arcsin/arccos` inputs clamped to [-1, 1]
   - Air mass capped for very low elevations (β < 0.5°)
   - cos(θ) clamped to [0, ∞) (sun can't be behind panel)

4. **Hemisphere Handling:**
   - Azimuth quadrant check logic differs for N/S hemispheres
   - Panel faces North in S. Hemisphere (φc=0°), South in N. Hemisphere (φc=180°)

---

## 7. Equations NOT Used (Noted in Thesis)

- **Eq 13:** Beam horizontal irradiance `IBH = IB·sin(β)` - calculated but not separately used
- **Eq 21:** Shunt resistance power dissipation - not modeled (assumes no shading)
- **Eq 23-24:** Isc, Voc temperature adjustments - simplified to overall power coefficient
- **Eq 26:** Module efficiency - inverted (efficiency is input parameter, power is output)
- **Eq 27-32:** Locomotive forces/power - not applicable to this analysis

---

**Document Status:** Complete for all non-tracking calculations  
**Last Updated:** 2025-11-29  
**Code Reference:** `solar_model.py`
