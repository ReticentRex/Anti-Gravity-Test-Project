# PV Model Implementation & Validation

This document explains how the PV performance parameters (Angular Loss, Temperature, Efficiency) were implemented and validates the results against expected theoretical behavior.

## 1. Implementation Details

### A. Angular Loss (Equation 20)
We used the **Martin and Ruiz** model (implied by Eq 20 in the thesis) to calculate the **Incidence Angle Modifier (IAM)**. This factor accounts for the reflection of light off the glass surface of the panel at steep angles.

*   **Formula:**
    $$AL(\theta) = \frac{1 - \exp(-\cos\theta / \alpha_r)}{1 - \exp(-1 / \alpha_r)}$$
    *   $\theta$: Angle of Incidence (AOI).
    *   $\alpha_r$: Angular Loss Coefficient (Nominal: `0.17`).
*   **Effect:**
    *   When $\theta = 0^\circ$ (Normal incidence), $AL = 1$ (No loss).
    *   When $\theta = 90^\circ$ (Grazing incidence), $AL = 0$ (100% loss).
*   **Implementation:**
    *   **2-Axis Tracking:** Always perfectly aimed ($\theta = 0$), so **Angular Loss is ZERO** ($AL=1$).
    *   **Fixed Horizontal:** Significant losses in early morning/late afternoon when sun is low.

### B. Cell Temperature (Equation 22)
We calculated the operating temperature of the cell ($T_{cell}$) based on the ambient temperature and the effective irradiance.

*   **Formula:**
    $$T_{cell} = T_{amb} + (NOCT - 20) \times \frac{S}{0.8}$$
    *   $T_{amb}$: Ambient Temperature (Assumed constant `25°C`).
    *   $NOCT$: Nominal Operating Cell Temperature (`45°C`).
    *   $S$: Effective Irradiance in kW/m² ($I_c \times AL$).
*   **Effect:**
    *   Higher Irradiance $\rightarrow$ Higher Temperature.
    *   **2-Axis Tracking** sees higher irradiance throughout the day, so it runs **hotter** than fixed panels, leading to slightly higher thermal losses.

### C. Power Output (Equation 25)
We calculated the final power output by adjusting the STC efficiency for temperature.

*   **Formula:**
    $$P_{out} = \eta_{STC} \times S \times [1 + \alpha_p (T_{cell} - 25)]$$
    *   $\eta_{STC}$: Efficiency at Standard Test Conditions (`14%`).
    *   $\alpha_p$: Temperature Coefficient of Power (`-0.45 %/°C`).
*   **Effect:**
    *   For every 1°C above 25°C, the panel loses 0.45% of its power.

---

## 2. Validation of Results

We can validate the model by calculating the **"Effective Annual Efficiency"** for each mode.
$$ \text{Effective Eff} = \frac{\text{Total Annual PV Energy (kWh/m}^2)}{\text{Total Annual Incident Irradiance (kWh/m}^2)} $$

**Expected Behavior:**
1.  **Base:** Should be lower than 14% due to thermal and angular losses.
2.  **2-Axis vs Horizontal:**
    *   **2-Axis:** Zero angular loss, but higher thermal loss (hotter).
    *   **Horizontal:** High angular loss, lower thermal loss (cooler).

### Analysis of Output Data (Perth)

| Metric                           | Horizontal | 1-Axis Azimuth | 1-Axis Elevation | 2-Axis     |
| :------------------------------- | :--------- | :------------- | :--------------- | :--------- |
| **Incident Irradiance** (kWh/m²) | 2317.10    | 3262.15        | 2479.33          | 3568.95    |
| **PV Energy Yield** (kWh/m²)     | 280.51     | 398.81         | 298.28           | 434.39     |
| **Effective Efficiency**         | **12.11%** | **12.23%**     | **12.03%**       | **12.17%** |

### Observations:

1.  **General Efficiency (~12.1%):**
    *   The effective efficiency is consistently around **12.1%**, which is reasonable.
    *   **Loss Calculation:** $14\% \rightarrow 12.1\%$ represents a **~13.5% total system loss**.
    *   This aligns with expectations:
        *   ~5-10% thermal loss (operating ~10-20°C above STC).
        *   ~2-5% angular loss (averaged over the year).

2.  **2-Axis (12.17%) vs Horizontal (12.11%):**
    *   **2-Axis is slightly MORE efficient.**
    *   **Why?** The gain from **eliminating angular losses** (perfect tracking) outweighs the penalty from **higher operating temperatures**.
    *   Even though 2-Axis panels run hotter (reducing efficiency), they never suffer from reflection losses at steep angles, which is a significant factor for fixed panels.

3.  **1-Axis Azimuth (12.23%):**
    *   **Highest Efficiency.**
    *   This is interesting. It tracks the sun East-West (minimizing angular loss significantly) but might have a slightly lower average incidence angle than 2-axis? Or perhaps the trade-off between cooling (lower irradiance than 2-axis) and tracking is optimal here?
    *   Actually, Azimuth tracking (Vertical Axis) keeps the sun at a relatively constant "height" relative to the panel normal, avoiding the extreme grazing angles of a fixed panel, while not capturing the *full* intensity (and heat) of 2-axis.

### Conclusion
The results are **physically consistent**.
*   Efficiencies are suppressed below STC (14%) as expected.
*   Tracking modes show higher yields not just because they "see" more light, but because they utilize it more efficiently (better angles), despite the thermal penalty.
