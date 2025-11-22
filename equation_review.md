# Governing Equations Review
**Source:** Ryan Coble-Neal Thesis Final (1).pdf

This document outlines the specific mathematical conventions used in the thesis and identifies simplifying assumptions or potential issues in the governing equations.

## 1. Conventions Used
It is critical to follow these conventions when using the equations, as they may differ from other standard textbooks (e.g., Duffie & Beckman).

| Parameter              | Convention in Thesis                                     | Standard/Alternative                                 | Notes                                                    |
| :--------------------- | :------------------------------------------------------- | :--------------------------------------------------- | :------------------------------------------------------- |
| **Hour Angle ($H$)**   | **Positive (+) in Morning**<br>Negative (-) in Afternoon | Negative (-) in Morning<br>Positive (+) in Afternoon | *Eq 2: $H = 15 \times (12 - ST)$*<br>e.g., 10am = +30°   |
| **Azimuth ($\phi_s$)** | **North = 0°**<br>East = +90°<br>West = -90°             | South = 0° (Common in PV)<br>North = 0° (Navigation) | *Eq 6.1 checks this.*                                    |
| **Longitude**          | **West = Positive (+)**                                  | East = Positive (+)                                  | *Eq 3 is for West (+). Eq 3.1 is for East.*              |
| **Latitude**           | **North = Positive (+)**                                 | North = Positive (+)                                 | Standard.                                                |
| **Time**               | **Solar Time ($ST$)**                                    | Local Clock Time                                     | *Must convert using Eq 3/3.1 before finding Hour Angle.* |

## 2. Equation Review & Potential Issues

### Solar Irradiance Model (ASHRAE Clear Sky)
*   **Observation:** **Eq 9** uses $A = 1160 + ...$ for extraterrestrial flux.
*   **Context:** This is the **ASHRAE Clear Sky Model** parameter ("Apparent Extraterrestrial Flux"), not the physical Solar Constant ($G_{sc} \approx 1361 W/m^2$).
*   **Impact:** This model is designed to estimate terrestrial irradiance directly and inherently includes some atmospheric attenuation. It will produce lower "top of atmosphere" values than physics-based models, which is intentional for this specific empirical model.

### Reflected Irradiance (Albedo)
*   **Observation:** **Eq 18** calculates **Reflected Component ($I_{RC}$)** using $\rho$.
*   **User Clarification:** $\rho$ denotes **ground reflectance** (not cloud/sky), which explains the equation form.
*   **Equation:** $I_{RC} = \rho (I_{BH} + I_{DH}) \frac{1 - \cos(\Sigma)}{2}$
*   **View Factor:** The term $\frac{1 - \cos(\Sigma)}{2}$ is the **view factor to the ground**.
    *   If it were reflecting from the sky, it would use the sky view factor: $\frac{1 + \cos(\Sigma)}{2}$.
    *   This confirms $\rho$ is strictly modeling ground reflection (albedo).
*   **Ambiguity Note:** The text writes `(1 - cos(E) / 2 )`. Mathematically, this must be interpreted as `(1 - cos(E)) / 2`.

### PV Performance Simplifications
*   **Open Circuit Voltage ($V_{oc}$) [Eq 24]:**
    *   $V_{oc} = V_{oc,STC}[1 + \alpha_v(T_{cell} - 25)]$
    *   **Issue:** This equation **ignores the logarithmic dependence of voltage on irradiance**.
    *   **Reality:** $V_{oc}$ drops significantly at low light levels (e.g., sunrise/sunset/clouds).
    *   **Impact:** The model will **overestimate power generation** during low-irradiance periods, as it assumes voltage remains high even when there is little light.

*   **Short Circuit Current ($I_{sc}$) [Eq 23]:**
    *   Assumes linear scaling with Irradiance ($S$). This is a standard and generally accurate assumption for crystalline silicon.

### Locomotive Equations
*   **Aerodynamic Drag [Eq 28.3]:** Standard form.
*   **Rolling Resistance [Eq 28.1]:** Standard form.
*   **No Errors Found:** The derivation from Force to Power ($P = Fv$) and the cubic relationship with velocity ($v^3$) for drag power are physically correct.

## 3. Summary
The mathematical model is largely self-consistent, provided the specific sign conventions (especially for Hour Angle) are respected. The main physical limitations are the **linear voltage model** (optimistic at low light) and the use of the **ASHRAE clear sky model** (which is an estimation tool, not a precise spectral physics model).
