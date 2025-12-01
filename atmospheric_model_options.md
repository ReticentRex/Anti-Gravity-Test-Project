# Atmospheric Model Improvements for Extreme Latitudes

**Context:** At latitude -80° on Day 355, the model predicts 20.12 kWh/m² daily DNI, which seems high compared to typical values (7-8 kWh/m² in deserts). The current model uses equations calibrated for mid-latitudes.

---

## Option 2: Latitude-Dependent Optical Depth

### Current Implementation

**Equation 10 (Optical Depth):**
```
k = 0.174 + 0.035·sin[360/365 · (n - 100)]
```

This varies **seasonally** but is the same for all latitudes.

### What is Optical Depth (k)?

Optical depth represents the **total atmospheric opacity** - how much the atmosphere absorbs and scatters sunlight. It depends on:

1. **Water vapor content** - absorbs infrared and near-infrared
2. **Aerosols** - dust, pollution, sea salt
3. **Air density** - decreases with altitude
4. **Ozone** - absorbs UV light

### Why Make It Latitude-Dependent?

**Polar regions (60°-90°):**
- Much drier air (less water vapor)
- Cleaner atmosphere (less aerosol pollution)
- **BUT:** Longer path length through atmosphere at low sun angles
- **NET EFFECT:** Lower k values (higher transmission) may be appropriate

**Tropical regions (0°-23°):**
- High humidity (more water vapor)
- More aerosols from vegetation, industry
- **NET EFFECT:** Higher k values (lower transmission)

**Mid-latitudes (23°-60°):**
- Moderate humidity
- Variable aerosol content
- Current model likely calibrated for this region

### Proposed Formula

```python
# Base optical depth (seasonal variation)
k_base = 0.174 + 0.035 * sin(2π/365 · (day - 100))

# Latitude adjustment factor
lat_abs = abs(latitude)

if lat_abs < 23.45:  # Tropics
    k_factor = 1.2  # 20% more opaque
elif lat_abs < 60:  # Temperate
    k_factor = 1.0  # Baseline (current calibration)
else:  # Polar (60-90°)
    k_factor = 0.85  # 15% clearer atmosphere

k = k_base * k_factor
```

### Impact on DNI

At -80° latitude, Day 355, Elevation 13.4°:

**Current:**
- k = 0.1408
- DNI = 673 W/m²

**With k_factor = 0.85:**
- k = 0.1408 × 0.85 = 0.1197
- DNI = 1234 × e^(-0.1197 × 4.3) = **770 W/m²** (+14%)

**With k_factor = 1.15 (opposite direction):**
- k = 0.1408 × 1.15 = 0.1619
- DNI = 1234 × e^(-0.1619 × 4.3) = **592 W/m²** (-12%)

### Pros
- ✅ Simple to implement (one parameter change)
- ✅ Physically motivated (polar air is cleaner/drier)
- ✅ Easy to tune by adjusting k_factor

