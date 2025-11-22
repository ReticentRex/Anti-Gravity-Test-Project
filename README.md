# Solar Resource & PV Performance Model

A physics-based solar energy simulation tool that calculates hourly solar irradiance and photovoltaic (PV) power output for different collector orientations.

## Overview

This project implements the solar resource and PV performance equations from the Ryan Coble-Neal thesis, providing detailed analysis of:

- Solar geometry and position tracking
- Atmospheric attenuation (ASHRAE Clear Sky Model)
- Four collector orientations (Horizontal, 1-Axis Azimuth, 1-Axis Elevation, 2-Axis)
- PV panel performance including angular and thermal losses

## Features

- **Accurate Physics**: Implements thesis equations for solar geometry (Eq 1-6), irradiance (Eq 9-19), and PV performance (Eq 20-26)
- **Multiple Tracking Modes**: Compare fixed, single-axis, and dual-axis tracking systems
- **Loss Analysis**: Detailed breakdown of angular reflection and thermal losses
- **Interactive GUI**: Streamlit web application for easy visualization
- **Comprehensive Output**: Hourly data with annual summaries in CSV format

## Installation

1. Clone this repository
2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies:

   ```bash
   pip install pandas numpy streamlit plotly
   ```

## Usage

### Command Line

Run the solar model directly:

```bash
python solar_model.py
```

This generates `solar_model_output.csv` with hourly data and annual summaries.

### Web GUI

Launch the interactive Streamlit dashboard:

```bash
streamlit run solar_app.py
```

Then:

1. Enter your location (latitude/longitude) in the sidebar
2. Click "Run Simulation"
3. View interactive charts and download results

## Output

The model generates:

- **Hourly irradiance** (W/m²) for each collector orientation
- **Hourly PV power output** (W/m²) accounting for losses
- **Annual energy yields** (kWh/m²)
- **Performance ratios** comparing each mode to 2-axis tracking
- **Loss breakdowns** (angular vs thermal)

## Example Results (Perth, Australia)

| Orientation | Annual Yield (kWh/m²) | vs 2-Axis |
|-------------|----------------------|-----------|
| Horizontal | 280.5 | 64.6% |
| 1-Axis Azimuth | 398.8 | 91.8% |
| 1-Axis Elevation | 298.3 | 68.7% |
| 2-Axis | 434.4 | 100% |

## Project Structure

- `solar_model.py` - Core simulation engine
- `solar_app.py` - Streamlit GUI application
- `pv_validation.md` - Physics validation and analysis
- `governing_equations.md` - Equation documentation
- `equation_review.md` - Detailed equation review

## Technical Details

**Solar Geometry**: Calculates sun position using declination angle, hour angle, and local coordinates.

**Irradiance Model**: ASHRAE Clear Sky Model with atmospheric attenuation factors for beam and diffuse radiation.

**PV Performance**:

- Nominal efficiency: 14%
- NOCT: 45°C
- Temperature coefficient: -0.45%/°C
- Angular loss coefficient: 0.17

## License

This project implements equations from academic research. Please cite the original thesis if using this work.

## Author

Developed based on the thesis: "Identifying the Factors Impacting the Performance of Two-Axis Sun-Tracking Photovoltaic Systems on Mobile Platforms" by Ryan Coble-Neal.
