# Azimuth Angle Correction for Global Latitudes

This document details the mathematical correction applied to the Solar Azimuth Angle ($\phi_s$) calculation to ensure validity for both Northern and Southern Hemispheres.

## The Original Equation (Thesis Eq 6.1)

The thesis provides the following inequality to determine the quadrant of the sun:

$$ \cos(H) \ge \frac{\tan(\delta)}{\tan(L)} $$

Where:
*   $H$ is the Hour Angle.
*   $\delta$ is the Solar Declination.
*   $L$ is the Latitude.

The thesis states:
> "If the condition is met, then $|\phi_s| \le 90^\circ$ (Sun is generally North). Else, $|\phi_s| > 90^\circ$ (Sun is generally South)."

**This logic is correct for the Southern Hemisphere**, where the "normal" sun direction (towards the Equator) is North ($0^\circ$).

## The Problem for Northern Hemisphere

In the Northern Hemisphere ($L > 0$):
*   The Equator is to the **South** ($180^\circ$).
*   The "normal" sun direction is South.

However, the inequality $\cos(H) \ge \frac{\tan(\delta)}{\tan(L)}$ essentially tests if the sun is **"Equatorward"** of the observer.

*   If the condition is **True** (Sun is Equatorward):
    *   In Southern Hemisphere: Equator is North $\rightarrow$ Sun is North ($|\phi_s| \le 90^\circ$).
    *   In Northern Hemisphere: Equator is South $\rightarrow$ Sun is South ($|\phi_s| > 90^\circ$).

## The Corrected Logic

To handle both hemispheres correctly, we interpret the inequality result based on the sign of the Latitude ($L$).

Let $C$ be the boolean result of the inequality:
$$ C = \left( \cos(H) \ge \frac{\tan(\delta)}{\tan(L)} \right) $$

### Case 1: Southern Hemisphere ($L < 0$)
*   **If $C$ is True:** Sun is North ($|\phi_s| \le 90^\circ$).
*   **If $C$ is False:** Sun is South ($|\phi_s| > 90^\circ$).

### Case 2: Northern Hemisphere ($L > 0$)
*   **If $C$ is True:** Sun is South ($|\phi_s| > 90^\circ$).
*   **If $C$ is False:** Sun is North ($|\phi_s| \le 90^\circ$).

## Implementation in Python

```python
# Calculate the check value
check_val = np.tan(delta_rad) / np.tan(lat_rad)
condition_met = np.cos(H_rad) >= check_val

is_north_hemisphere = self.latitude > 0

if is_north_hemisphere:
    # Northern Hemisphere Logic
    if condition_met:
        # Sun is South (|phi| > 90)
        phi_s = adjust_to_obtuse(phi_s)
    # else: Sun is North (|phi| <= 90), no adjustment needed
else:
    # Southern Hemisphere Logic
    if not condition_met:
        # Sun is South (|phi| > 90)
        phi_s = adjust_to_obtuse(phi_s)
    # else: Sun is North (|phi| <= 90), no adjustment needed
```