### Cons
- ❌ Empirical adjustment (not based on first principles)
- ❌ May still not capture very low angle behavior accurately
- ❌ Affects all elevations equally (doesn't specifically fix low-angle issue)

---

## Option 3: Kasten-Young Air Mass Formula

### Current Implementation

**Equation 11 (Simple Air Mass):**
```
m = 1 / sin(β)
```

This is a geometric approximation assuming:
- Flat Earth
- Uniform atmosphere
- Straight-line path

### What is Air Mass (m)?

Air mass represents **how much atmosphere sunlight travels through** relative to the vertical path:
- m = 1: Sun directly overhead (shortest path)
- m = 2: Sun at 30° elevation (2x more atmosphere)
- m = 4.3: Sun at 13.4° elevation (4.3x more atmosphere)

### Why the Simple Formula Fails at Low Angles

At low elevations (< 20°):
1. **Earth curvature matters** - atmosphere curves with Earth
2. **Atmospheric refraction** - light bends as it enters denser layers
3. **Non-uniform density** - atmosphere gets thinner with altitude

The simple formula `1/sin(β)` assumes a flat Earth with uniform atmosphere.

### Kasten-Young Formula (1989)

Empirically derived from atmospheric measurements:

```
m = 1 / (sin(β) + 0.50572 · (β + 6.07995)^(-1.6364))
```

Where β is in **degrees** (not radians for the second term).

**Key improvement:** Better accuracy at low sun angles by accounting for atmospheric curvature.

### Comparison: Simple vs Kasten-Young

| Elevation | Simple m | Kasten-Young m | Difference |
|-----------|----------|----------------|------------|
| 90° | 1.00 | 1.00 | 0% |
| 45° | 1.41 | 1.41 | 0% |
| 30° | 2.00 | 2.00 | 0% |
| 20° | 2.92 | 3.07 | +5% |
| 15° | 3.86 | 4.09 | +6% |
| 10° | 5.76 | 6.18 | +7% |
| 5° | 11.47 | 12.44 | +8% |
| 2° | 28.65 | 31.31 | +9% |

**At 13.4° elevation (our case):**
- Simple: m = 4.30
- Kasten-Young: m ≈ 4.56 (+6%)

### Impact on DNI

At -80° latitude, Day 355, Elevation 13.4°:

**Current (Simple):**
- m = 4.30
- DNI = 1234 × e^(-0.1408 × 4.30) = **673 W/m²**

**With Kasten-Young:**
- m = 4.56
- DNI = 1234 × e^(-0.1408 × 4.56) = **640 W/m²** (-5%)

### Pros
- ✅ Physically accurate (based on atmospheric measurements)
- ✅ Well-established in solar engineering literature
- ✅ Specifically improves low-angle accuracy
- ✅ No arbitrary parameters to tune

### Cons
- ❌ Slightly more complex calculation
- ❌ Only ~5-10% difference at typical low angles
- ❌ May not fully solve the "20 kWh/m² seems high" issue

---

## Combined Approach

You could implement **both** options:

```python
# Latitude-dependent optical depth
k_base = 0.174 + 0.035 * sin(2π/365 · (day - 100))
lat_abs = abs(latitude)

if lat_abs < 23.45:
    k_factor = 1.2
elif lat_abs < 60:
    k_factor = 1.0
else:
    k_factor = 0.85

k = k_base * k_factor

# Kasten-Young air mass
m = 1 / (sin(β_rad) + 0.50572 * (β_deg + 6.07995)^(-1.6364))

# DNI calculation
DNI = A · e^(-k·m)
```

**Combined impact at 13.4° elevation:**
- k = 0.1197 (with k_factor = 0.85)
- m = 4.56 (Kasten-Young)
- DNI = 1234 × e^(-0.1197 × 4.56) = **733 W/m²** (+9% vs current)

This would make polar regions **brighter**, exacerbating the high DNI issue!

---

## Recommendations

### If 20 kWh/m² DNI seems **too high**:

**Use Option 2 with k_factor > 1.0 for polar regions:**
```python
# Polar regions have longer path through stratospheric ozone
# and increased Rayleigh scattering at low angles
if lat_abs > 60:
    k_factor = 1.15  # Increase attenuation
```

This acknowledges that even though polar air is clean, the **consistently low sun angles** mean more total atmospheric path.

### If 20 kWh/m² DNI seems **reasonable**:

**Use Option 3 (Kasten-Young) alone:**
- Improves physical accuracy
- Minimal code change
- Well-established formula
- Slightly reduces DNI at low angles

### For Maximum Accuracy:

**Combine both, tuning k_factor based on empirical data:**
- Use Kasten-Young for air mass (always better)
- Adjust k_factor after comparing to measured polar irradiance data
- Antarctic research stations publish weather data that could validate

---

## Implementation Complexity

**Option 2 (Latitude-dependent k):**
- Lines of code: ~10
- Testing needed: Low (simple multiplier)
- Risk: Low

**Option 3 (Kasten-Young):**
- Lines of code: ~5
- Testing needed: Medium (verify at all elevations)
- Risk: Very Low (well-established formula)

**Combined:**
- Lines of code: ~15
- Testing needed: Medium
- Risk: Low

---

## Research Questions to Answer

Before deciding, you might want to research:

1. **What is typical DNI in Antarctica during summer?**
   - Research stations publish weather data
   - Compare to model predictions

2. **How does atmospheric composition vary with latitude?**
   - Water vapor content (Precipitable Water Vapor maps)
   - Aerosol optical depth (NASA satellite data)

3. **Are there solar irradiance model standards for polar regions?**
   - NREL Solar Position Algorithm
   - Bird Clear Sky Model
   - DISC model

4. **What do commercial PV simulation tools use?**
   - PVsyst
   - SAM (System Advisor Model)
   - How do they handle extreme latitudes?

---

## My Recommendation

Start with **Option 3 (Kasten-Young)** because:
1. It's scientifically well-established
2. Low risk, easy to implement
3. Improves accuracy at all latitudes
4. Can always add Option 2 later if needed

Then validate against real-world data if available. If the model still predicts unreasonably high DNI at poles, add Option 2 with appropriate k_factor tuning.
