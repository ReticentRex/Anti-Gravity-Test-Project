# Governing Equations Analysis
**Source:** Ryan Coble-Neal Thesis Final (1).pdf

The thesis presents a comprehensive mathematical model linking solar geometry, atmospheric conditions, and vehicle dynamics to evaluate the feasibility of Two-Axis Sun-Tracking Photovoltaic Systems on Mobile Platforms.

## 1. Solar Geometry (The "Where")
These equations determine the relative position of the Sun and the PV panel.

*   **Solar Declination ($\delta$) [Eq 1]:** Calculates the angle of the sun relative to the equatorial plane based on the day of the year ($n$).
*   **Hour Angle ($H$) [Eq 2]:** Determines the sun's east-west position relative to the local meridian, based on solar time.
*   **Solar Time ($ST$) [Eq 3, 3.1]:** Adjusts local clock time for longitude and the **Equation of Time ($E$) [Eq 4]**, which accounts for Earth's elliptical orbit.
*   **Elevation ($\beta$) & Azimuth ($\phi_s$) [Eq 5, 6]:** These are the key outputs of the geometry section, defining the Sun's exact position in the sky for a given location ($L$) and time.
*   **Angle of Incidence ($\theta$) [Eq 7, 8]:** The critical link between the sun's position and the panel's orientation (tilt $\Sigma$, azimuth $\phi_c$). **Minimizing $\theta$ (keeping it close to 0°) is the primary goal of the two-axis tracking system.**

## 2. Solar Irradiance (The "How Much")
These equations calculate the available solar energy based on the geometry established above.

*   **Extraterrestrial Flux ($A$) [Eq 9]:** The baseline solar energy reaching the top of the atmosphere.
*   **Atmospheric Attenuation [Eq 10-12]:**
    *   **Optical Depth ($k$)** and **Air Mass ($m$)** reduce the beam intensity.
    *   **Direct Beam ($I_B$) [Eq 12]:** The remaining direct sunlight reaching the ground.
*   **Total Incident Irradiance ($I_C$) [Eq 19]:** The sum of three components:
    1.  **Beam Component ($I_{BC}$):** $I_B \cos(\theta)$ (Directly proportional to the cosine of the angle of incidence).
    2.  **Diffuse Component ($I_{DC}$):** Scattered light, dependent on the **Sky Diffuse Factor ($C$) [Eq 15]**.
    3.  **Reflected Component ($I_{RC}$):** Light reflected from the ground, dependent on surface reflectance ($\rho$).

**Relationship:** $I_C$ is the input "fuel" for the PV panel. The tracking system maximizes $I_{BC}$ by maximizing $\cos(\theta)$.

## 3. PV Panel Performance (The "Efficiency")
These equations determine how much of the incident irradiance is converted into electricity.

*   **Angular Loss ($AL$) [Eq 20]:** Accounts for reflection off the panel glass, which increases exponentially at high angles of incidence ($\theta > 55^\circ$).
*   **Temperature Effects [Eq 22-25]:**
    *   **Cell Temperature ($T_{cell}$):** Increases with irradiance ($S$) and ambient temperature ($T_{amb}$).
    *   **Efficiency Loss:** As $T_{cell}$ rises, Voltage ($V_{oc}$) and Power ($P_{mp}$) decrease.
*   **Overall Efficiency ($\mu_{pv}$) [Eq 26]:** The final ratio of electrical power output to solar power input.

## 4. Locomotive Performance (The "Cost")
These equations evaluate the energy cost of moving the vehicle, which is crucial for determining if the added weight/drag of a PV system is worth it.

*   **Net Force ($F_{net}$) [Eq 27-28]:** Sum of Tractive force ($F_t$), Rolling resistance ($F_f$), Gravity/Slope ($F_g$), and Aerodynamic Drag ($F_d$).
*   **Tractive Power ($P_t$) [Eq 32]:** The power required to maintain velocity.
    *   $P_t \propto mass \times velocity$ (Rolling resistance & Gravity)
    *   $P_t \propto Area \times velocity^3$ (Aerodynamic Drag)

**Key Insight [Eq 32.1]:** At higher speeds, aerodynamic drag dominates. Therefore, **minimizing the cross-sectional area ($A$) and drag coefficient ($C_d$) of the PV system is more critical than minimizing its mass.** This supports the need for a tracking system that can "stow flat" during transit.

## Summary of Relationships
1.  **Time & Location** $\rightarrow$ **Solar Geometry** ($\beta, \phi_s$)
2.  **Solar Geometry** + **Panel Orientation** $\rightarrow$ **Angle of Incidence** ($\theta$)
3.  **Angle of Incidence** + **Atmosphere** $\rightarrow$ **Total Irradiance** ($I_C$)
4.  **Total Irradiance** + **Temperature** $\rightarrow$ **PV Power Output** ($P_{mp}$)
5.  **Vehicle Design** + **Velocity** $\rightarrow$ **Power Consumption** ($P_t$)

**The Thesis Goal:** Maximize **PV Power Output** (via tracking) while minimizing the increase in **Power Consumption** (via aerodynamic design).
