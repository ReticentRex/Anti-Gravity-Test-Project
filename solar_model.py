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
        delta_deg = 23.45 * np.sin(np.radians(360/365 * (n - 81)))
        delta_rad = np.radians(delta_deg)
        
        # 2. Equation of Time (E) [Eq 4, 4.1]
        B_deg = 360/364 * (n - 81)
        B_rad = np.radians(B_deg)
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
                
            if np.cos(H_rad) < check_val:
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
        A = 1160 + 75 * np.sin(np.radians(360/365 * (n - 275)))
        
        # 2. Optical Depth (k) [Eq 10]
        k = 0.174 + 0.035 * np.sin(np.radians(360/365 * (n - 100)))
        
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
        C = 0.095 + 0.04 * np.sin(np.radians(360/365 * (n - 100)))
        
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

    def calculate_pv_performance(self, Ic, cos_theta, T_amb=25):
        """
        Calculate PV Power Output and Losses.
        
        Args:
            Ic (float): Total Incident Irradiance (W/m2)
            cos_theta (float): Cosine of Angle of Incidence
            T_amb (float): Ambient Temperature (C)
            
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
        EFF_STC = 0.14 # Efficiency at STC (14%)
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
            'Loss_Angular': max(0, Loss_Angular),
            'Loss_Thermal': Loss_Thermal 
        }

    def generate_annual_profile(self):
        """
        Generate hourly solar profile for the entire year.
        Calculates irradiance, PV Power, and Losses for 4 collector orientations.
        
        Returns:
            pd.DataFrame: Hourly data
        """
        data = []
        
        for day in range(1, 366):
            for hour in range(24):
                # Calculate geometry
                geom = self.calculate_geometry(day, hour)
                
                # Skip if sun is below horizon (Night time)
                if geom['elevation'] <= 0:
                    continue
                
                # Calculate base irradiance (DNI, Diffuse Factor)
                irrad = self.calculate_irradiance(day, geom['elevation'])
                
                # Extract common variables
                beta = geom['elevation']
                phi_s = geom['azimuth']
                Ib = irrad['dni']
                C = irrad['diffuse_factor']
                
                # --- Mode 1: Horizontal ---
                Ic_horiz, cos_theta_horiz = self.calculate_incident_irradiance(beta, phi_s, 0, 0, Ib, C)
                res_horiz = self.calculate_pv_performance(Ic_horiz, cos_theta_horiz)
                
                # --- Mode 2: 1-Axis Azimuth Tracking ---
                sigma_az_track = abs(self.latitude)
                phi_c_az_track = phi_s
                Ic_1axis_az, cos_theta_1axis_az = self.calculate_incident_irradiance(beta, phi_s, sigma_az_track, phi_c_az_track, Ib, C)
                res_1axis_az = self.calculate_pv_performance(Ic_1axis_az, cos_theta_1axis_az)
                
                # --- Mode 3: 1-Axis Elevation Tracking ---
                phi_c_el_track = 0 # Facing North
                sigma_el_track = 90 - beta
                Ic_1axis_el, cos_theta_1axis_el = self.calculate_incident_irradiance(beta, phi_s, sigma_el_track, phi_c_el_track, Ib, C)
                res_1axis_el = self.calculate_pv_performance(Ic_1axis_el, cos_theta_1axis_el)
                
                # --- Mode 4: 2-Axis Tracking ---
                sigma_2axis = 90 - beta
                Ibc_2axis = Ib 
                Idc_2axis = C * Ib * (1 + np.cos(np.radians(sigma_2axis))) / 2
                Irc_2axis = 0.2 * Ib * (np.sin(np.radians(beta)) + C) * (1 - np.cos(np.radians(sigma_2axis))) / 2
                Ic_2axis = Ibc_2axis + Idc_2axis + Irc_2axis
                
                # For 2-axis, cos_theta is always 1 (perfect tracking)
                res_2axis = self.calculate_pv_performance(Ic_2axis, 1.0)
                
                row = {
                    'Day': day,
                    'Hour': hour,
                    'Declination_deg': geom['declination'],
                    'HourAngle_deg': geom['hour_angle'],
                    'Elevation_deg': geom['elevation'],
                    'Azimuth_deg': geom['azimuth'],
                    'DNI_W_m2': Ib,
                    'GHI_W_m2': irrad['global_horizontal'],
                    
                    # Irradiance
                    'I_Horizontal_W_m2': Ic_horiz,
                    'I_1Axis_Azimuth_W_m2': Ic_1axis_az,
                    'I_1Axis_Elevation_W_m2': Ic_1axis_el,
                    'I_2Axis_W_m2': Ic_2axis,
                    
                    # PV Power
                    'P_Horizontal_W_m2': res_horiz['P_out'],
                    'P_1Axis_Azimuth_W_m2': res_1axis_az['P_out'],
                    'P_1Axis_Elevation_W_m2': res_1axis_el['P_out'],
                    'P_2Axis_W_m2': res_2axis['P_out'],
                    
                    # Angular Losses (Irradiance W/m2)
                    'Loss_Ang_Horiz_W_m2': res_horiz['Loss_Angular'],
                    'Loss_Ang_1Axis_Az_W_m2': res_1axis_az['Loss_Angular'],
                    'Loss_Ang_1Axis_El_W_m2': res_1axis_el['Loss_Angular'],
                    'Loss_Ang_2Axis_W_m2': res_2axis['Loss_Angular'],
                    
                    # Thermal Losses (Power W/m2)
                    'Loss_Therm_Horiz_W_m2': res_horiz['Loss_Thermal'],
                    'Loss_Therm_1Axis_Az_W_m2': res_1axis_az['Loss_Thermal'],
                    'Loss_Therm_1Axis_El_W_m2': res_1axis_el['Loss_Thermal'],
                    'Loss_Therm_2Axis_W_m2': res_2axis['Loss_Thermal']
                }
                data.append(row)
                
        df = pd.DataFrame(data)
        
        # Calculate Annual Totals (kWh/m2)
        annual_2axis_yield = df['P_2Axis_W_m2'].sum() / 1000
        
        totals = {
            'Annual_GHI_Total_kWh_m2': df['GHI_W_m2'].sum() / 1000,
            'Annual_DNI_Total_kWh_m2': df['DNI_W_m2'].sum() / 1000,
            
            # Irradiance Totals
            'Annual_I_Horizontal_kWh_m2': df['I_Horizontal_W_m2'].sum() / 1000,
            'Annual_I_1Axis_Azimuth_kWh_m2': df['I_1Axis_Azimuth_W_m2'].sum() / 1000,
            'Annual_I_1Axis_Elevation_kWh_m2': df['I_1Axis_Elevation_W_m2'].sum() / 1000,
            'Annual_I_2Axis_kWh_m2': df['I_2Axis_W_m2'].sum() / 1000,
            
            # PV Energy Yield Totals
            'Annual_Yield_Horizontal_kWh_m2': df['P_Horizontal_W_m2'].sum() / 1000,
            'Annual_Yield_1Axis_Azimuth_kWh_m2': df['P_1Axis_Azimuth_W_m2'].sum() / 1000,
            'Annual_Yield_1Axis_Elevation_kWh_m2': df['P_1Axis_Elevation_W_m2'].sum() / 1000,
            'Annual_Yield_2Axis_kWh_m2': annual_2axis_yield,
            
            # Annual Losses (Angular - Irradiance kWh/m2)
            'Annual_Loss_Ang_Horiz_kWh_m2': df['Loss_Ang_Horiz_W_m2'].sum() / 1000,
            'Annual_Loss_Ang_1Axis_Az_kWh_m2': df['Loss_Ang_1Axis_Az_W_m2'].sum() / 1000,
            'Annual_Loss_Ang_1Axis_El_kWh_m2': df['Loss_Ang_1Axis_El_W_m2'].sum() / 1000,
            'Annual_Loss_Ang_2Axis_kWh_m2': df['Loss_Ang_2Axis_W_m2'].sum() / 1000,
            
            # Annual Losses (Thermal - Power kWh/m2)
            'Annual_Loss_Therm_Horiz_kWh_m2': df['Loss_Therm_Horiz_W_m2'].sum() / 1000,
            'Annual_Loss_Therm_1Axis_Az_kWh_m2': df['Loss_Therm_1Axis_Az_W_m2'].sum() / 1000,
            'Annual_Loss_Therm_1Axis_El_kWh_m2': df['Loss_Therm_1Axis_El_W_m2'].sum() / 1000,
            'Annual_Loss_Therm_2Axis_kWh_m2': df['Loss_Therm_2Axis_W_m2'].sum() / 1000,
            
            # Performance Ratios
            'Ratio_Yield_Horizontal_vs_2Axis_Percent': (df['P_Horizontal_W_m2'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0,
            'Ratio_Yield_1Axis_Azimuth_vs_2Axis_Percent': (df['P_1Axis_Azimuth_W_m2'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0,
            'Ratio_Yield_1Axis_Elevation_vs_2Axis_Percent': (df['P_1Axis_Elevation_W_m2'].sum() / 1000) / annual_2axis_yield * 100 if annual_2axis_yield > 0 else 0
        }
        
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
