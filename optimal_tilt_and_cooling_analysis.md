# Optimal Tilt and Cooling Logic Analysis

## 1. Optimal Tilt Calculation

### Location in Code
`solar_model.py` - `calculate_optimal_tilt()` function (lines 367-455)

### How It Works
The function searches for the optimal tilt angle by:
1. **Search Range:** Latitude ± 5 degrees
   - For Perth (-32°S): Tests tilts from 27° to 37°
   - Ensures practical range around the common "tilt = latitude" rule
   
2. **Two Optimization Modes:**
   
   **Mode 1: Optimize for Electrical Yield** (`optimize_electrical=True`)
   - Maximizes actual power output (`P_out`)
   - Accounts for:
     - Temperature effects on efficiency
     - Angular reflection losses (IAM)
     - Seasonal variation
   - Finds the tilt that produces the most kWh/year
   
   **Mode 2: Optimize for Incident Irradiance** (`optimize_electrical=False`)
   - Maximizes total incident irradiance (`Ic`)
   - Purely geometric optimization
   - Ignores thermal effects
   - Finds the tilt that captures the most sunlight (W/m²)

3. **Process:**
   ```python
   for tilt in range(lat-5, lat+6):
       for each hour of the year:
           calculate irradiance on panel at this tilt
           if optimize_electrical:
               sum electrical output (P_out)
           else:
               sum incident irradiance (Ic)
       
       if total > best_so_far:
           best_tilt = tilt
   ```

### Where It's Used
- `solar_app.py` line 496: Called when "Run Simulation" button is pressed
- The result is passed to `generate_annual_profile()` as the `optimal_tilt` parameter
- Used for 1-Axis Azimuth tracker and other configurations that need a "default" tilt

### Example Results
For Perth (-32°S):
- **Irradiance-optimized:** ~28-30° (slightly less than latitude)
- **Electrical-optimized:** ~25-27° (even lower, favors cooler seasons)

The electrical-optimized tilt is typically **2-5° lower** than irradiance-optimized because:
- Lower tilt → Better capture of high summer sun (when panels get hot and efficiency drops)
- Trade-off: Accept slightly less winter irradiance for better summer efficiency

---

## 2. Active Cooling Logic - ISSUE IDENTIFIED

### Current Implementation
The code calculates "cooled" performance by using `P_at_25C`:

```python
# In calculate_pv_performance():
P_ref_25C = EFF_STC * S_W_m2  # Power if panel were at 25°C
T_cell = T_amb + (NOCT - 20) / 0.8 * S_kW_m2  # Actual cell temp
temp_factor = 1 + ALPHA_P * (T_cell - 25)
P_out = P_ref_25C * temp_factor  # Actual power at T_cell

# In generate_annual_profile():
totals['Annual_Yield_Cooled_XXX'] += P_at_25C * step_factor / 1000
```

### The Problem
**When `T_cell < 25°C`, the panel naturally performs BETTER than at 25°C.**

Example - Winter Morning:
- `T_amb = 10°C`
- `Ic = 400 W/m²` (low irradiance)
- `T_cell = 10 + (45-20)/0.8 * 0.4 = 22.5°C`
- `P_ref_25C = 0.14 * 400 = 56 W/m²` (power at 25°C)
- `temp_factor = 1 + (-0.0045) * (22.5 - 25) = 1.011` (11% better!)
- `P_out = 56 * 1.011 = 56.6 W/m²` (actual power)

**Current "Cooling" Benefit:**
- Cooled Power: `P_at_25C = 56.0 W/m²`
- Actual Power: `P_out = 56.6 W/m²`
- "Benefit": `56.0 - 56.6 = -0.6 W/m²` **NEGATIVE!**

This means the code is saying "cooling would make it worse" - but that's because it would require **heating** the panel from 22.5°C to 25°C!

### The Fix
**Cooling should only activate when `T_cell > 25°C`:**

```python
# Correct logic:
if T_cell > 25:
    P_cooled = P_ref_25C  # Cool to 25°C
else:
    P_cooled = P_out  # Already cold, no cooling needed
```

### Proposed Code Change
In `calculate_pv_performance()`, add a new return value:

```python
# After calculating P_out and P_ref_25C:
if T_cell > 25:
    P_cooled = P_ref_25C  # Cooling benefit available
    cooling_benefit = P_ref_25C - P_out  # Positive value
else:
    P_cooled = P_out  # Already below 25°C, no cooling needed
    cooling_benefit = 0  # No benefit from cooling

return {
    'P_out': max(0, P_out),
    'P_at_25C': max(0, P_ref_25C),
    'P_cooled': max(0, P_cooled),  # NEW: Smart cooling
    'Cooling_Benefit': cooling_benefit,  # NEW: Actual benefit
    'Loss_Angular': max(0, Loss_Angular),
    'Loss_Thermal': Loss_Thermal,
    'T_cell': T_cell
}
```

Then update all `P_at_25C` usages to `P_cooled`.

### Impact
This fix will:
1. ✅ Prevent "negative cooling benefit" in winter/cold climates
2. ✅ More accurately represent active cooling systems (e.g., water-cooled panels)
3. ✅ Show realistic cooling benefits concentrated in summer/hot climates
4. ✅ Make the "Active Cooling Benefit" section in the UI meaningful

---

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| **Optimal Tilt Calculation** | ✅ Working | Searches lat±5°, supports 2 modes |
| **Tilt Usage** | ✅ Correct | Used for 1-axis azimuth and defaults |
| **Cooling Logic** | ❌ **BUG** | Tries to "cool" panels that are already cold |
| **Fix Required** | 🔧 Yes | Add smart cooling: only cool if T_cell > 25°C |

**Recommendation:** Implement the proposed fix to make cooling logic physically realistic.
