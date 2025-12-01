def calculate_optimal_tilt_1axis_azimuth(self, efficiency=0.2, optimize_electrical=False):
    """
    Calculates optimal tilt for 1-Axis Azimuth Tracker specifically.
    Fixed tilt, rotating azimuth following the sun.
    
    Args:
        efficiency: PV module efficiency
        optimize_electrical: If True, maximizes electrical yield. If False, maximizes irradiance.
    
    Returns: (optimal_tilt, max_yield_kwh_m2)
    """
    # Pre-calculate solar geometry
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
    end_tilt = int(lat_abs) + 6
    
    for tilt in range(start_tilt, end_tilt):
        total_value = 0
        
        for data in daylight_data:
            # 1-Axis Azimuth: Fixed tilt, azimuth follows sun
            phi_c = data['phi_s']  # Panel azimuth matches sun azimuth
            
            Ic, cos_theta = self.calculate_incident_irradiance(
                data['beta'], data['phi_s'],
                tilt, phi_c,
                data['Ib'], data['C']
            )
            
            if optimize_electrical:
                pv_result = self.calculate_pv_performance(Ic, cos_theta, T_amb=data['T_amb'], efficiency=efficiency)
                total_value += (pv_result['P_out'] / 1000.0)
            else:
                total_value += (Ic / 1000.0)
        
        if total_value > max_optimization_value:
            max_optimization_value = total_value
            best_tilt = tilt
    
    # Calculate electrical yield at optimal tilt
    total_electrical_yield = 0
    for data in daylight_data:
        phi_c = data['phi_s']
        Ic, cos_theta = self.calculate_incident_irradiance(
            data['beta'], data['phi_s'],
            best_tilt, phi_c,
            data['Ib'], data['C']
        )
        pv_result = self.calculate_pv_performance(Ic, cos_theta, T_amb=data['T_amb'], efficiency=efficiency)
        total_electrical_yield += (pv_result['P_out'] / 1000.0)
    
    return best_tilt, total_electrical_yield

