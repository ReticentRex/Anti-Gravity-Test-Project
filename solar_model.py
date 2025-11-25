import numpy as np
import pandas as pd

class SolarModel:
    def __init__(self, latitude, longitude):
        """
        Initialize the Solar Model with location coordinates.
        
        Args:
            latitude (float): Latitude in degrees (North +, South -)
            longitude (float): Longitude in degrees (East +, West -)
        """
        self.latitude = latitude
        self.longitude = longitude
        
        # Determine Time Zone Meridian (approximate based on longitude)
        # 15 degrees per hour. 
        # Thesis convention: West Longitude is +ve in Eq 3, but standard UTC is East +ve.
        # We will use standard convention for input (East +ve) and adapt equations.
        # Local Time Meridian = round(Longitude / 15) * 15
        self.local_time_meridian = round(longitude / 15) * 15
        
        # Default Tilt (Latitude) and Azimuth (Equator facing)
        self.tilt = abs(latitude)
        if latitude < 0:
            self.azimuth = 0 # North facing for Southern Hemisphere
        else:
            self.azimuth = 180 # South facing for Northern Hemisphere

    def calculate_ambient_temperature(self, day_of_year, hour):
        """
        Calculate ambient temperature using sinusoidal model.
        Varies with season (annual cycle) and time of day (diurnal cycle).
        Temperature parameters scale with latitude for realism.
        
        Args:
            day_of_year (int): Day number (1-365)
            hour (float): Local clock time (0-23.99)
            
        Returns:
            float: Ambient temperature in °C
        """
        # Absolute latitude for temperature scaling
        abs_lat = abs(self.latitude)
        
        # Annual average temperature (decreases with latitude)
        # Equator: ~27°C, Mid-latitudes (30-40°): ~18°C, Polar (60°+): ~5°C
        if abs_lat < 23.45:  # Tropical
            T_avg = 27 - 0.15 * abs_lat
        elif abs_lat < 50:  # Temperate
            T_avg = 30 - 0.4 * abs_lat
        else:  # Polar
            T_avg = 20 - 0.3 * abs_lat
        
        # Seasonal amplitude (increases with latitude)
        # Equator: ~2°C variation, Mid-latitudes: ~10°C, Polar: ~20°C
        if abs_lat < 23.45:
            delta_T_seasonal = 2 + 0.15 * abs_lat
        elif abs_lat < 66.5:
            delta_T_seasonal = 5 + 0.3 * abs_lat
        else:
            delta_T_seasonal = 20
        
        # Diurnal (daily) amplitude: ~8-12°C typically
        delta_T_diurnal = 10
        
        # Seasonal cycle: Peak summer temperature
        # Southern Hemisphere: Day ~15 (mid-Jan), Northern Hemisphere: Day ~195 (mid-July)
        if self.latitude < 0:
            day_offset = 15  # Southern summer peak
        else:
            day_offset = 195  # Northern summer peak
        
        T_seasonal = T_avg + delta_T_seasonal * np.cos(2 * np.pi * (day_of_year - day_offset) / 365)
        
        # Diurnal cycle: Peak temperature around 2-3 PM (hour 14-15)
        # Using sine wave: minimum at ~3 AM (hour 3), maximum at ~3 PM (hour 15)
        # Offset by 3 hours so minimum is at 3 AM
        hour_offset = 3  # Minimum at 3 AM
        T_diurnal_variation = -delta_T_diurnal * np.cos(2 * np.pi * (hour - hour_offset) / 24)
        
        T_amb = T_seasonal + T_diurnal_variation
        
        # Ensure reasonable bounds (not below -50°C or above 50°C in most cases)
        T_amb = np.clip(T_amb, -50, 55)
        
        return T_amb
        
    def calculate_geometry(self, day_of_year, hour):
        """
        Calculate solar geometry parameters for a given day and hour.
        
        Args:
            day_of_year (int): Day number (1-365)
            hour (float): Local clock time (0-23.99)
            
        Returns:
            dict: Dictionary containing geometry parameters
        """
        n = day_of_year
        
        # 1. Solar Declination (delta) [Eq 1]
        # Use 2π/365 for smooth annual cycle in radians
        delta_deg = 23.45 * np.sin(2 * np.pi / 365 * (n - 81))
        delta_rad = np.radians(delta_deg)
        
        # 2. Equation of Time (E) [Eq 4, 4.1]
        # B should be in radians for use in trig functions
        # Uses 364 per Masters (2013) - empirical fit for equation of time
        B_rad = 2 * np.pi / 364 * (n - 81)
        E_min = 9.87 * np.sin(2*B_rad) - 7.53 * np.cos(B_rad) - 1.5 * np.sin(B_rad)
        
        # 3. Solar Time (ST) [Eq 3.1 for East Longitude]
        # ST = CT + 4 min/deg * (Local Longitude - Local Time Meridian) + E
        time_correction_min = 4 * (self.longitude - self.local_time_meridian) + E_min
        solar_time_hours = hour + time_correction_min / 60
        
        # 4. Hour Angle (H) [Eq 2]
        # Thesis Convention: Positive in Morning (before solar noon)
        # H = 15 * (12 - ST)
        H_deg = 15 * (12 - solar_time_hours)
        H_rad = np.radians(H_deg)
        
        # 5. Elevation Angle (beta) [Eq 5]
        lat_rad = np.radians(self.latitude)
        sin_beta = np.cos(lat_rad) * np.cos(delta_rad) * np.cos(H_rad) + \
                   np.sin(lat_rad) * np.sin(delta_rad)
        beta_rad = np.arcsin(np.clip(sin_beta, -1, 1)) # Clip for numerical stability
        beta_deg = np.degrees(beta_rad)
        
        # 6. Azimuth Angle (phi_s) [Eq 6, 6.1]
        # Thesis Convention: North = 0, East = +90, West = -90
        
        # Calculate uncorrected azimuth
        if np.cos(beta_rad) == 0:
            phi_s_deg = 0 # Zenith
        else:
            sin_phi_s = (np.cos(delta_rad) * np.sin(H_rad)) / np.cos(beta_rad)
            phi_s_rad = np.arcsin(np.clip(sin_phi_s, -1, 1))
            phi_s_deg = np.degrees(phi_s_rad)
            
            # Check quadrant [Eq 6.1]
            # If cos(H) >= tan(delta)/tan(lat), then |phi_s| <= 90
            # Note: tan(lat) can be 0 at equator, handle division by zero
            if np.tan(lat_rad) == 0:
                check_val = np.inf if np.tan(delta_rad) >= 0 else -np.inf
            else:
                check_val = np.tan(delta_rad) / np.tan(lat_rad)
                
            # The thesis condition seems to be derived for Southern Hemisphere (where Sun is normally North, i.e., |phi| <= 90).
            # For Northern Hemisphere (Lat > 0), Sun is normally South (i.e., |phi| > 90).
            # We need to adjust the logic based on hemisphere.
            
            is_north_hemisphere = self.latitude >= 0
            condition_met = np.cos(H_rad) >= check_val
            
            if is_north_hemisphere:
                # In Northern Hemisphere:
                # If condition met (Summer-like), Sun is North (|phi| <= 90).
                # If condition NOT met (Winter-like), Sun is South (|phi| > 90).
                
                # So for North Hem:
                # Met -> South (>90)
                # Not Met -> North (<=90)
                if condition_met:
                     # |phi_s| > 90
                    if phi_s_deg > 0:
                        phi_s_deg = 180 - phi_s_deg
                    else:
                        phi_s_deg = -180 - phi_s_deg
                # else: keep |phi_s| <= 90
                
            else:
                # Southern Hemisphere (Original Thesis Logic)
                # Met -> North (<=90)
                # Not Met -> South (>90)
                if not condition_met:
                    # |phi_s| > 90
                    if phi_s_deg > 0:
                        phi_s_deg = 180 - phi_s_deg
                    else:
                        phi_s_deg = -180 - phi_s_deg
                    
        return {
            'declination': delta_deg,
            'hour_angle': H_deg,
            'solar_time': solar_time_hours,
            'elevation': beta_deg,
            'azimuth': phi_s_deg
        }

    def calculate_irradiance(self, day_of_year, elevation_deg):
        """
        Calculate solar irradiance components.
        
        Args:
            day_of_year (int): Day number
            elevation_deg (float): Solar elevation in degrees
            
        Returns:
            dict: Dictionary containing irradiance components
        """
        n = day_of_year
        beta_rad = np.radians(elevation_deg)
        
        # If sun is below horizon, irradiance is 0
        if elevation_deg <= 0:
            return {
                'extraterrestrial': 0,
                'optical_depth': 0,
                'air_mass': 0,
                'dni': 0,
                'diffuse_factor': 0,
                'diffuse_horizontal': 0,
                'global_horizontal': 0
            }
            
        # 1. Apparent Extraterrestrial Flux (A) [Eq 9]
        # Convert to radians: sin expects radians, so we use 2π/365 instead of 360/365
        A = 1160 + 75 * np.sin(2 * np.pi / 365 * (n - 275))
        
        # 2. Optical Depth (k) [Eq 10]
        k = 0.174 + 0.035 * np.sin(2 * np.pi / 365 * (n - 100))
        
        # 3. Air Mass (m) [Eq 11]
        # Prevent division by zero for very low angles
        sin_beta = np.sin(beta_rad)
        if sin_beta < 0.01: # Approx 0.5 degrees
             m = 1 / 0.01 # Cap air mass
        else:
            m = 1 / sin_beta
            
        # 4. Direct Normal Irradiance (Ib) [Eq 12]
        # This is the beam component measured perpendicular to the sun's rays
        Ib = A * np.exp(-k * m)
        
        # 5. Sky Diffuse Factor (C) [Eq 15]
        C = 0.095 + 0.04 * np.sin(2 * np.pi / 365 * (n - 100))
        
        # 6. Diffuse Horizontal Irradiance (Idh) [Eq 16]
        # Note: Thesis Eq 16 says Idh = C * Ib. 
        # Usually Diffuse is a fraction of Global or Extraterrestrial, 
        # but here it is modeled as a fraction of the Direct Beam.
        Idh = C * Ib
        
        # 7. Beam Horizontal Irradiance (Ibh) [Eq 13]
        Ibh = Ib * np.sin(beta_rad)
        
        # 8. Global Horizontal Irradiance (GHI)
        GHI = Ibh + Idh
        
        return {
            'extraterrestrial': A,
            'optical_depth': k,
            'air_mass': m,
            'dni': Ib,
            'diffuse_factor': C,
            'diffuse_horizontal': Idh,
            'global_horizontal': GHI
        }

    def calculate_incident_irradiance(self, beta_deg, phi_s_deg, sigma_deg, phi_c_deg, Ib, C, rho=0.2):
        """
        Calculate total incident irradiance (Ic) on a tilted surface.
        
        Args:
            beta_deg: Solar Elevation
            phi_s_deg: Solar Azimuth
            sigma_deg: Panel Tilt
            phi_c_deg: Panel Azimuth
            Ib: Direct Normal Irradiance
            C: Sky Diffuse Factor
            rho: Ground Reflectance (Albedo)
            
        Returns:
            tuple: (Total Incident Irradiance Ic, Cosine of Incidence Angle cos_theta)
        """
        # Convert to radians
        beta = np.radians(beta_deg)
        phi_s = np.radians(phi_s_deg)
        sigma = np.radians(sigma_deg)
        phi_c = np.radians(phi_c_deg)
        
        # 1. Angle of Incidence (theta) [Eq 8]
        cos_theta = np.cos(beta) * np.cos(phi_s - phi_c) * np.sin(sigma) + \
                    np.sin(beta) * np.cos(sigma)
        
        # Clamp cos_theta to 0 (sun behind panel)
        cos_theta = max(0, cos_theta)
        
        # 2. Beam Component (Ibc) [Eq 14]
        Ibc = Ib * cos_theta
        
        # 3. Diffuse Component (Idc) [Eq 17]
        # Idc = C * Ib * (1 + cos(sigma))/2
        Idc = C * Ib * (1 + np.cos(sigma)) / 2
        
        # 4. Reflected Component (Irc) [Eq 18]
        # Irc = rho * Ib * (sin(beta) + C) * (1 - cos(sigma))/2
        Irc = rho * Ib * (np.sin(beta) + C) * (1 - np.cos(sigma)) / 2
        
        # Total Incident Irradiance [Eq 19]
        Ic = Ibc + Idc + Irc
        return Ic, cos_theta

    def calculate_pv_performance(self, Ic, cos_theta, T_amb=25, efficiency=0.14):
        """
        Calculate PV Power Output and Losses.
        
        Args:
            Ic (float): Total Incident Irradiance (W/m2)
            cos_theta (float): Cosine of Angle of Incidence
            T_amb (float): Ambient Temperature (C)
            efficiency (float): PV Module Efficiency (0.0 to 1.0). Default 0.14.
            
        Returns:
            dict: {
                'P_out': PV Power Output (W/m2),
                'Loss_Angular': Irradiance Loss due to reflection (W/m2),
                'Loss_Thermal': Power Loss due to temperature (W/m2)
            }
        """
        # Nominal Parameters
        ALPHA_R = 0.17 # Angular Loss Coefficient
        NOCT = 45.0    # Nominal Operating Cell Temp [C]
        EFF_STC = efficiency # Efficiency at STC
        ALPHA_P = -0.0045 # Power Temp Coefficient (-0.45%/C)
        
        # 1. Angular Loss (AL)
        if cos_theta <= 0:
            IAM = 0
        else:
            numerator = 1 - np.exp(-cos_theta / ALPHA_R)
            denominator = 1 - np.exp(-1 / ALPHA_R)
            IAM = numerator / denominator
            
        # Effective Irradiance (S)
        S_W_m2 = Ic * IAM
        
        # Angular Loss (Irradiance Level)
        Loss_Angular = Ic - S_W_m2
        
        # 2. Cell Temperature (T_cell)
        S_kW_m2 = S_W_m2 / 1000.0
        T_cell = T_amb + (NOCT - 20) / 0.8 * S_kW_m2
        
        # 3. Power Calculation
        # Reference Power at 25C (after angular loss)
        P_ref_25C = EFF_STC * S_W_m2
        
        # Actual Power at T_cell
        temp_factor = 1 + ALPHA_P * (T_cell - 25)
        P_out = P_ref_25C * temp_factor
        
        # Thermal Loss (Power Level)
        # Positive value means loss (produced less than at 25C)
        Loss_Thermal = P_ref_25C - P_out
        
        return {
            'P_out': max(0, P_out),
            'P_at_25C': max(0, P_ref_25C),  # Theoretical power if cooled to 25°C
            'Loss_Angular': max(0, Loss_Angular),
            'Loss_Thermal': Loss_Thermal,
            'T_cell': T_cell
        }

    def calculate_optimal_tilt(self, efficiency=0.2, optimize_electrical=False):
        """
        Calculates the optimal tilt angle for a fixed south-facing panel (or north-facing in SH).
        Checks range: Latitude +/- 5 degrees.
        
        Args:
            efficiency: PV module efficiency (0.0 to 1.0)
            optimize_electrical: If True, maximizes electrical yield (accounting for thermal losses).
                                If False, maximizes incident irradiance only (geometric optimum).
        
        Returns: (optimal_tilt, max_yield_kwh_m2) where max_yield is the ELECTRICAL yield at optimal tilt
        """
        # Pre-calculate solar geometry and irradiance for all daylight hours to speed up optimization
        daylight_data = []
        for day in range(1, 366):
            for hour in range(24):
                geom = self.calculate_geometry(day, hour)
                if geom['elevation'] <= 0: continue
                
                irrad = self.calculate_irradiance(day, geom['elevation'])
                T_amb = self.calculate_ambient_temperature(day, hour)
                
                daylight_data.append({
                    'beta': geom['elevation'],
                    'phi_s': geom['azimuth'],
                    'Ib': irrad['dni'],
                    'C': irrad['diffuse_factor'],
                    'T_amb': T_amb
                })
        
        best_tilt = 0
        max_optimization_value = 0
        
        # Search range: Latitude +/- 5 degrees
        lat_abs = abs(self.latitude)
        start_tilt = max(0, int(lat_abs) - 5)
        end_tilt = int(lat_abs) + 6 # +6 because range is exclusive at end
        
        for tilt in range(start_tilt, end_tilt):
            if optimize_electrical:
                # Mode 1: Optimize for electrical yield (with thermal losses)
                total_value = 0
                panel_azimuth = 0 if self.latitude < 0 else 180
                
                for data in daylight_data:
                    Ic, cos_theta = self.calculate_incident_irradiance(
                        data['beta'], data['phi_s'], 
                        tilt, panel_azimuth, 
                        data['Ib'], data['C']
                    )
                    
                    # Calculate PV performance to get electrical output
                    pv_result = self.calculate_pv_performance(Ic, cos_theta, T_amb=data['T_amb'], efficiency=efficiency)
                    total_value += (pv_result['P_out'] / 1000.0)  # Convert W to kW, sum over hours
            else:
                # Mode 2: Optimize for incident irradiance only (geometric optimum)
                total_value = 0
                panel_azimuth = 0 if self.latitude < 0 else 180
                
                for data in daylight_data:
                    Ic, cos_theta = self.calculate_incident_irradiance(
                        data['beta'], data['phi_s'], 
                        tilt, panel_azimuth, 
                        data['Ib'], data['C']
                    )
                    
                    # Sum incident irradiance energy (Ic is W/m², divide by 1000 to get kWh/m²)
                    total_value += (Ic / 1000.0)
            
            if total_value > max_optimization_value:
                max_optimization_value = total_value
                best_tilt = tilt
        
        # Always calculate the ELECTRICAL yield at the optimal tilt for comparison purposes
        total_electrical_yield = 0
        panel_azimuth = 0 if self.latitude < 0 else 180
        
        for data in daylight_data:
            Ic, cos_theta = self.calculate_incident_irradiance(
                data['beta'], data['phi_s'], 
                best_tilt, panel_azimuth, 
                data['Ib'], data['C']
            )
            
            # Calculate PV performance to get electrical output
            pv_result = self.calculate_pv_performance(Ic, cos_theta, T_amb=data['T_amb'], efficiency=efficiency)
            total_electrical_yield += (pv_result['P_out'] / 1000.0)  # Convert W to kW, sum over hours
                
        return best_tilt, total_electrical_yield  # Return kWh/m2 electrical yield

    def generate_annual_profile(self, efficiency=0.2, fixed_tilt=None, fixed_azimuth=None, optimal_tilt=None):
        """
        Generate hourly solar profile for the entire year.
        Calculates irradiance, PV Power, and Losses for 4 collector orientations.
        Optionally calculates for a 5th "Fixed Custom" orientation.
        
        Args:
            fixed_tilt (float, optional): Tilt angle for custom fixed panel.
            fixed_azimuth (float, optional): Azimuth angle for custom fixed panel.
            optimal_tilt (float, optional): Optimal tilt angle to use for 1-Axis trackers.
            efficiency (float, optional): PV Module Efficiency (0.0 to 1.0). Default 0.14.
            
        Returns:
            tuple: (pd.DataFrame, dict) -> (Hourly Data, Annual Totals)
        """
        data = []
        
        # Use provided overrides or defaults
        tilt_fixed = fixed_tilt if fixed_tilt is not None else self.tilt
        azimuth_fixed = fixed_azimuth if fixed_azimuth is not None else self.azimuth
        
        # Tilt for 1-Axis Trackers
        # If optimal_tilt is provided, use it. Otherwise use defaults.
        # Default for 1-Axis Azimuth was abs(latitude)
        # Default for 1-Axis Polar was self.tilt (user input)
        tilt_1axis_az = optimal_tilt if optimal_tilt is not None else abs(self.latitude)
        tilt_1axis_polar = optimal_tilt if optimal_tilt is not None else tilt_fixed

        # Initialize Annual Totals
        annual_yield_horiz = 0
        annual_yield_1axis_az = 0
        annual_yield_1axis_el = 0
        annual_yield_2axis = 0
        annual_yield_fixed = 0
        
        # Loss Totals
        loss_ang_horiz = 0; loss_therm_horiz = 0
        loss_ang_1axis_az = 0; loss_therm_1axis_az = 0
        loss_ang_1axis_el = 0; loss_therm_1axis_el = 0
        loss_ang_2axis = 0; loss_therm_2axis = 0
        loss_ang_fixed = 0; loss_therm_fixed = 0
        
        # Incident Totals
        inc_horiz = 0; inc_1axis_az = 0; inc_1axis_el = 0; inc_2axis = 0; inc_fixed = 0
        
        daylight_hours_count = 0
        
        for day in range(1, 366):
            for hour in range(24):
                # Calculate geometry
                geom = self.calculate_geometry(day, hour)
                
                # Check current hour and next hour to see if this is a transitional hour
                # Include if sun is up at start OR sun is up at end (transitional)
                geom_next = self.calculate_geometry(day, hour + 1)
                
                if geom['elevation'] <= 0 and geom_next['elevation'] <= 0:
                    continue
                
                daylight_hours_count += 1
                
                # Calculate base irradiance (DNI, Diffuse Factor)
                irrad = self.calculate_irradiance(day, geom['elevation'])
                
                # Extract common variables
                beta = geom['elevation']
                phi_s = geom['azimuth']
                Ib = irrad['dni']
                C = irrad['diffuse_factor']
                
                # Calculate ambient temperature for this time step
                T_amb = self.calculate_ambient_temperature(day, hour)
                
                # --- Mode 1: Horizontal ---
                Ic_horiz, cos_theta_horiz = self.calculate_incident_irradiance(beta, phi_s, 0, 0, Ib, C)
                res_horiz = self.calculate_pv_performance(Ic_horiz, cos_theta_horiz, T_amb=T_amb, efficiency=efficiency)
                
                # --- Mode 2: 1-Axis Azimuth Tracking ---
                # Uses tilt_1axis_az
                sigma_az_track = tilt_1axis_az
                phi_c_az_track = phi_s
                Ic_1axis_az, cos_theta_1axis_az = self.calculate_incident_irradiance(beta, phi_s, sigma_az_track, phi_c_az_track, Ib, C)
                res_1axis_az = self.calculate_pv_performance(Ic_1axis_az, cos_theta_1axis_az, T_amb=T_amb, efficiency=efficiency)
                
                # --- Mode 3: 1-Axis Elevation Tracking ---
                # Tracker rotates on E-W axis, tilting N-S to track elevation.
                
                delta = geom['declination']
                
                # Determine panel orientation based on latitude and declination
                if abs(self.latitude) >= 23.45:
                    # Outside tropics: Always face equator
                    phi_c_el_track = 0 if self.latitude < 0 else 180
                elif abs(self.latitude) < 0.1:
                    # At or very near equator: Always face North to avoid equinox flips
                    # (Sun passes overhead at equinoxes, orientation doesn't matter much)
                    phi_c_el_track = 0
                else:
                    # Inside tropics (but not at equator): Determine from declination
                    if self.latitude < 0:
                        # Southern Hemisphere
                        if delta > 0 and abs(delta) > abs(self.latitude):
                            phi_c_el_track = 0  # Sun in Northern sky → Face North
                        else:
                            phi_c_el_track = 180  # Sun in Southern sky → Face South
                    else:
                        # Northern Hemisphere
                        if delta < 0 and abs(delta) > abs(self.latitude):
                            phi_c_el_track = 180  # Sun in Southern sky → Face South
                        else:
                            phi_c_el_track = 0  # Sun in Northern sky → Face North
                
                # Panel tilt tracks the complement of elevation angle
                sigma_el_track = 90 - beta
                
                Ic_1axis_el, cos_theta_1axis_el = self.calculate_incident_irradiance(beta, phi_s, sigma_el_track, phi_c_el_track, Ib, C)
                res_1axis_el = self.calculate_pv_performance(Ic_1axis_el, cos_theta_1axis_el, T_amb=T_amb, efficiency=efficiency)
                
                # --- Mode 4: 2-Axis Tracking ---
                # Panel always points directly at the sun
                # Beam irradiance: Ic_beam = DNI (since cos(theta) = 1)
                Ibc_2axis = Ib 
                
                # Diffuse and ground-reflected irradiance
                # When panel points at sun: sigma (panel tilt from horizontal) = 90 - beta
                # cos(sigma) = cos(90 - beta) = sin(beta)
                # For diffuse: (1 + cos(sigma))/2 = (1 + sin(beta))/2
                # For ground-reflected: (1 - cos(sigma))/2 = (1 - sin(beta))/2
                
                sin_beta = np.sin(np.radians(beta))
                Idc_2axis = C * Ib * (1 + sin_beta) / 2
                Irc_2axis = 0.2 * Ib * (sin_beta + C) * (1 - sin_beta) / 2
                Ic_2axis = Ibc_2axis + Idc_2axis + Irc_2axis
                
                # For 2-axis, cos_theta is always 1 (perfect tracking)
                res_2axis = self.calculate_pv_performance(Ic_2axis, 1.0, T_amb=T_amb, efficiency=efficiency)
                
                # --- Mode 5: 1-Axis Polar (Hour Angle) Tracking ---
                # User Inputs:
                # 'fixed_tilt': The tilt of the ROTATION AXIS from the horizontal.
                # 'fixed_azimuth': The azimuth the PANEL faces at solar noon.
                
                # 1. Determine Axis Tilt
                # If not provided, default to Latitude (standard polar mount).
                axis_tilt_polar = tilt_1axis_polar
                
                # 2. Determine Axis Azimuth
                # The Axis is the line the panel rotates around.
                # For a polar mount, the Axis points towards the Celestial Pole.
                # The Panel is mounted perpendicular to the Axis (or declination adjusted).
                # At Noon, the Panel faces the Equator (Sun).
                # Therefore, the Axis Azimuth is 180 degrees opposite to the Panel Azimuth.
                # Example S. Hem: Panel faces North (0) -> Axis points South (180).
                # Example N. Hem: Panel faces South (180) -> Axis points North (0).
                
                if fixed_azimuth is not None:
                    panel_azimuth_noon = fixed_azimuth
                    axis_azimuth_polar = panel_azimuth_noon + 180
                else:
                    # Default defaults
                    if self.latitude < 0:
                        panel_azimuth_noon = 0 # North
                        axis_azimuth_polar = 180 # South
                    else:
                        panel_azimuth_noon = 180 # South
                        axis_azimuth_polar = 0 # North
                
                # 3. Calculate Axis Vector k
                # Azimuth is from North (y) towards East (x).
                az_rad = np.radians(axis_azimuth_polar)
                tilt_rad = np.radians(axis_tilt_polar)
                
                k_x = np.cos(tilt_rad) * np.sin(az_rad)
                k_y = np.cos(tilt_rad) * np.cos(az_rad)
                k_z = np.sin(tilt_rad)
                
                # 4. Calculate Noon Normal Vector n0
                # This is the direction the panel faces at solar noon (Hour Angle = 0).
                # It is determined by the User's 'fixed_azimuth' (Panel Azimuth).
                # The Tilt of the normal is complementary to the Axis Tilt (90 - Axis Tilt).
                
                n0_az_rad = np.radians(panel_azimuth_noon)
                n0_tilt_rad = np.pi/2 - tilt_rad
                
                n0_x = np.cos(n0_tilt_rad) * np.sin(n0_az_rad)
                n0_y = np.cos(n0_tilt_rad) * np.cos(n0_az_rad)
                n0_z = np.sin(n0_tilt_rad)
                
                # 5. Rotation Angle rho
                # We rotate n0 about k by angle rho.
                # rho depends on the Hour Angle (omega) and the Axis direction.
                # The rotation direction should be such that for positive omega (Morning),
                # the panel turns towards the East.
                
                # Let's define a reference "East" vector e = (1, 0, 0).
                # The rotation of the normal vector n0 around k should move it towards e in the morning.
                # Or simpler:
                # The angular velocity vector w points along the Earth's axis (North).
                # w_earth = (0, cos(lat), sin(lat)) for N. Hem? No, Earth axis is North-South.
                # Let's stick to the tracker axis k.
                # If k points generally North (k_y > 0), then right-hand rotation by +omega moves West-to-East?
                # Wait, right hand rule around North axis: Thumb North, Fingers curl West-to-East.
                # So if k points North, +omega rotation is correct.
                # If k points South, we need -omega rotation to match the Earth's rotation.
                
                # We can use the dot product of k with the North Vector (0, 1, 0).
                # projection = k_y.
                # If k_y > 0 (North-ish), rho = omega.
                # If k_y < 0 (South-ish), rho = -omega.
                # But what if k_y = 0 (East-West axis)?
                # Then it's a horizontal E-W tracker.
                # If k points East (1, 0, 0). Right hand rule: Curl Y to Z. South to Up.
                # Morning (Sun East). We want panel to face East.
                # This logic is getting tricky for arbitrary axes.
                
                # Robust Approach:
                # The rotation axis k should be aligned such that it has a "North-pointing" component
                # to use rho = omega.
                # If the user defines an axis that points South, we should invert the rotation.
                # So, sign = sign(dot(k, North)).
                # North = (0, 1, 0). dot = k_y.
                
                omega_rad = np.radians(geom['hour_angle'])
                
                # Use k_y to determine general North/South alignment
                if k_y >= 0:
                    rho_rad = omega_rad
                else:
                    rho_rad = -omega_rad
                
                # Cross product vector v_cross = k x n0
                v_cross_x = k_y * n0_z - k_z * n0_y
                
                # Rotated Normal Vector n_rot
                # n_rot = n0 * cos(rho) + v_cross * sin(rho)
                # x-component:
                n_rot_x = v_cross_x * np.sin(rho_rad)
                # y-component:
                n_rot_y = n0_y * np.cos(rho_rad) 
                # z-component:
                n_rot_z = n0_z * np.cos(rho_rad)
                
                # Convert n_rot to Tilt (beta) and Azimuth (phi)
                # Tilt beta_c = arcsin(n_rot_z)
                # Azimuth phi_c: tan(phi_c) = x / y
                
                # Check for valid tilt (must be >= 0, i.e., facing sky)
                if n_rot_z < 0:
                    # Facing ground. Clamp to horizon or skip?
                    # Tracker usually hits mechanical limit or just points down.
                    # Let's assume it points down (self-shading/backside).
                    # Effectively 0 direct irradiance.
                    beta_c_polar = 0
                    phi_c_polar = 0
                    cos_theta_polar = 0
                    Ic_polar = 0 # Initialize here
                else:
                    beta_c_polar = np.degrees(np.arcsin(n_rot_z))
                    
                    # Azimuth
                    # atan2(x, y) returns angle from y-axis (North) towards x-axis (East)?
                    # Standard atan2(y, x) is from x-axis.
                    # We want Azimuth: 0=North (y), 90=East (x).
                    # So Azimuth = atan2(x, y).
                    phi_c_polar = np.degrees(np.arctan2(n_rot_x, n_rot_y))
                    
                    # Calculate Incidence
                    Ic_polar, cos_theta_polar = self.calculate_incident_irradiance(beta, phi_s, beta_c_polar, phi_c_polar, Ib, C)

                res_polar = self.calculate_pv_performance(Ic_polar, cos_theta_polar, T_amb=T_amb, efficiency=efficiency)
                
                # --- Mode 9: 1-Axis Horizontal (New) ---
                # Axis Tilt = 0. Axis Azimuth = 0 (North-South).
                # Tracks East-West.
                
                axis_tilt_horiz = 0
                # Axis Azimuth same as Polar (N/S)
                axis_azimuth_horiz = axis_azimuth_polar 
                
                # 3. Calculate Axis Vector k_h
                az_rad_h = np.radians(axis_azimuth_horiz)
                tilt_rad_h = np.radians(axis_tilt_horiz)
                
                k_x_h = np.cos(tilt_rad_h) * np.sin(az_rad_h)
                k_y_h = np.cos(tilt_rad_h) * np.cos(az_rad_h)
                k_z_h = np.sin(tilt_rad_h)
                
                # 4. Calculate Noon Normal Vector n0_h
                # Panel Azimuth Noon same as Polar
                n0_az_rad_h = np.radians(panel_azimuth_noon)
                n0_tilt_rad_h = np.pi/2 - tilt_rad_h
                
                n0_x_h = np.cos(n0_tilt_rad_h) * np.sin(n0_az_rad_h)
                n0_y_h = np.cos(n0_tilt_rad_h) * np.cos(n0_az_rad_h)
                n0_z_h = np.sin(n0_tilt_rad_h)
                
                # 5. Rotation Angle rho_h
                # Use same logic: if k points North, rho = omega.
                if k_y_h >= 0:
                    rho_rad_h = omega_rad
                else:
                    rho_rad_h = -omega_rad
                    
                # Cross product v_cross_h = k_h x n0_h
                v_cross_x_h = k_y_h * n0_z_h - k_z_h * n0_y_h
                
                # Rotated Normal n_rot_h
                # n_rot_h = n0_h * cos(rho) + v_cross_h * sin(rho)
                # x-component only needed for Azimuth? No, need all for beta/phi.
                # Actually, simplified:
                n_rot_x_h = v_cross_x_h * np.sin(rho_rad_h)
                n_rot_y_h = n0_y_h * np.cos(rho_rad_h)
                n_rot_z_h = n0_z_h * np.cos(rho_rad_h)
                
                if n_rot_z_h < 0:
                    beta_c_horiz = 0
                    phi_c_horiz = 0
                    cos_theta_horiz = 0
                    Ic_horiz_track = 0
                else:
                    beta_c_horiz = np.degrees(np.arcsin(n_rot_z_h))
                    phi_c_horiz = np.degrees(np.arctan2(n_rot_x_h, n_rot_y_h))
                    
                    Ic_horiz_track, cos_theta_horiz = self.calculate_incident_irradiance(beta, phi_s, beta_c_horiz, phi_c_horiz, Ib, C)
                    
                res_horiz_track = self.calculate_pv_performance(Ic_horiz_track, cos_theta_horiz, T_amb=T_amb, efficiency=efficiency)
                
                # --- Mode 6: Fixed Custom (Optional) ---
                res_fixed = None
                if fixed_tilt is not None and fixed_azimuth is not None:
                    Ic_fixed, cos_theta_fixed = self.calculate_incident_irradiance(beta, phi_s, fixed_tilt, fixed_azimuth, Ib, C)
                    res_fixed = self.calculate_pv_performance(Ic_fixed, cos_theta_fixed, T_amb=T_amb, efficiency=efficiency)
                    
                # --- Mode 7: Fixed East-West (Dual Panel) ---
                # Two panels, both tilted 45 deg.
                # Panel A: Azimuth 90 (East). Panel B: Azimuth 270 (West).
                # System Yield is average of both (assuming 50/50 capacity split).
                
                tilt_ew = 45
                az_e = 90
                az_w = 270
                
                Ic_e, cos_theta_e = self.calculate_incident_irradiance(beta, phi_s, tilt_ew, az_e, Ib, C)
                res_e = self.calculate_pv_performance(Ic_e, cos_theta_e, T_amb=T_amb, efficiency=efficiency)
                
                Ic_w, cos_theta_w = self.calculate_incident_irradiance(beta, phi_s, tilt_ew, az_w, Ib, C)
                res_w = self.calculate_pv_performance(Ic_w, cos_theta_w, T_amb=T_amb, efficiency=efficiency)
                
                # Average for System Stats (per m2 of installed capacity)
                Ic_ew = (Ic_e + Ic_w) / 2
                P_ew = (res_e['P_out'] + res_w['P_out']) / 2
                Loss_Ang_ew = (res_e['Loss_Angular'] + res_w['Loss_Angular']) / 2
                Loss_Therm_ew = (res_e['Loss_Thermal'] + res_w['Loss_Thermal']) / 2
                
                # --- Mode 8: Fixed North-South (Dual Panel) ---
                # Two panels, both tilted 45 deg.
                # Panel A: Azimuth 0 (North). Panel B: Azimuth 180 (South).
                
                tilt_ns = 45
                az_n = 0
                az_s = 180
                
                Ic_n, cos_theta_n = self.calculate_incident_irradiance(beta, phi_s, tilt_ns, az_n, Ib, C)
                res_n = self.calculate_pv_performance(Ic_n, cos_theta_n, T_amb=T_amb, efficiency=efficiency)
                
                Ic_s, cos_theta_s = self.calculate_incident_irradiance(beta, phi_s, tilt_ns, az_s, Ib, C)
                res_s = self.calculate_pv_performance(Ic_s, cos_theta_s, T_amb=T_amb, efficiency=efficiency)
                
                # Average for System Stats
                Ic_ns = (Ic_n + Ic_s) / 2
                P_ns = (res_n['P_out'] + res_s['P_out']) / 2
                Loss_Ang_ns = (res_n['Loss_Angular'] + res_s['Loss_Angular']) / 2
                Loss_Therm_ns = (res_n['Loss_Thermal'] + res_s['Loss_Thermal']) / 2
                
                row = {
                    'Day': day,
                    'Hour': hour,
                    'Declination_deg': geom['declination'],
                    'HourAngle_deg': geom['hour_angle'],
                    'Elevation_deg': geom['elevation'],
                    'Azimuth_deg': geom['azimuth'],
                    'DNI_W_m2': Ib,
                    'GHI_W_m2': irrad['global_horizontal'],
                    
                    # Temperature
                    'T_amb': T_amb,
                    'T_cell_Horiz': res_horiz['T_cell'],
                    'T_cell_1Axis_Az': res_1axis_az['T_cell'],
                    'T_cell_1Axis_Polar': res_polar['T_cell'],
                    'T_cell_1Axis_Horiz': res_horiz_track['T_cell'],
                    'T_cell_1Axis_El': res_1axis_el['T_cell'],
                    'T_cell_2Axis': res_2axis['T_cell'],
                    'T_cell_Fixed_EW': (res_e['T_cell'] + res_w['T_cell']) / 2,
                    'T_cell_Fixed_NS': (res_n['T_cell'] + res_s['T_cell']) / 2,
                    
                    # Irradiance
                    'I_Horizontal_W_m2': Ic_horiz,
                    'I_1Axis_Azimuth_W_m2': Ic_1axis_az,
                    'I_1Axis_Polar_W_m2': Ic_polar,
                    'I_1Axis_Horizontal_W_m2': Ic_horiz_track,
                    'I_1Axis_Elevation_W_m2': Ic_1axis_el,
                    'I_2Axis_W_m2': Ic_2axis,
                    'I_Fixed_EW_W_m2': Ic_ew,
                    'I_Fixed_NS_W_m2': Ic_ns,
                    
                    # PV Power
                    'P_Horiz': res_horiz['P_out'],
                    'P_1Axis_Az': res_1axis_az['P_out'],
                    'P_1Axis_Polar': res_polar['P_out'],
                    'P_1Axis_Horiz': res_horiz_track['P_out'],
                    'P_1Axis_El': res_1axis_el['P_out'],
                    'P_2Axis': res_2axis['P_out'],
                    'P_Fixed_EW': P_ew,
                    'P_Fixed_NS': P_ns,
                    
                    # PV Power at 25°C (theoretical with active cooling)
                    'P_Horiz_25C': res_horiz['P_at_25C'],
                    'P_1Axis_Az_25C': res_1axis_az['P_at_25C'],
                    'P_1Axis_Polar_25C': res_polar['P_at_25C'],
                    'P_1Axis_Horiz_25C': res_horiz_track['P_at_25C'],
                    'P_1Axis_El_25C': res_1axis_el['P_at_25C'],
                    'P_2Axis_25C': res_2axis['P_at_25C'],
                    'P_Fixed_EW_25C': (res_e['P_at_25C'] + res_w['P_at_25C']) / 2,
                    'P_Fixed_NS_25C': (res_n['P_at_25C'] + res_s['P_at_25C']) / 2,
                    
                    # Angular Losses (Irradiance W/m2)
                    'Loss_Ang_Horiz_W_m2': res_horiz['Loss_Angular'],
                    'Loss_Ang_1Axis_Az_W_m2': res_1axis_az['Loss_Angular'],
                    'Loss_Ang_1Axis_Polar_W_m2': res_polar['Loss_Angular'],
                    'Loss_Ang_1Axis_Horizontal_W_m2': res_horiz_track['Loss_Angular'],
                    'Loss_Ang_1Axis_El_W_m2': res_1axis_el['Loss_Angular'],
                    'Loss_Ang_2Axis_W_m2': res_2axis['Loss_Angular'],
                    'Loss_Ang_Fixed_EW_W_m2': Loss_Ang_ew,
                    'Loss_Ang_Fixed_NS_W_m2': Loss_Ang_ns,
                    
                    # Thermal Losses (Power W/m2)
                    'Loss_Therm_Horiz_W_m2': res_horiz['Loss_Thermal'],
                    'Loss_Therm_1Axis_Az_W_m2': res_1axis_az['Loss_Thermal'],
                    'Loss_Therm_1Axis_Polar_W_m2': res_polar['Loss_Thermal'],
                    'Loss_Therm_1Axis_Horizontal_W_m2': res_horiz_track['Loss_Thermal'],
                    'Loss_Therm_1Axis_El_W_m2': res_1axis_el['Loss_Thermal'],
                    'Loss_Therm_2Axis_W_m2': res_2axis['Loss_Thermal'],
                    'Loss_Therm_Fixed_EW_W_m2': Loss_Therm_ew,
                    'Loss_Therm_Fixed_NS_W_m2': Loss_Therm_ns
                }
                
                # Add Fixed Custom data if calculated
                if res_fixed:
                    row.update({
                        'I_Fixed_W_m2': Ic_fixed,
                        'T_cell_Fixed': res_fixed['T_cell'],
                        'P_Fixed': res_fixed['P_out'],
                        'P_Fixed_25C': res_fixed['P_at_25C'],
                        'Loss_Ang_Fixed_W_m2': res_fixed['Loss_Angular'],
                        'Loss_Therm_Fixed_W_m2': res_fixed['Loss_Thermal'],
                    })
                
                data.append(row)
                
        df = pd.DataFrame(data)
        
        # Calculate Annual Totals (kWh/m2)
        annual_2axis_yield = df['P_2Axis'].sum() / 1000
        
        totals = {
            'Annual_GHI_Total_kWh_m2': df['GHI_W_m2'].sum() / 1000,
            'Annual_DNI_Total_kWh_m2': df['DNI_W_m2'].sum() / 1000,
            
            # Irradiance Totals
            'Annual_I_Horizontal_kWh_m2': df['I_Horizontal_W_m2'].sum() / 1000,
            'Annual_I_1Axis_Azimuth_kWh_m2': df['I_1Axis_Azimuth_W_m2'].sum() / 1000,
            'Annual_I_1Axis_Polar_kWh_m2': df['I_1Axis_Polar_W_m2'].sum() / 1000,
            'Annual_I_1Axis_Horizontal_kWh_m2': df['I_1Axis_Horizontal_W_m2'].sum() / 1000,
            'Annual_I_1Axis_Elevation_kWh_m2': df['I_1Axis_Elevation_W_m2'].sum() / 1000,
            'Annual_I_2Axis_kWh_m2': df['I_2Axis_W_m2'].sum() / 1000,
            'Annual_I_Fixed_EW_kWh_m2': df['I_Fixed_EW_W_m2'].sum() / 1000,
            'Annual_I_Fixed_NS_kWh_m2': df['I_Fixed_NS_W_m2'].sum() / 1000,
            
            # Yield Totals
            'Annual_Yield_Horizontal_kWh_m2': df['P_Horiz'].sum() / 1000,
            'Annual_Yield_1Axis_Azimuth_kWh_m2': df['P_1Axis_Az'].sum() / 1000,
            'Annual_Yield_1Axis_Polar_kWh_m2': df['P_1Axis_Polar'].sum() / 1000,
            'Annual_Yield_1Axis_Horizontal_kWh_m2': df['P_1Axis_Horiz'].sum() / 1000,
            'Annual_Yield_1Axis_Elevation_kWh_m2': df['P_1Axis_El'].sum() / 1000,
            'Annual_Yield_2Axis_kWh_m2': annual_2axis_yield,
            'Annual_Yield_Fixed_EW_kWh_m2': df['P_Fixed_EW'].sum() / 1000,
            'Annual_Yield_Fixed_NS_kWh_m2': df['P_Fixed_NS'].sum() / 1000,
            
            # Cooled Yield Totals (at 25°C - theoretical with active cooling)
            'Annual_Yield_Cooled_Horizontal_kWh_m2': df['P_Horiz_25C'].sum() / 1000,
            'Annual_Yield_Cooled_1Axis_Azimuth_kWh_m2': df['P_1Axis_Az_25C'].sum() / 1000,
            'Annual_Yield_Cooled_1Axis_Polar_kWh_m2': df['P_1Axis_Polar_25C'].sum() / 1000,
            'Annual_Yield_Cooled_1Axis_Horizontal_kWh_m2': df['P_1Axis_Horiz_25C'].sum() / 1000,
            'Annual_Yield_Cooled_1Axis_Elevation_kWh_m2': df['P_1Axis_El_25C'].sum() / 1000,
            'Annual_Yield_Cooled_2Axis_kWh_m2': df['P_2Axis_25C'].sum() / 1000,
            'Annual_Yield_Cooled_Fixed_EW_kWh_m2': df['P_Fixed_EW_25C'].sum() / 1000,
            'Annual_Yield_Cooled_Fixed_NS_kWh_m2': df['P_Fixed_NS_25C'].sum() / 1000,
            
            # Annual Losses (Angular - Irradiance kWh/m2)
            'Annual_Loss_Ang_Horiz_kWh_m2': df['Loss_Ang_Horiz_W_m2'].sum() / 1000,
            'Annual_Loss_Ang_1Axis_Az_kWh_m2': df['Loss_Ang_1Axis_Az_W_m2'].sum() / 1000,
            'Annual_Loss_Ang_1Axis_Polar_kWh_m2': df['Loss_Ang_1Axis_Polar_W_m2'].sum() / 1000,
            'Annual_Loss_Ang_1Axis_Horizontal_kWh_m2': df['Loss_Ang_1Axis_Horizontal_W_m2'].sum() / 1000,
            'Annual_Loss_Ang_1Axis_El_kWh_m2': df['Loss_Ang_1Axis_El_W_m2'].sum() / 1000,
            'Annual_Loss_Ang_2Axis_kWh_m2': df['Loss_Ang_2Axis_W_m2'].sum() / 1000,
            'Annual_Loss_Ang_Fixed_EW_kWh_m2': df['Loss_Ang_Fixed_EW_W_m2'].sum() / 1000,
            'Annual_Loss_Ang_Fixed_NS_kWh_m2': df['Loss_Ang_Fixed_NS_W_m2'].sum() / 1000,
            
            # Annual Losses (Thermal - Power kWh/m2)
            'Annual_Loss_Therm_Horiz_kWh_m2': df['Loss_Therm_Horiz_W_m2'].sum() / 1000,
            'Annual_Loss_Therm_1Axis_Az_kWh_m2': df['Loss_Therm_1Axis_Az_W_m2'].sum() / 1000,
            'Annual_Loss_Therm_1Axis_Polar_kWh_m2': df['Loss_Therm_1Axis_Polar_W_m2'].sum() / 1000,
            'Annual_Loss_Therm_1Axis_Horizontal_kWh_m2': df['Loss_Therm_1Axis_Horizontal_W_m2'].sum() / 1000,
            'Annual_Loss_Therm_1Axis_El_kWh_m2': df['Loss_Therm_1Axis_El_W_m2'].sum() / 1000,
            'Annual_Loss_Therm_2Axis_kWh_m2': df['Loss_Therm_2Axis_W_m2'].sum() / 1000,
            'Annual_Loss_Therm_Fixed_EW_kWh_m2': df['Loss_Therm_Fixed_EW_W_m2'].sum() / 1000,
            'Annual_Loss_Therm_Fixed_NS_kWh_m2': df['Loss_Therm_Fixed_NS_W_m2'].sum() / 1000,
            
            # Performance Ratios
            'Ratio_Yield_Horizontal_vs_2Axis_Percent': (df['P_Horiz'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0,
            'Ratio_Yield_1Axis_Azimuth_vs_2Axis_Percent': (df['P_1Axis_Az'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0,
            'Ratio_Yield_1Axis_Polar_vs_2Axis_Percent': (df['P_1Axis_Polar'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0,
            'Ratio_Yield_1Axis_Elevation_vs_2Axis_Percent': (df['P_1Axis_El'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0,
            'Ratio_Yield_Fixed_vs_2Axis_Percent': (df['P_Fixed'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0,
            'Ratio_Yield_Fixed_EW_vs_2Axis_Percent': (df['P_Fixed_EW'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0,
            'Ratio_Yield_Fixed_NS_vs_2Axis_Percent': (df['P_Fixed_NS'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0
        }
        
        # Add Fixed Custom Totals if calculated
        if fixed_tilt is not None:
            totals['Annual_I_Fixed_kWh_m2'] = df['I_Fixed_W_m2'].sum() / 1000
            totals['Annual_Yield_Fixed_kWh_m2'] = df['P_Fixed'].sum() / 1000
            totals['Annual_Loss_Ang_Fixed_kWh_m2'] = df['Loss_Ang_Fixed_W_m2'].sum() / 1000
            totals['Annual_Loss_Therm_Fixed_kWh_m2'] = df['Loss_Therm_Fixed_W_m2'].sum() / 1000
            totals['Ratio_Yield_Fixed_vs_2Axis_Percent'] = (df['P_Fixed'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0
            totals['Annual_Yield_Cooled_Fixed_kWh_m2'] = df['P_Fixed_25C'].sum() / 1000
        
        # Capacity Factors
        # Rated Power (kW/m2) = efficiency (since STC is 1 kW/m2)
        rated_power_kw_m2 = efficiency
        total_hours = 8760
        
        def calc_cf(yield_val, hours):
            if hours > 0 and rated_power_kw_m2 > 0:
                return (yield_val / (rated_power_kw_m2 * hours)) * 100
            return 0.0

        # Overall CF (8760h)
        totals['CF_Overall_Horizontal'] = calc_cf(totals['Annual_Yield_Horizontal_kWh_m2'], total_hours)
        totals['CF_Overall_1Axis_Azimuth'] = calc_cf(totals['Annual_Yield_1Axis_Azimuth_kWh_m2'], total_hours)
        totals['CF_Overall_1Axis_Polar'] = calc_cf(totals['Annual_Yield_1Axis_Polar_kWh_m2'], total_hours)
        totals['CF_Overall_1Axis_Horizontal'] = calc_cf(totals['Annual_Yield_1Axis_Horizontal_kWh_m2'], total_hours)
        totals['CF_Overall_1Axis_Elevation'] = calc_cf(totals['Annual_Yield_1Axis_Elevation_kWh_m2'], total_hours)
        totals['CF_Overall_Fixed'] = calc_cf(totals['Annual_Yield_Fixed_kWh_m2'], total_hours)
        totals['CF_Overall_2Axis'] = calc_cf(totals['Annual_Yield_2Axis_kWh_m2'], total_hours)
        totals['CF_Overall_Fixed_EW'] = calc_cf(totals['Annual_Yield_Fixed_EW_kWh_m2'], total_hours)
        totals['CF_Overall_Fixed_NS'] = calc_cf(totals['Annual_Yield_Fixed_NS_kWh_m2'], total_hours)
        
        # Daylight CF
        totals['CF_Daylight_Horizontal'] = calc_cf(totals['Annual_Yield_Horizontal_kWh_m2'], daylight_hours_count)
        totals['CF_Daylight_1Axis_Azimuth'] = calc_cf(totals['Annual_Yield_1Axis_Azimuth_kWh_m2'], daylight_hours_count)
        totals['CF_Daylight_1Axis_Polar'] = calc_cf(totals['Annual_Yield_1Axis_Polar_kWh_m2'], daylight_hours_count)
        totals['CF_Daylight_1Axis_Horizontal'] = calc_cf(totals['Annual_Yield_1Axis_Horizontal_kWh_m2'], daylight_hours_count)
        totals['CF_Daylight_1Axis_Elevation'] = calc_cf(totals['Annual_Yield_1Axis_Elevation_kWh_m2'], daylight_hours_count)
        totals['CF_Daylight_Fixed'] = calc_cf(totals['Annual_Yield_Fixed_kWh_m2'], daylight_hours_count)
        totals['CF_Daylight_2Axis'] = calc_cf(totals['Annual_Yield_2Axis_kWh_m2'], daylight_hours_count)
        totals['CF_Daylight_Fixed_EW'] = calc_cf(totals['Annual_Yield_Fixed_EW_kWh_m2'], daylight_hours_count)
        totals['CF_Daylight_Fixed_NS'] = calc_cf(totals['Annual_Yield_Fixed_NS_kWh_m2'], daylight_hours_count)
        
        totals['Daylight_Hours'] = daylight_hours_count

        return df, totals

    def save_results(self, df, totals, filename='solar_model_output.csv'):
        """
        Save results to a single CSV file with a summary header.
        """
        with open(filename, 'w', newline='') as f:
            # 1. Write Annual Totals Section
            f.write("ANNUAL SUMMARY STATS\n")
            # Convert totals dict to a simple DataFrame for easy CSV string creation
            totals_df = pd.DataFrame(list(totals.items()), columns=['Metric', 'Value'])
            totals_df.to_csv(f, index=False)
            
            # 2. Spacer
            f.write("\nHOURLY DATA\n")
            
            # 3. Write Hourly Data
            df.to_csv(f, index=False)

    def get_summary_stats(self, totals):
        """
        Return key stats for display.
        """
        return {
            'annual_yield_horiz': totals['Annual_Yield_Horizontal_kWh_m2'],
            'annual_yield_1axis_az': totals['Annual_Yield_1Axis_Azimuth_kWh_m2'],
            'annual_yield_1axis_polar': totals['Annual_Yield_1Axis_Polar_kWh_m2'],
            'annual_yield_1axis_el': totals['Annual_Yield_1Axis_Elevation_kWh_m2'],
            'annual_yield_2axis': totals['Annual_Yield_2Axis_kWh_m2']
        }

if __name__ == "__main__":
    # Test Case: Perth (Approximate location from thesis)
    # Latitude: -32.05, Longitude: 115.89
    model = SolarModel(latitude=-32.05, longitude=115.89)
    
    print("Generating annual profile with PV performance...")
    df, totals = model.generate_annual_profile()
    
    print("\nCalculating summary statistics...")
    stats = model.get_summary_stats(totals)
    
    print(f"\nAnnual PV Energy Yields (kWh/m2):")
    print(f"  Horizontal:       {stats['annual_yield_horiz']:.2f}")
    print(f"  1-Axis Azimuth:   {stats['annual_yield_1axis_az']:.2f}")
    print(f"  1-Axis Elevation: {stats['annual_yield_1axis_el']:.2f}")
    print(f"  2-Axis:           {stats['annual_yield_2axis']:.2f}")
    
    # Save to CSV
    model.save_results(df, totals, 'solar_model_output.csv')
    print("\nResults saved to solar_model_output.csv (Summary + Hourly Data)")