def calculate_optimal_tilt_1axis_polar(self, efficiency=0.2, optimize_electrical=False):
    """
    Calculates optimal axis tilt for 1-Axis Polar Tracker.
    Axis tilted at this angle, panel rotates around it following hour angle.
    
    Note: For polar trackers, the "tilt" is the axis tilt angle (typically = latitude).
    This function searches for the best axis tilt.
    
    Args:
        efficiency: PV module efficiency
        optimize_electrical: If True, maximizes electrical yield. If False, maximizes irradiance.
    
    Returns: (optimal_axis_tilt, max_yield_kwh_m2)
    """
    # Pre-calculate solar geometry
    daylight_data = []
    for day in range(1, 366):
        for hour in range(24):
            geom = self.calculate_geometry(day, hour)
            if geom['elevation'] <= 0: continue
            
            irrad = self.calculate_irradiance(day, geom['elevation'])
            T_amb = self.calculate_ambient_temperature(day, hour)
            
            daylight_data.append({
                'day': day,
                'hour': hour,
                'H_deg': geom['hour_angle'],
                'beta': geom['elevation'],
                'phi_s': geom['azimuth'],
                'Ib': irrad['dni'],
                'C': irrad['diffuse_factor'],
                'T_amb': T_amb
            })
    
    best_axis_tilt = 0
    max_optimization_value = 0
    
    # Search range: Latitude +/- 5 degrees
    lat_abs = abs(self.latitude)
    start_tilt = max(0, int(lat_abs) - 5)
    end_tilt = int(lat_abs) + 6
    
    for axis_tilt in range(start_tilt, end_tilt):
        total_value = 0
        
        # Axis azimuth (points to pole)
        axis_azimuth = 180 if self.latitude < 0 else 0
        panel_azimuth_noon = 0 if self.latitude < 0 else 180
        
        for data in daylight_data:
            # Simulate polar tracker panel orientation
            import numpy as np
            
            # Calculate panel orientation using rotation around polar axis
            az_rad = np.radians(axis_azimuth)
            tilt_rad = np.radians(axis_tilt)
            
            k_x = np.cos(tilt_rad) * np.sin(az_rad)
            k_y = np.cos(tilt_rad) * np.cos(az_rad)
            k_z = np.sin(tilt_rad)
            
            n0_az_rad = np.radians(panel_azimuth_noon)
            n0_tilt_rad = np.pi/2 - tilt_rad
            n0_x = np.cos(n0_tilt_rad) * np.sin(n0_az_rad)
            n0_y = np.cos(n0_tilt_rad) * np.cos(n0_az_rad)
            n0_z = np.sin(n0_tilt_rad)
            
            omega_rad = np.radians(data['H_deg'])
            rho_rad = omega_rad if k_y >= 0 else -omega_rad
            
            v_cross_x = k_y * n0_z - k_z * n0_y
            n_rot_x = v_cross_x * np.sin(rho_rad)
            n_rot_y = n0_y * np.cos(rho_rad)
            n_rot_z = n0_z * np.cos(rho_rad)
            
            if n_rot_z < 0:
                continue  # Panel facing down, skip
            
            n_rot_z = np.clip(n_rot_z, -1.0, 1.0)
            sigma_polar = np.degrees(np.arccos(n_rot_z))
            phi_c_polar = np.degrees(np.arctan2(n_rot_x, n_rot_y))
            
            Ic, cos_theta = self.calculate_incident_irradiance(
                data['beta'], data['phi_s'],
                sigma_polar, phi_c_polar,
                data['Ib'], data['C']
            )
            
            if optimize_electrical:
                pv_result = self.calculate_pv_performance(Ic, cos_theta, T_amb=data['T_amb'], efficiency=efficiency)
                total_value += (pv_result['P_out'] / 1000.0)
            else:
                total_value += (Ic / 1000.0)
        
        if total_value > max_optimization_value:
            max_optimization_value = total_value
            best_axis_tilt = axis_tilt
    
    # Calculate electrical yield at optimal axis tilt
    total_electrical_yield = 0
    axis_azimuth = 180 if self.latitude < 0 else 0
    panel_azimuth_noon = 0 if self.latitude < 0 else 180
    
    for data in daylight_data:
        import numpy as np
        
        az_rad = np.radians(axis_azimuth)
        tilt_rad = np.radians(best_axis_tilt)
        
        k_x = np.cos(tilt_rad) * np.sin(az_rad)
        k_y = np.cos(tilt_rad) * np.cos(az_rad)
        k_z = np.sin(tilt_rad)
        
        n0_az_rad = np.radians(panel_azimuth_noon)
        n0_tilt_rad = np.pi/2 - tilt_rad
        n0_x = np.cos(n0_tilt_rad) * np.sin(n0_az_rad)
        n0_y = np.cos(n0_tilt_rad) * np.cos(n0_az_rad)
        n0_z = np.sin(n0_tilt_rad)
        
        omega_rad = np.radians(data['H_deg'])
        rho_rad = omega_rad if k_y >= 0 else -omega_rad
        
        v_cross_x = k_y * n0_z - k_z * n0_y
        n_rot_x = v_cross_x * np.sin(rho_rad)
        n_rot_y = n0_y * np.cos(rho_rad)
        n_rot_z = n0_z * np.cos(rho_rad)
        
        if n_rot_z < 0:
            continue
        
        n_rot_z = np.clip(n_rot_z, -1.0, 1.0)
        sigma_polar = np.degrees(np.arccos(n_rot_z))
        phi_c_polar = np.degrees(np.arctan2(n_rot_x, n_rot_y))
        
        Ic, cos_theta = self.calculate_incident_irradiance(
            data['beta'], data['phi_s'],
            sigma_polar, phi_c_polar,
            data['Ib'], data['C']
        )
        pv_result = self.calculate_pv_performance(Ic, cos_theta, T_amb=data['T_amb'], efficiency=efficiency)
        total_electrical_yield += (pv_result['P_out'] / 1000.0)
    
    return best_axis_tilt, total_electrical_yield
