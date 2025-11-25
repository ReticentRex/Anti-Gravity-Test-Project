import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from solar_model import SolarModel

# ... (Page Config and Title remain same) ...

# Page Config
st.set_page_config(
    page_title="Solar Resource Model",
    page_icon="☀️",
    layout="wide"
)

# Initialize Session State for Mode
if 'user_mode' not in st.session_state:
    st.session_state['user_mode'] = None

# --- Landing Page (Mode Selection) ---
if st.session_state['user_mode'] is None:
    st.title("☀️ Solar Resource Model")
    st.markdown("### Choose your experience level:")
    
    # Custom CSS for Landing Page Buttons
    st.markdown("""
    <style>
    /* Base Button Style */
    div.stButton > button {
        width: 100%;
        aspect-ratio: 1 / 1;
        height: auto !important;
        border-radius: 25px;
        border: 2px solid rgba(0,0,0,0.1) !important; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify_content: center;
        color: #1a1a1a !important; /* Force Dark Text */
        opacity: 1 !important;
        padding: 20px !important;
    }
    
    /* Button Text Styling */
    div.stButton > button p {
        font-size: 32px !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        margin-top: 10px !important;
    }
    
    /* Hover Effects */
    div.stButton > button:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        border-color: rgba(0,0,0,0.2) !important;
    }
    
    /* Standard Version (Green Pastel) */
    .st-key-btn_standard button {
        background-color: #C8E6C9 !important;
    }
    .st-key-btn_standard button:hover {
        background-color: #A5D6A7 !important;
    }
    /* Standard Icon via Pseudo-element */
    .st-key-btn_standard button::before {
        content: "🏡";
        font-size: 80px;
        margin-bottom: 10px;
        display: block;
    }

    /* Van Life Version (Orange Pastel) */
    .st-key-btn_vanlife button {
        background-color: #FFE0B2 !important; /* Warm Orange */
    }
    .st-key-btn_vanlife button:hover {
        background-color: #FFCC80 !important;
    }
    /* Van Life Icon via Pseudo-element */
    .st-key-btn_vanlife button::before {
        content: "🚐";
        font-size: 80px;
        margin-bottom: 10px;
        display: block;
    }

    /* Advanced Version (Blue Pastel) */
    .st-key-btn_advanced button {
        background-color: #BBDEFB !important;
    }
    .st-key-btn_advanced button:hover {
        background-color: #90CAF9 !important;
    }
    /* Advanced Icon via Pseudo-element */
    .st-key-btn_advanced button::before {
        content: "🚀";
        font-size: 80px;
        margin-bottom: 10px;
        display: block;
    }
    
    /* Helper Text Styling */
    .mode-helper-text {
        text-align: center; 
        margin-bottom: 15px; 
        font-size: 1.4rem;
        font-weight: 600;
        opacity: 0.9;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Layout: Spacer, Standard, Van Life, Advanced, Spacer
    c_space1, c_std, c_van, c_adv, c_space2 = st.columns([0.5, 2, 2, 2, 0.5])
    
    with c_std:
        st.markdown("<div class='mode-helper-text'>For Homeowners &<br>General Users</div>", unsafe_allow_html=True)
        if st.button("Standard\nVersion", use_container_width=True, key="btn_standard"):
            st.session_state['user_mode'] = 'Standard'
            st.rerun()
    
    with c_van:
        st.markdown("<div class='mode-helper-text'>For Van Lifers<br>and 4WDs</div>", unsafe_allow_html=True)
        if st.button("Van Life/4WD", use_container_width=True, key="btn_vanlife"):
            st.session_state['user_mode'] = 'VanLife'
            st.rerun()
            
    with c_adv:
        st.markdown("<div class='mode-helper-text'>For Engineers &<br>Researchers</div>", unsafe_allow_html=True)
        if st.button("Advanced\nVersion", use_container_width=True, key="btn_advanced"):
            st.session_state['user_mode'] = 'Advanced'
            st.rerun()

# --- Van Life/4WD Version (Placeholder) ---
elif st.session_state['user_mode'] == 'VanLife':
    with st.sidebar:
        st.header("⚙️ Settings")
        if st.button("🔄 Switch Mode"):
            st.session_state['user_mode'] = None
            st.rerun()
    
    st.markdown("## 🚐 Van Life / 4WD Solar Calculator")
    st.info("🏕️ This specialized mode for mobile off-grid systems is coming soon!")
    st.markdown("""
    **Planned features:**
    - Flat panel optimization (roof-mounted)
    - Portable/tiltable panel calculations
    - Battery sizing recommendations
    - Daily energy consumption matching
    - Travel route solar forecasting
    """)


# --- Standard Version ---
elif st.session_state['user_mode'] == 'Standard':
    from streamlit_searchbox import st_searchbox
    
    # Sidebar - Switch Mode Button
    with st.sidebar:
        st.header("⚙️ Settings")
        if st.button("🔄 Switch Mode"):
            st.session_state['user_mode'] = None
            st.rerun()
        st.markdown("---")
        st.info("Using OpenStreetMap for location search. No API Key required.")
    
    # Search function for streamlit-searchbox
    def search_nominatim(query: str):
        if len(query) < 3:
            return []
        
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 5,
                'addressdetails': 1
            }
            headers = {'User-Agent': 'SolarResourceModel/1.0'}
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            
            # Return list of display names
            return [r['display_name'] for r in data] if data else []
        except:
            return []
        
    st.markdown("## 🏡 Standard Solar Assessment")
    st.markdown("Enter your location and system size to get a quick estimate.")

    # Inputs
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        # Searchbox with autocomplete
        selected_address = st_searchbox(
            search_nominatim,
            label="🔍 Search Location",
            placeholder="Start typing your suburb or address...",
            key="location_search",
            clear_on_submit=False
        )
        
        # Get full location data if something selected
        selected_location = None
        if selected_address:
            try:
                # Re-query to get full location data
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': selected_address,
                    'format': 'json',
                    'limit': 1,
                    'addressdetails': 1
                }
                headers = {'User-Agent': 'SolarResourceModel/1.0'}
                response = requests.get(url, params=params, headers=headers)
                data = response.json()
                
                if data:
                    selected_location = data[0]
                    lat = float(selected_location['lat'])
                    lon = float(selected_location['lon'])
                    
                    st.success(f"✓ {selected_address}")
                    st.caption(f"📍 {lat:.4f}°, {lon:.4f}°")
            except:
                st.error("Error retrieving location details")
    
    with col_input2:
        system_capacity_kw = st.number_input("System Rated Power (kW)", min_value=1.0, value=6.6, step=0.1)
        num_people = st.number_input("Number of People in Household", min_value=1, value=4, step=1, help="Used to estimate daily energy demand.")

    # Run Simulation
    if st.button("🚀 Run Assessment", type="primary", disabled=(selected_location is None)):
        with st.spinner("Simulating solar performance..."):
            # 1. Determine Parameters
            latitude = float(selected_location['lat'])
            longitude = float(selected_location['lon'])
            hemisphere = 'South' if latitude < 0 else 'North'
            
            # Azimuth: North (0) for Southern Hemisphere, South (180) for Northern
            azimuth = 0 if hemisphere == 'South' else 180
            
            tilt_std = 25.0
            efficiency = 0.14 # Fixed 14%
            
            # Find optimal tilt by testing a range
            st.markdown("---")
            st.subheader(f"Results for {system_capacity_kw}kW System")
            
            # Helper for metrics
            def show_metric_card(label, yield_per_m2, total_yield_kwh, is_ideal=False):
                bg_color = "#f0f2f6" if not is_ideal else "#e8f5e9"
                border = "2px solid #4caf50" if is_ideal else "1px solid #ddd"
                st.markdown(f"""
                <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; border: {border}; margin-bottom: 10px;">
                    <h4 style="margin:0; color:#333;">{label}</h4>
                    <div style="font-size: 2rem; font-weight: bold; color: #1a1a1a;">
                        {int(total_yield_kwh):,} <span style="font-size: 1rem; color: #666;">kWh/year</span>
                    </div>
                    <div style="font-size: 1rem; color: #555;">
                        {int(yield_per_m2):,} kWh/m²
                    </div>
                </div>
                """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            
            area_m2 = system_capacity_kw / efficiency
            
            # Horizontal
            horiz_m2 = totals_std['Annual_Yield_Horizontal_kWh_m2']
            horiz_sys = horiz_m2 * area_m2
            with c1:
                show_metric_card("Horizontal (Flat)", horiz_m2, horiz_sys)
                
            # Standard Fixed (25 deg)
            fixed_m2 = totals_std['Annual_Yield_Fixed_kWh_m2']
            fixed_sys = fixed_m2 * area_m2
            with c2:
                show_metric_card(f"Fixed Panel ({int(tilt_std)}° Tilt)", fixed_m2, fixed_sys)
                
            # Ideal Fixed (Lat Tilt)
            ideal_m2 = totals_ideal['Annual_Yield_Fixed_kWh_m2']
            ideal_sys = ideal_m2 * area_m2
            with c3:
                show_metric_card(f"Optimal Fixed ({int(tilt_ideal)}° Tilt)", ideal_m2, ideal_sys, is_ideal=True)
            
            
            # Charts (Simplified Annual Comparison)
            st.markdown("### Annual Energy Comparison")
            
            chart_data = pd.DataFrame({
                'Configuration': ['Horizontal (Flat)', f'Fixed Panel ({int(tilt_std)}°)', f'Optimal Fixed ({int(tilt_ideal)}°)'],
                'Annual Yield (kWh)': [horiz_sys, fixed_sys, ideal_sys]
            })
            
            fig = px.bar(chart_data, x='Configuration', y='Annual Yield (kWh)',
                         title="Annual Energy Yield Comparison",
                         color='Configuration',
                         color_discrete_map={
                             'Horizontal (Flat)': '#bdc3c7', 
                             f'Fixed Panel ({int(tilt_std)}°)': '#3498db', 
                             f'Optimal Fixed ({int(tilt_ideal)}°)': '#2ecc71'
                         })
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # --- Demand vs Generation Analysis ---
            st.markdown("---")
            st.subheader("📊 Seasonal Demand vs Generation")
            st.markdown(f"Comparing your **{system_capacity_kw} kW** system against a typical **{num_people}-person** household demand.")
            
            # 1. Define Demand Profile
            # Approx 6.0 kWh per person per day (Typical AU household ~24kWh for 4 people)
            daily_usage_kwh = num_people * 6.0
            
            # Default to Real Data (Ausgrid)
            use_real_data = True
            try:
                from load_profiles import get_profile
            except ImportError:
                # Fallback if file missing
                use_real_data = False

            # Synthetic Profile Weights (Fallback)
            synthetic_weights = [
                0.02, 0.02, 0.02, 0.02, 0.02, 0.03, # 0-5 (Night)
                0.05, 0.08, 0.06, 0.04, 0.03, 0.03, # 6-11 (Morning Peak)
                0.03, 0.03, 0.03, 0.04, 0.06, 0.09, # 12-17 (Day/Early Eve)
                0.10, 0.09, 0.06, 0.04, 0.03, 0.03  # 18-23 (Evening Peak)
            ]
            # Normalize synthetic
            total_weight = sum(synthetic_weights)
            synthetic_weights = [w/total_weight for w in synthetic_weights]
            
            # 2. Calculate Seasonal Solar Profiles (using Optimal Fixed system)
            # Add Season column
            # Southern Hemisphere Seasons
            if hemisphere == 'South':
                season_map = {12: 'Summer', 1: 'Summer', 2: 'Summer',
                              3: 'Autumn', 4: 'Autumn', 5: 'Autumn',
                              6: 'Winter', 7: 'Winter', 8: 'Winter',
                              9: 'Spring', 10: 'Spring', 11: 'Spring'}
            else:
                season_map = {12: 'Winter', 1: 'Winter', 2: 'Winter',
                              3: 'Spring', 4: 'Spring', 5: 'Spring',
                              6: 'Summer', 7: 'Summer', 8: 'Summer',
                              9: 'Autumn', 10: 'Autumn', 11: 'Autumn'}
            
            # Fix: Calculate Month from Day of Year
            # Using a non-leap year (2023) for standard mapping
            df_ideal['Date'] = pd.to_datetime(df_ideal['Day'] - 1, unit='D', origin='2023-01-01')
            df_ideal['Month'] = df_ideal['Date'].dt.month
            
            df_ideal['Season'] = df_ideal['Month'].map(season_map)
            
            # Group by Season and Hour to get average kW
            # Note: 'P_Fixed_W_m2' is Power in W/m2. 
            # System Power (kW) = (Power W/m2 / 1000) * Area (m2)
            df_ideal['System_Gen_kW'] = (df_ideal['P_Fixed_W_m2'] / 1000.0) * area_m2
            
            seasonal_profiles = df_ideal.groupby(['Season', 'Hour'])['System_Gen_kW'].mean().reset_index()
            
            # Fix: Ensure all 24 hours exist for each season (fill missing with 0)
            # Create a complete index of Season * Hour
            seasons = ['Summer', 'Autumn', 'Winter', 'Spring']
            full_idx = pd.MultiIndex.from_product([seasons, range(24)], names=['Season', 'Hour'])
            seasonal_profiles = seasonal_profiles.set_index(['Season', 'Hour']).reindex(full_idx, fill_value=0).reset_index()
            
            # 3. Create Visualization (2x2 Grid)
            from plotly.subplots import make_subplots
            
            # Seasonal Demand Multipliers (relative to baseline)
            # Winter: Higher due to heating / lighting
            # Summer: Higher due to cooling
            seasonal_demand_factors = {
                'Summer': 1.3,
                'Autumn': 1.0,
                'Winter': 1.4,
                'Spring': 1.0
            }
            
            # seasons list is already defined above
            fig_seasonal = make_subplots(
                rows=2, cols=2, 
                subplot_titles=seasons, 
                vertical_spacing=0.25,
                horizontal_spacing=0.1
            )
            
            for i, season in enumerate(seasons):
                row = (i // 2) + 1
                col = (i % 2) + 1
                
                # Solar Data
                solar_data = seasonal_profiles[seasonal_profiles['Season'] == season]['System_Gen_kW'].values
                hours = list(range(24))
                
                # Calculate Season-Specific Demand
                season_factor = seasonal_demand_factors.get(season, 1.0)
                season_daily_usage = daily_usage_kwh * season_factor
                
                if use_real_data:
                    # Use Ausgrid Profile for this season
                    weights = get_profile(season)
                    season_demand_profile = [w * season_daily_usage for w in weights]
                else:
                    # Use Synthetic Profile
                    season_demand_profile = [w * season_daily_usage for w in synthetic_weights]
                
                # Add Solar Area
                fig_seasonal.add_trace(
                    go.Scatter(
                        x=hours, y=solar_data, 
                        fill='tozeroy', 
                        name='Solar Generation',
                        line=dict(color='#f1c40f', width=2),
                        fillcolor='rgba(241, 196, 15, 0.3)',
                        showlegend=(i==0)
                    ),
                    row=row, col=col
                )
                
                # Add Demand Line
                fig_seasonal.add_trace(
                    go.Scatter(
                        x=hours, y=season_demand_profile, 
                        mode='lines', 
                        name='Household Demand',
                        line=dict(color='#2c3e50', width=3, dash='solid'), 
                        showlegend=(i==0)
                    ),
                    row=row, col=col
                )
                
                fig_seasonal.update_xaxes(title_text="Hour", row=row, col=col, tickvals=[0,6,12,18,23], showgrid=False)
                fig_seasonal.update_yaxes(title_text="kW", row=row, col=col, showgrid=True, gridcolor='#333') # Darker grid for contrast if needed, or let theme handle it

            fig_seasonal.update_layout(
                height=700, 
                title_text="Average Daily Profiles by Season",
                # Removed explicit white background to match Advanced Mode (inherits theme)
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_seasonal, use_container_width=True)
            
            st.info("📊 **Data Source:** Representative load profiles based on typical Australian residential consumption patterns from published energy research (CSIRO, AEMO). These are synthetic approximations for demonstration purposes.")

# --- Advanced Version (Existing App) ---
elif st.session_state['user_mode'] == 'Advanced':
    st.sidebar.button("🔄 Switch Mode", on_click=lambda: st.session_state.update({'user_mode': None}))
    
    # Title and Intro
    st.title("☀️ Solar Resource & PV Performance Model")
    st.markdown("""
    This tool simulates the hourly solar energy yield for different collector orientations based on the thesis by Ryan Coble-Neal: [*Identifying the Factors Impacting the Performance of Two-Axis Sun-Tracking Photovoltaic Systems on Mobile Platforms*](https://ryancoble-neal.com/projects/project1.html).
    It accounts for **Solar Geometry**, **Atmospheric Attenuation**, **Angular Losses**, and **Thermal Losses**.
    """)

    # Sidebar - Inputs
    st.sidebar.header("📍 Location Settings")
    latitude = st.sidebar.number_input("Latitude (deg)", value=-32.05, min_value=-90.0, max_value=90.0, step=0.01, help="Positive for North, Negative for South")
    longitude = st.sidebar.number_input("Longitude (deg)", value=115.89, min_value=-180.0, max_value=180.0, step=0.01, help="Positive for East, Negative for West")
    st.sidebar.markdown("---")
    st.sidebar.header("🔧 Fixed Panel Settings")
    fixed_tilt = st.sidebar.number_input("Tilt Angle (deg)", value=32.0, min_value=0.0, max_value=90.0, step=1.0, help="0 = Horizontal, 90 = Vertical")
    fixed_azimuth = st.sidebar.number_input("Azimuth Angle (deg)", value=0.0, min_value=-180.0, max_value=180.0, step=1.0, help="0 = North, 90 = East, -90 = West, 180 = South")

    st.sidebar.markdown("---")
    st.sidebar.header("⚡ PV Module Parameters")
    efficiency_percent = st.sidebar.number_input("Module Efficiency (%)", value=14.0, min_value=1.0, max_value=50.0, step=0.1, help="Standard Test Conditions (STC) Efficiency")
    system_capacity_kw = st.sidebar.number_input("System Rated Power (kW)", min_value=0.1, value=5.0, step=0.1)


    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Simulation")
    optimize_electrical = st.sidebar.checkbox(
        "Optimise Tilt Angle For Temperature and AOI",
        value=False,
        help="When checked, optimal tilt maximizes electrical yield by accounting for both temperature effects and AOI (Angle of Incidence - the angle between sunlight and the panel normal). When unchecked, it optimizes purely for AOI to minimize reflection losses and maximize incident irradiance, ignoring thermal effects."
    )
    if st.sidebar.button("Run Simulation", type="primary"):
        with st.spinner("Calculating annual profile..."):
            # Initialize Model
            model = SolarModel(latitude=latitude, longitude=longitude)
            
            # Calculate Optimal Tilt
            optimal_tilt, optimal_yield = model.calculate_optimal_tilt(
                efficiency=efficiency_percent/100.0,
                optimize_electrical=optimize_electrical
            )
            st.session_state['optimal_tilt'] = optimal_tilt
            st.session_state['optimal_yield'] = optimal_yield
            st.session_state['optimize_electrical'] = optimize_electrical
            
            # Generate Profile with Optimal Tilt
            df_hourly, totals = model.generate_annual_profile(
                fixed_tilt=fixed_tilt, 
                fixed_azimuth=fixed_azimuth, 
                efficiency=efficiency_percent/100.0,
                optimal_tilt=optimal_tilt
            )
            
            # Store results in session state
            st.session_state['totals'] = totals
            st.session_state['df_hourly'] = df_hourly
            st.session_state['run_simulation'] = True

    if st.session_state.get('run_simulation'):
        totals = st.session_state.get('totals', {})
        optimal_tilt = st.session_state.get('optimal_tilt', 0)
        optimal_yield = st.session_state.get('optimal_yield', 0)
        optimize_electrical = st.session_state.get('optimize_electrical', False)
        df_hourly = st.session_state.get('df_hourly')
        
        # Define Metric Columns with detailed tooltips
        tracker_tooltips = {
            'Horizontal': 'Panel lies flat on the ground (0° tilt). Simple but inefficient.',
            'Fixed Tilt': f'Panel fixed at {fixed_tilt}° tilt, {fixed_azimuth}° azimuth. No moving parts.',
            'Fixed E-W': 'Two panels at 45° tilt facing East (90°) and West (270°). Averages morning/evening production.',
            'Fixed N-S': 'Two panels at 45° tilt facing North (0°) and South (180°). Captures different sun paths.',
            '1-Axis Azimuth': 'Rotates East-West on a tilted axis to follow the sun\'s daily path. Panel tilt is optimized.',
            '1-Axis Polar': 'Axis tilted at latitude angle, aligned with Earth\'s rotation axis. Rotates by hour angle (15°/hour) to track the sun\'s East-West motion. Does NOT adjust for seasonal elevation changes.',
            '1-Axis Horizontal': 'Horizontal North-South axis. Rotates East-West like Polar but without seasonal tilt advantage.',
            '1-Axis Elevation': 'Rotates on horizontal East-West axis to track sun elevation by tilting North-South. Panel orientation (N or S) is determined by seasonal declination, not instantaneous azimuth. Most beneficial at equatorial latitudes where sun crosses between hemispheres throughout the year.',
            '2-Axis': 'Fully articulating tracker. Adjusts both azimuth and elevation to point directly at the sun at all times.'
        }
        
        metric_cols = [
            ('Horizontal', 'Annual_Yield_Horizontal_kWh_m2', 'Flat on the ground'),
            ('Fixed Tilt', 'Annual_Yield_Fixed_kWh_m2', f'Fixed at {fixed_tilt}° tilt, {fixed_azimuth}° azimuth'),
            ('Fixed E-W', 'Annual_Yield_Fixed_EW_kWh_m2', 'Dual panels facing East and West'),
            ('Fixed N-S', 'Annual_Yield_Fixed_NS_kWh_m2', 'Dual panels facing North and South'),
            ('1-Axis Azimuth', 'Annual_Yield_1Axis_Azimuth_kWh_m2', 'Tracks sun East-West'),
            ('1-Axis Polar', 'Annual_Yield_1Axis_Polar_kWh_m2', 'Aligned with Earth\'s axis'),
            ('1-Axis Horizontal', 'Annual_Yield_1Axis_Horizontal_kWh_m2', 'Horizontal N-S axis'),
            ('1-Axis Elevation', 'Annual_Yield_1Axis_Elevation_kWh_m2', 'Tracks sun elevation'),
            ('2-Axis', 'Annual_Yield_2Axis_kWh_m2', 'Tracks sun exactly')
        ]
            
        
        # Custom CSS for larger body text
        st.markdown("""
        <style>
            html, body, [class*="css"]  {
                font-size: 1.1rem;
            }
        </style>
        """, unsafe_allow_html=True)

        # Helper for custom metrics
        def display_custom_metric(label, value, unit, delta_val=None, delta_text=None, is_ref=False):
            delta_html = ""
            label_color = "#b0b0b0" # Lighter grey for better contrast
            unit_color = "#b0b0b0"
            
            if is_ref:
                 delta_html = f'<div style="font-size: 0.9rem; color: #09ab3b;">Reference</div>' # Green Reference
            elif delta_val is not None:
                color = "#09ab3b" if delta_val >= 0 else "#ff2b2b"
                arrow = "↑" if delta_val >= 0 else "↓"
                delta_html = f'<div style="font-size: 0.9rem; color: {color};">{arrow} {abs(delta_val):.0f}{delta_text}</div>'
                
            st.markdown(f"""
            <div style="margin-bottom: 10px;">
                <div style="font-size: 0.9rem; color: {label_color}; margin-bottom: -5px;">{label}</div>
                <div style="font-size: 1.4rem; font-weight: 600;">{value:,.0f} <span style="font-size: 0.9rem; color: {unit_color};">{unit}</span></div>
                {delta_html}
            </div>
            """, unsafe_allow_html=True)

        # Section 1: Average Energy Density (Uncooled)
        st.subheader("⚡ Average Energy Density Without Active Cooling (kWh/m²)")
        
        # Display in a 3-column grid
        for i in range(0, len(metric_cols), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(metric_cols):
                    label, key, help_text = metric_cols[i+j]
                    with cols[j]:
                        val = totals.get(key, 0)
                        
                        # Calculate Delta % vs 2-Axis
                        ref_val = totals.get('Annual_Yield_2Axis_kWh_m2', 1)
                        if ref_val > 0:
                            pct = (val / ref_val) * 100
                            delta_val = pct - 100 # e.g. 80% -> -20%
                        else:
                            delta_val = 0
                            
                        is_ref = (label == '2-Axis')
                        
                        # Delta HTML
                        delta_html = ""
                        if is_ref:
                             delta_html = f'<div style="font-size: 0.9rem; color: #09ab3b;">Reference</div>'
                        elif label == 'Fixed Tilt':
                            # Two-line comparison: vs Optimal and vs 2-Axis
                            pct_diff_optimal = ((val - optimal_yield) / optimal_yield * 100) if optimal_yield > 0 else 0
                            pct_diff_2axis = delta_val  # Already calculated above
                            
                            if abs(pct_diff_optimal) < 0.1:
                                # Within 0.1% of optimal
                                line1 = f'<div style="font-size: 0.85rem; color: #09ab3b;">✓ Optimal: {optimal_tilt:.0f}° ({optimal_yield:.0f} kWh/m²)</div>'
                            else:
                                color1 = "#09ab3b" if pct_diff_optimal >= 0 else "#ff2b2b"
                                arrow1 = "↑" if pct_diff_optimal >= 0 else "↓"
                                line1 = f'<div style="font-size: 0.85rem; color: {color1};">{arrow1} {abs(pct_diff_optimal):.1f}% vs Opt: {optimal_tilt:.0f}° ({optimal_yield:.0f} kWh/m²)</div>'
                            
                            color2 = "#09ab3b" if pct_diff_2axis >= 0 else "#ff2b2b"
                            arrow2 = "↑" if pct_diff_2axis >= 0 else "↓"
                            line2 = f'<div style="font-size: 0.85rem; color: {color2};">{arrow2} {abs(pct_diff_2axis):.1f}% vs 2-Axis</div>'
                            
                            delta_html = line1 + line2
                        elif delta_val != 0:
                            color = "#09ab3b" if delta_val >= 0 else "#ff2b2b"
                            arrow = "↑" if delta_val >= 0 else "↓"
                            delta_html = f'<div style="font-size: 0.9rem; color: {color};">{arrow} {abs(delta_val):.0f}%</div>'
                        else:
                            delta_html = '<div style="font-size: 0.9rem; color: #b0b0b0;">-</div>'
                            
                        # Extra Note for Optimized Trackers
                        extra_html = ""
                        if label in ['1-Axis Azimuth', '1-Axis Polar']:
                             extra_html = f'<div style="font-size: 0.75rem; color: #2ecc71; margin-top: 2px;">✓ Optimized to {optimal_tilt:.0f}°</div>'

                        # Capacity Factor
                        cf_key_map = {
                            'Annual_Yield_Horizontal_kWh_m2': 'Horizontal',
                            'Annual_Yield_Fixed_kWh_m2': 'Fixed',
                            'Annual_Yield_Fixed_EW_kWh_m2': 'Fixed_EW',
                            'Annual_Yield_Fixed_NS_kWh_m2': 'Fixed_NS',
                            'Annual_Yield_1Axis_Azimuth_kWh_m2': '1Axis_Azimuth',
                            'Annual_Yield_1Axis_Polar_kWh_m2': '1Axis_Polar',
                            'Annual_Yield_1Axis_Horizontal_kWh_m2': '1Axis_Horizontal',
                            'Annual_Yield_1Axis_Elevation_kWh_m2': '1Axis_Elevation',
                            'Annual_Yield_2Axis_kWh_m2': '2Axis'
                        }
                        cf_suffix = cf_key_map.get(key)
                        cf_overall = totals.get(f"CF_Overall_{cf_suffix}", 0)
                        cf_daylight = totals.get(f"CF_Daylight_{cf_suffix}", 0)
                        
                        # Image Handling
                        import base64
                        base_path = "c:/Users/Ryan/Desktop/Random BS/Anti Gravity Test Project/Collector Images/"
                        image_files = {
                            'Horizontal': "horizontal_panel_schematic_1763815355294.png",
                            'Fixed Tilt': "fixed_custom_schematic_1763815554067.png",
                            '1-Axis Azimuth': "one_axis_azimuth_schematic_1763815278060.png",
                            '1-Axis Elevation': "one_axis_elevation_schematic_1763815294214.png",
                            '2-Axis': "two_axis_tracking_schematic_1763815319309.png",
                            '1-Axis Polar': "polar_axis_schematic_v4.png",
                            '1-Axis Horizontal': "horizontal_axis_schematic.png",
                            'Fixed E-W': "East-West Collector Configuration Schematic.png",
                            'Fixed N-S': "north_south_schematic_v3.png"
                        }
                        
                        img_html = ""
                        img_path_for_modal = ""
                        img_id = label.replace(" ", "_").replace("-", "_")
                        if label in image_files:
                            img_path = base_path + image_files[label]
                            img_path_for_modal = img_path
                            try:
                                with open(img_path, "rb") as f:
                                    img_data = base64.b64encode(f.read()).decode()
                                # Image with hover effect
                                img_html = f'''<style>
.tracker-img-{img_id} {{
    transition: all 0.3s ease;
    cursor: pointer;
}}
.tracker-img-{img_id}:hover {{
    transform: scale(1.05);
    filter: brightness(1.1);
}}
</style>
<div style="border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px; padding: 8px; background-color: rgba(255, 255, 255, 0.03); display: inline-block;">
    <img src="data:image/png;base64,{img_data}" class="tracker-img-{img_id}" style="height: 120px; width: auto; display: block;" title="Click expander below to view full size">
</div>'''
                            except Exception:
                                img_html = '<div style="height: 120px; width: 120px; display: flex; align-items: center; justify-content: center; color: #ccc; border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px;">No Image</div>'

                        # Get tooltip
                        tooltip = tracker_tooltips.get(label, '').replace('"', '&quot;')
                        
                        # Help icon matching Streamlit's native style with improved tooltip
                        help_icon_svg = '''<svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 512 512" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M504 256c0 136.997-111.043 248-248 248S8 392.997 8 256C8 119.083 119.043 8 256 8s248 111.083 248 248zM262.655 90c-54.497 0-89.255 22.957-116.549 63.758-3.536 5.286-2.353 12.415 2.715 16.258l34.699 26.31c5.205 3.947 12.621 3.008 16.665-2.122 17.864-22.658 30.113-35.797 57.303-35.797 20.429 0 45.698 13.148 45.698 32.958 0 14.976-12.363 22.667-32.534 33.976C247.128 238.528 216 254.941 216 296v4c0 6.627 5.373 12 12 12h56c6.627 0 12-5.373 12-12v-1.333c0-28.462 83.186-29.647 83.186-106.667 0-58.002-60.165-102-116.531-102zM256 338c-25.365 0-46 20.635-46 46 0 25.364 20.635 46 46 46s46-20.636 46-46c0-25.365-20.635-46-46-46z"></path></svg>'''
                        
                        # Streamlit-style tooltip CSS
                        tooltip_css = f'''<style>
.help-tooltip-{img_id} {{
    position: relative;
    display: inline-block;
}}
.help-tooltip-{img_id} .tooltiptext {{
    visibility: hidden;
    width: 300px;
    background-color: #262730;
    color: #fafafa;
    text-align: left;
    border-radius: 6px;
    padding: 12px;
    position: absolute;
    z-index: 1000;
    bottom: 125%;
    left: 50%;
    margin-left: -150px;
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 14px;
    line-height: 1.6;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
}}
.help-tooltip-{img_id} .tooltiptext::after {{
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: #262730 transparent transparent transparent;
}}
.help-tooltip-{img_id}:hover .tooltiptext {{
    visibility: visible;
    opacity: 1;
}}
</style>'''
                        
                        # Render Card with Side-by-Side Layout
                        st.markdown(f"""{tooltip_css}
<div style="border: 1px solid rgba(128, 128, 128, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 6px; background-color: rgba(255, 255, 255, 0.02);">
<div style="text-align: center; font-size: 1rem; font-weight: 600; color: #b0b0b0; margin-bottom: 12px;">
    {label}
    <span class="help-tooltip-{img_id}" style="display: inline-block; margin-left: 4px; vertical-align: middle; color: rgba(49, 51, 63, 0.6); cursor: help;">
        {help_icon_svg}
        <span class="tooltiptext">{tooltip}</span>
    </span>
</div>
<div style="display: flex; align-items: center; justify-content: space-between; gap: 20px;">
<div style="flex: 1; text-align: left; display: flex; flex-direction: column; gap: 3px;">
<div style="font-size: 1.3rem; font-weight: 700;">{val:,.0f} <span style="font-size: 0.85rem; color: #b0b0b0; font-weight: 400;">kWh/m²</span></div>
<div style="font-size: 0.8rem; color: #888;">CF<sub>ann</sub> = {cf_overall:.1f}%</div>
<div style="font-size: 0.8rem; color: #888;">CF<sub>day</sub> = {cf_daylight:.1f}%</div>
<div style="margin-top: 2px;">{delta_html}</div>
{extra_html}
</div>
<div style="flex-shrink: 0;">
{img_html}
</div>
</div>
</div>
""", unsafe_allow_html=True)
                        
                        # Add integrated expander for full-size image viewing
                        if img_path_for_modal and label in image_files:
                            with st.expander("🔍 Click to view full schematic", expanded=False):
                                st.image(img_path_for_modal, caption=f"{label}", use_container_width=True)

        st.info(f"""
        **Daylight Capacity Factor** reveals the system's efficiency specifically during sun-up hours. 
        
        For your **{system_capacity_kw} kW** system, it is calculated as:  
        `Daylight CF = (Annual Energy Yield) / ({system_capacity_kw} kW × Daylight Hours)`
        
        This metric filters out night-time hours to show how effectively the tracking system captures available solar energy when it matters most.
        """)
        
        if optimize_electrical:
            st.info(f"""
            **Optimal Tilt Calculation:** The optimal angle of **{optimal_tilt:.0f}°** maximizes **annual electrical yield**, accounting for real-world thermal losses.
            
            This is calculated by testing tilt angles from **{max(0, int(abs(latitude)) - 5)}° to {int(abs(latitude)) + 5}°** and finding which produces the most electricity over the year, including:
            - **Temperature effects** on panel efficiency (via NOCT and thermal loss model)
            - **Angular reflection losses** at different sun elevations
            - **Seasonal variation** in sun path and intensity
            
            This optimization finds the tilt that balances capturing more sunlight in cooler seasons (higher efficiency) vs. peak summer irradiance.
            """)
        else:
            st.info(f"""
            **Optimal Tilt Calculation:** The optimal angle of **{optimal_tilt:.0f}°** maximizes **annual incident irradiance** on the panel surface.
            
            This is calculated by testing tilt angles from **{max(0, int(abs(latitude)) - 5)}° to {int(abs(latitude)) + 5}°** and finding which receives the most total sunlight over the year.
            
            Traditional "rules of thumb" suggest ~90% of latitude ({abs(latitude)*0.9:.1f}°), but this model accounts for:
            - **Angular reflection losses** at different sun elevations throughout the year
            - **Seasonal variation** in sun path and intensity
            
            **Note:** The displayed energy yields **do include temperature effects** (via NOCT efficiency and thermal losses), but the optimal tilt angle itself is determined purely by maximizing incident sunlight—not by balancing thermal performance. This allows for clear comparison between cooled and uncooled collector performance in the analysis below.
            """)

        st.markdown("---")

        # --- Section 1.5: Total System Yield ---
        st.header(f"⚡ Your {system_capacity_kw} kW System Annual Energy Yield")
        
        # Calculate Array Area (m2) = Rated Power (kW) / Efficiency (kW/m2)
        rated_power_per_m2 = efficiency_percent / 100.0
        array_area_m2 = system_capacity_kw / rated_power_per_m2
        
        st.markdown(f"Based on your **{efficiency_percent}%** efficient panels, your system requires approximately **{array_area_m2:.1f} m²** of active solar area.")
        
        # Reference Yield for Delta (2-Axis)
        ref_yield_per_m2 = totals.get('Annual_Yield_2Axis_kWh_m2', 0)

        # Display in a 3-column grid with card-based layout
        for i in range(0, len(metric_cols), 3):
            sys_cols = st.columns(3)
            for j in range(3):
                if i + j < len(metric_cols):
                    label, key, _ = metric_cols[i+j]
                    with sys_cols[j]:
                        yield_per_m2 = totals.get(key, 0)
                        
                        if efficiency_percent > 0:
                            # Total energy = yield_per_m2 * area
                            total_energy_kwh = yield_per_m2 * array_area_m2
                            ref_total_energy = ref_yield_per_m2 * array_area_m2
                            delta_val = total_energy_kwh - ref_total_energy
                        else:
                            total_energy_kwh = 0
                            delta_val = 0
                        
                        is_ref = (label == '2-Axis')
                        
                        # Delta HTML
                        delta_html = ""
                        if is_ref:
                            delta_html = f'<div style="font-size: 0.8rem; color: #09ab3b;">Reference</div>'
                        elif label == 'Fixed Tilt':
                            # Two-line comparison: vs Optimal and vs 2-Axis
                            optimal_sys_yield = optimal_yield * array_area_m2
                            current_sys_yield = total_energy_kwh
                            pct_diff_optimal = ((current_sys_yield - optimal_sys_yield) / optimal_sys_yield * 100) if optimal_sys_yield > 0 else 0
                            pct_diff_2axis = (delta_val / ref_total_energy * 100) if ref_total_energy > 0 else 0
                            
                            if abs(pct_diff_optimal) < 0.1:
                                # Within 0.1% of optimal
                                line1 = f'<div style="font-size: 0.8rem; color: #09ab3b;">✓ Optimal: {optimal_tilt:.0f}° ({optimal_sys_yield:,.0f} kWh)</div>'
                            else:
                                color1 = "#09ab3b" if pct_diff_optimal >= 0 else "#ff2b2b"
                                arrow1 = "↑" if pct_diff_optimal >= 0 else "↓"
                                line1 = f'<div style="font-size: 0.8rem; color: {color1};">{arrow1} {abs(pct_diff_optimal):.1f}% vs Opt: {optimal_tilt:.0f}° ({optimal_sys_yield:,.0f} kWh)</div>'
                            
                            color2 = "#09ab3b" if pct_diff_2axis >= 0 else "#ff2b2b"
                            arrow2 = "↑" if pct_diff_2axis >= 0 else "↓"
                            line2 = f'<div style="font-size: 0.8rem; color: {color2};">{arrow2} {abs(pct_diff_2axis):.1f}% vs 2-Axis</div>'
                            
                            delta_html = line1 + line2
                        elif delta_val != 0:
                            pct_diff_2axis = (delta_val / ref_total_energy * 100) if ref_total_energy > 0 else 0
                            color = "#09ab3b" if delta_val >= 0 else "#ff2b2b"
                            arrow = "↑" if delta_val >= 0 else "↓"
                            delta_html = f'<div style="font-size: 0.8rem; color: {color};">{arrow} {abs(pct_diff_2axis):.1f}% vs 2-Axis</div>'
                        else:
                            delta_html = '<div style="font-size: 0.8rem; color: #b0b0b0;">-</div>'
                            
                        # Extra Note for Optimized Trackers
                        extra_html = ""
                        if label in ['1-Axis Azimuth', '1-Axis Polar']:
                             extra_html = f'<div style="font-size: 0.75rem; color: #2ecc71; margin-top: 2px;">✓ Optimized to {optimal_tilt:.0f}°</div>'
                        
                        # Get CF data
                        cf_key_map = {
                            'Annual_Yield_Horizontal_kWh_m2': 'Horizontal',
                            'Annual_Yield_Fixed_kWh_m2': 'Fixed',
                            'Annual_Yield_Fixed_EW_kWh_m2': 'Fixed_EW',
                            'Annual_Yield_Fixed_NS_kWh_m2': 'Fixed_NS',
                            'Annual_Yield_1Axis_Azimuth_kWh_m2': '1Axis_Azimuth',
                            'Annual_Yield_1Axis_Polar_kWh_m2': '1Axis_Polar',
                            'Annual_Yield_1Axis_Horizontal_kWh_m2': '1Axis_Horizontal',
                            'Annual_Yield_1Axis_Elevation_kWh_m2': '1Axis_Elevation',
                            'Annual_Yield_2Axis_kWh_m2': '2Axis'
                        }
                        cf_suffix = cf_key_map.get(key)
                        cf_overall = totals.get(f"CF_Overall_{cf_suffix}", 0)
                        cf_daylight = totals.get(f"CF_Daylight_{cf_suffix}", 0)
                        
                        # Image Handling
                        import base64
                        base_path = "c:/Users/Ryan/Desktop/Random BS/Anti Gravity Test Project/Collector Images/"
                        image_files = {
                            'Horizontal': "horizontal_panel_schematic_1763815355294.png",
                            'Fixed Tilt': "fixed_custom_schematic_1763815554067.png",
                            '1-Axis Azimuth': "one_axis_azimuth_schematic_1763815278060.png",
                            '1-Axis Elevation': "one_axis_elevation_schematic_1763815294214.png",
                            '2-Axis': "two_axis_tracking_schematic_1763815319309.png",
                            '1-Axis Polar': "polar_axis_schematic_v4.png",
                            '1-Axis Horizontal': "horizontal_axis_schematic.png",
                            'Fixed E-W': "East-West Collector Configuration Schematic.png",
                            'Fixed N-S': "north_south_schematic_v3.png"
                        }
                        
                        img_html = ""
                        if label in image_files:
                            img_path = base_path + image_files[label]
                            try:
                                with open(img_path, "rb") as f:
                                    img_data = base64.b64encode(f.read()).decode()
                                # Image with tight frame
                                img_html = f'<div style="border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px; padding: 8px; background-color: rgba(255, 255, 255, 0.03); display: inline-block;"><img src="data:image/png;base64,{img_data}" style="height: 120px; width: auto; display: block;"></div>'
                            except Exception:
                                img_html = '<div style="height: 120px; width: 120px; display: flex; align-items: center; justify-content: center; color: #ccc; border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px;">No Image</div>'

                        # Render Card with Side-by-Side Layout
                        st.markdown(f"""
<div style="border: 1px solid rgba(128, 128, 128, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 16px; background-color: rgba(255, 255, 255, 0.02);">
<div style="text-align: center; font-size: 1rem; font-weight: 600; color: #b0b0b0; margin-bottom: 12px;">{label}</div>
<div style="display: flex; align-items: center; justify-content: space-between; gap: 20px;">
<div style="flex: 1; text-align: left; display: flex; flex-direction: column; gap: 3px;">
<div style="font-size: 1.3rem; font-weight: 700;">{total_energy_kwh:,.0f} <span style="font-size: 0.85rem; color: #b0b0b0; font-weight: 400;">kWh</span></div>
<div style="font-size: 0.8rem; color: #888;">CF<sub>ann</sub> = {cf_overall:.1f}%</div>
<div style="font-size: 0.8rem; color: #888;">CF<sub>day</sub> = {cf_daylight:.1f}%</div>
<div style="margin-top: 2px;">{delta_html}</div>
{extra_html}
</div>
<div style="flex-shrink: 0;">
{img_html}
</div>
</div>
</div>
""", unsafe_allow_html=True)


        st.markdown("---")
        
        # --- Active Cooling Benefit Section ---
        st.header("❄️ Active Cooling Benefit")
        st.markdown("Comparison of **Cooled (25°C)** vs **Uncooled** collector performance, showing the benefit of active cooling systems.")
        st.info("""
        **Active Cooling** maintains panels at 25°C, eliminating thermal losses. The percentages below show how much additional energy could be generated if panels were actively cooled to maintain optimal temperature, compared to their actual operating temperature.
        """)
        
        # Subsection 1: Average Energy Density
        st.subheader("⚡ Average Energy Density with Active Cooling (kWh/m²)")
        
        # Dictionary mapping for cooled yields
        cooled_yield_keys = {
            'Horizontal': 'Annual_Yield_Cooled_Horizontal_kWh_m2',
            'Fixed Tilt': 'Annual_Yield_Cooled_Fixed_kWh_m2',
            'Fixed E-W': 'Annual_Yield_Cooled_Fixed_EW_kWh_m2',
            'Fixed N-S': 'Annual_Yield_Cooled_Fixed_NS_kWh_m2',
            '1-Axis Azimuth': 'Annual_Yield_Cooled_1Axis_Azimuth_kWh_m2',
            '1-Axis Polar': 'Annual_Yield_Cooled_1Axis_Polar_kWh_m2',
            '1-Axis Horizontal': 'Annual_Yield_Cooled_1Axis_Horizontal_kWh_m2',
            '1-Axis Elevation': 'Annual_Yield_Cooled_1Axis_Elevation_kWh_m2',
            '2-Axis': 'Annual_Yield_Cooled_2Axis_kWh_m2'
        }
        
        # Display in a 3-column grid
        for i in range(0, len(metric_cols), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(metric_cols):
                    label, uncooled_key, _ = metric_cols[i+j]
                    cooled_key = cooled_yield_keys.get(label)
                    
                    with cols[j]:
                        uncooled_val = totals.get(uncooled_key, 0)
                        cooled_val = totals.get(cooled_key, 0) if cooled_key else uncooled_val
                        
                        # Calculate cooling benefit percentage
                        if uncooled_val > 0:
                            cooling_benefit_pct = ((cooled_val - uncooled_val) / uncooled_val * 100)
                        else:
                            cooling_benefit_pct = 0
                        
                        # Calculate CF for cooled collectors
                        rated_power_kw_m2 = efficiency_percent / 100.0
                        total_hours = 8760
                        daylight_hours = totals.get('Daylight_Hours', 4380)
                        
                        if rated_power_kw_m2 > 0:
                            cf_overall = (cooled_val / (rated_power_kw_m2 * total_hours)) * 100
                            cf_daylight = (cooled_val / (rated_power_kw_m2 * daylight_hours)) * 100 if daylight_hours > 0 else 0
                        else:
                            cf_overall = 0
                            cf_daylight = 0
                        
                        # Cooling benefit delta HTML
                        delta_html = f'<div style="font-size: 0.85rem; color: #09ab3b;">↑ +{cooling_benefit_pct:.1f}% vs Uncooled</div>'
                        
                        # Image Handling
                        import base64
                        base_path = "c:/Users/Ryan/Desktop/Random BS/Anti Gravity Test Project/Collector Images/"
                        image_files = {
                            'Horizontal': "horizontal_panel_schematic_1763815355294.png",
                            'Fixed Tilt': "fixed_custom_schematic_1763815554067.png",
                            '1-Axis Azimuth': "one_axis_azimuth_schematic_1763815278060.png",
                            '1-Axis Elevation': "one_axis_elevation_schematic_1763815294214.png",
                            '2-Axis': "two_axis_tracking_schematic_1763815319309.png",
                            '1-Axis Polar': "polar_axis_schematic_v4.png",
                            '1-Axis Horizontal': "horizontal_axis_schematic.png",
                            'Fixed E-W': "East-West Collector Configuration Schematic.png",
                            'Fixed N-S': "north_south_schematic_v3.png"
                        }
                        
                        img_html = ""
                        if label in image_files:
                            img_path = base_path + image_files[label]
                            try:
                                with open(img_path, "rb") as f:
                                    img_data = base64.b64encode(f.read()).decode()
                                img_html = f'<div style="border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px; padding: 8px; background-color: rgba(255, 255, 255, 0.03); display: inline-block;"><img src="data:image/png;base64,{img_data}" style="height: 120px; width: auto; display:block;"></div>'
                            except Exception:
                                img_html = '<div style="height: 120px; width: 120px; display: flex; align-items: center; justify-content: center; color: #ccc; border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px;">No Image</div>'
                        
                        # Render Card
                        st.markdown(f"""
<div style="border: 1px solid rgba(128, 128, 128, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 16px; background-color: rgba(255, 255, 255, 0.02);">
<div style="text-align: center; font-size: 1rem; font-weight: 600; color: #b0b0b0; margin-bottom: 12px;">{label}</div>
<div style="display: flex; align-items: center; justify-content: space-between; gap: 20px;">
<div style="flex: 1; text-align: left; display: flex; flex-direction: column; gap: 3px;">
<div style="font-size: 1.3rem; font-weight: 700;">{cooled_val:,.0f} <span style="font-size: 0.85rem; color: #b0b0b0; font-weight: 400;">kWh/m²</span></div>
<div style="font-size: 0.8rem; color: #888;">CF<sub>ann</sub> = {cf_overall:.1f}%</div>
<div style="font-size: 0.8rem; color: #888;">CF<sub>day</sub> = {cf_daylight:.1f}%</div>
<div style="margin-top: 2px;">{delta_html}</div>
</div>
<div style="flex-shrink: 0;">
{img_html}
</div>
</div>
</div>
""", unsafe_allow_html=True)
        
        # Subsection 2: Annual System Yield
        st.subheader(f"⚡ Your {system_capacity_kw} kW System Annual Energy Yield with Active Cooling (kWh)")
        st.markdown(f"Based on your **{efficiency_percent}%** efficient panels, your system requires approximately **{array_area_m2:.1f} m²** of active solar area.")
        
        # Display in a 3-column grid
        for i in range(0, len(metric_cols), 3):
            sys_cols = st.columns(3)
            for j in range(3):
                if i + j < len(metric_cols):
                    label, uncooled_key, _ = metric_cols[i+j]
                    cooled_key = cooled_yield_keys.get(label)
                    
                    with sys_cols[j]:
                        uncooled_per_m2 = totals.get(uncooled_key, 0)
                        cooled_per_m2 = totals.get(cooled_key, 0) if cooled_key else uncooled_per_m2
                        
                        # System totals
                        uncooled_system = uncooled_per_m2 * array_area_m2
                        cooled_system = cooled_per_m2 * array_area_m2
                        
                        # Calculate cooling benefit percentage
                        if uncooled_system > 0:
                            cooling_benefit_pct = ((cooled_system - uncooled_system) / uncooled_system * 100)
                        else:
                            cooling_benefit_pct = 0
                        
                        # Calculate CF for cooled collectors
                        rated_power_kw_m2 = efficiency_percent / 100.0
                        total_hours = 8760
                        daylight_hours = totals.get('Daylight_Hours', 4380)
                        
                        if rated_power_kw_m2 > 0:
                            cf_overall = (cooled_per_m2 / (rated_power_kw_m2 * total_hours)) * 100
                            cf_daylight = (cooled_per_m2 / (rated_power_kw_m2 * daylight_hours)) * 100 if daylight_hours > 0 else 0
                        else:
                            cf_overall = 0
                            cf_daylight = 0
                        
                        # Cooling benefit delta HTML
                        delta_html = f'<div style="font-size: 0.85rem; color: #09ab3b;">↑ +{cooling_benefit_pct:.1f}% vs Uncooled</div>'
                        
                        # Image Handling
                        import base64
                        base_path = "c:/Users/Ryan/Desktop/Random BS/Anti Gravity Test Project/Collector Images/"
                        image_files = {
                            'Horizontal': "horizontal_panel_schematic_1763815355294.png",
                            'Fixed Tilt': "fixed_custom_schematic_1763815554067.png",
                            '1-Axis Azimuth': "one_axis_azimuth_schematic_1763815278060.png",
                            '1-Axis Elevation': "one_axis_elevation_schematic_1763815294214.png",
                            '2-Axis': "two_axis_tracking_schematic_1763815319309.png",
                            '1-Axis Polar': "polar_axis_schematic_v4.png",
                            '1-Axis Horizontal': "horizontal_axis_schematic.png",
                            'Fixed E-W': "East-West Collector Configuration Schematic.png",
                            'Fixed N-S': "north_south_schematic_v3.png"
                        }
                        
                        img_html = ""
                        if label in image_files:
                            img_path = base_path + image_files[label]
                            try:
                                with open(img_path, "rb") as f:
                                    img_data = base64.b64encode(f.read()).decode()
                                img_html = f'<div style="border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px; padding: 8px; background-color: rgba(255, 255, 255, 0.03); display: inline-block;"><img src="data:image/png;base64,{img_data}" style="height: 120px; width: auto; display: block;"></div>'
                            except Exception:
                                img_html = '<div style="height: 120px; width: 120px; display: flex; align-items: center; justify-content: center; color: #ccc; border: 1px solid rgba(128, 128, 128, 0.25); border-radius: 8px;">No Image</div>'
                        
                        # Render Card
                        st.markdown(f"""
<div style="border: 1px solid rgba(128, 128, 128, 0.15); border-radius: 12px; padding: 16px; margin-bottom: 16px; background-color: rgba(255, 255, 255, 0.02);">
<div style="text-align: center; font-size: 1rem; font-weight: 600; color: #b0b0b0; margin-bottom: 12px;">{label}</div>
<div style="display: flex; align-items: center; justify-content: space-between; gap: 20px;">
<div style="flex: 1; text-align: left; display: flex; flex-direction: column; gap: 3px;">
<div style="font-size: 1.3rem; font-weight: 700;">{cooled_system:,.0f} <span style="font-size: 0.85rem; color: #b0b0b0; font-weight: 400;">kWh</span></div>
<div style="font-size: 0.8rem; color: #888;">CF<sub>ann</sub> = {cf_overall:.1f}%</div>
<div style="font-size: 0.8rem; color: #888;">CF<sub>day</sub> = {cf_daylight:.1f}%</div>
<div style="margin-top: 2px;">{delta_html}</div>
</div>
<div style="flex-shrink: 0;">
{img_html}
</div>
</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("---")


        # --- Section 2: Annual Energy Generation & Loss Analysis ---
        st.header("📉 Annual Energy Generation & Loss Analysis")
        st.markdown("Comparison of **Useful Energy** vs **Thermal** and **Angular** Losses.")
        st.info("""
        **Thermal Loss:** Energy generation is inversely proportional to cell temperature. Higher temperatures reduce efficiency.
        **Angular Loss:** Energy reflected off the panel surface due to non-perpendicular incidence angles.
        """)
        
        # Prepare Data for Chart
        modes = [m[0] for m in metric_cols]
        yields = [totals.get(m[1], 0) for m in metric_cols]
        
        # Map keys for losses
        loss_therm_keys = [
            'Annual_Loss_Therm_Horiz_kWh_m2', 'Annual_Loss_Therm_Fixed_kWh_m2', 
            'Annual_Loss_Therm_Fixed_EW_kWh_m2', 'Annual_Loss_Therm_Fixed_NS_kWh_m2',
            'Annual_Loss_Therm_1Axis_Az_kWh_m2', 'Annual_Loss_Therm_1Axis_Polar_kWh_m2',
            'Annual_Loss_Therm_1Axis_Horizontal_kWh_m2',
            'Annual_Loss_Therm_1Axis_El_kWh_m2', 'Annual_Loss_Therm_2Axis_kWh_m2'
        ]
        loss_ang_keys = [
            'Annual_Loss_Ang_Horiz_kWh_m2', 'Annual_Loss_Ang_Fixed_kWh_m2',
            'Annual_Loss_Ang_Fixed_EW_kWh_m2', 'Annual_Loss_Ang_Fixed_NS_kWh_m2',
            'Annual_Loss_Ang_1Axis_Az_kWh_m2', 'Annual_Loss_Ang_1Axis_Polar_kWh_m2',
            'Annual_Loss_Ang_1Axis_Horizontal_kWh_m2',
            'Annual_Loss_Ang_1Axis_El_kWh_m2', 'Annual_Loss_Ang_2Axis_kWh_m2'
        ]
        
        therm_losses = [totals.get(k, 0) for k in loss_therm_keys]
        ang_losses = [totals.get(k, 0) for k in loss_ang_keys]
        
        fig_loss = go.Figure()
        fig_loss.add_trace(go.Bar(name='Useful Energy', x=modes, y=yields, marker_color='#2ecc71'))
        fig_loss.add_trace(go.Bar(name='Thermal Loss', x=modes, y=therm_losses, marker_color='#e74c3c'))
        fig_loss.add_trace(go.Bar(name='Angular Loss', x=modes, y=ang_losses, marker_color='#f1c40f'))
        
        fig_loss.update_layout(barmode='stack', title="Loss Analysis (Excluding Conversion Efficiency)", yaxis_title="Energy (kWh/m²)")
        st.plotly_chart(fig_loss, use_container_width=True)
        
        # --- Section 4: Energy Distribution (Pie Charts) ---
        st.header("🍰 Energy Distribution by Orientation")
        st.markdown("Proportion of **Total Available Solar Energy** converted to power vs. lost to various factors.")
        st.markdown("Legend shows: **Category (Absolute Value)**")
        
        # Helper to create pie chart with detailed legend
        def create_pie_chart(title, key_I, key_Ang, key_Therm, key_Yield):
            if key_I not in totals:
                return None
                
            I = totals[key_I]
            Ang = totals[key_Ang]
            Therm = totals[key_Therm]
            Yld = totals[key_Yield]
            Conv = I - Ang - Therm - Yld
            
            # Base values and labels
            values = [Yld, Therm, Ang, Conv]
            base_labels = ['Useful Power', 'Thermal Loss', 'Angular Loss', 'Conversion Loss']
            colors = ['#2ecc71', '#e74c3c', '#f1c40f', '#95a5a6'] # Green, Red, Yellow, Grey
            
            # Create labels with values for the legend
            legend_labels = [f"{label} ({val:.1f} kWh/m²)" for label, val in zip(base_labels, values)]
            
            fig = go.Figure(data=[go.Pie(
                labels=legend_labels, 
                values=values,
                marker=dict(colors=colors),
                textinfo='percent', # Show percent on the pie slices
                hoverinfo='label+value+percent',
                hole=0.3 # Donut style looks nice
            )])
            
            fig.update_layout(
                title_text=title,
                title_x=0.5, # Center title
                legend=dict(
                    orientation="h", 
                    yanchor="top", 
                    y=-0.1, 
                    xanchor="center", 
                    x=0.5
                ),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            return fig

        # Create Grid Layout (4 rows of 2)
        pie_configs = [
            ('Horizontal', 'Annual_I_Horizontal_kWh_m2', 'Annual_Loss_Ang_Horiz_kWh_m2', 'Annual_Loss_Therm_Horiz_kWh_m2', 'Annual_Yield_Horizontal_kWh_m2'),
            ('Fixed Custom', 'Annual_I_Fixed_kWh_m2', 'Annual_Loss_Ang_Fixed_kWh_m2', 'Annual_Loss_Therm_Fixed_kWh_m2', 'Annual_Yield_Fixed_kWh_m2'),
            ('Fixed E-W', 'Annual_I_Fixed_EW_kWh_m2', 'Annual_Loss_Ang_Fixed_EW_kWh_m2', 'Annual_Loss_Therm_Fixed_EW_kWh_m2', 'Annual_Yield_Fixed_EW_kWh_m2'),
            ('Fixed N-S', 'Annual_I_Fixed_NS_kWh_m2', 'Annual_Loss_Ang_Fixed_NS_kWh_m2', 'Annual_Loss_Therm_Fixed_NS_kWh_m2', 'Annual_Yield_Fixed_NS_kWh_m2'),
            ('1-Axis Azimuth', 'Annual_I_1Axis_Azimuth_kWh_m2', 'Annual_Loss_Ang_1Axis_Az_kWh_m2', 'Annual_Loss_Therm_1Axis_Az_kWh_m2', 'Annual_Yield_1Axis_Azimuth_kWh_m2'),
            ('1-Axis Polar', 'Annual_I_1Axis_Polar_kWh_m2', 'Annual_Loss_Ang_1Axis_Polar_kWh_m2', 'Annual_Loss_Therm_1Axis_Polar_kWh_m2', 'Annual_Yield_1Axis_Polar_kWh_m2'),
            ('1-Axis Horizontal', 'Annual_I_1Axis_Horizontal_kWh_m2', 'Annual_Loss_Ang_1Axis_Horizontal_kWh_m2', 'Annual_Loss_Therm_1Axis_Horizontal_kWh_m2', 'Annual_Yield_1Axis_Horizontal_kWh_m2'),
            ('1-Axis Elevation', 'Annual_I_1Axis_Elevation_kWh_m2', 'Annual_Loss_Ang_1Axis_El_kWh_m2', 'Annual_Loss_Therm_1Axis_El_kWh_m2', 'Annual_Yield_1Axis_Elevation_kWh_m2'),
            ('2-Axis', 'Annual_I_2Axis_kWh_m2', 'Annual_Loss_Ang_2Axis_kWh_m2', 'Annual_Loss_Therm_2Axis_kWh_m2', 'Annual_Yield_2Axis_kWh_m2')
        ]
        
        for i in range(0, len(pie_configs), 2):
            c1, c2 = st.columns(2)
            with c1:
                cfg = pie_configs[i]
                fig = create_pie_chart(*cfg)
                if fig: st.plotly_chart(fig, use_container_width=True)
                elif cfg[0] == 'Fixed Custom': st.info("Run simulation to see Fixed Custom data.")
                
            if i+1 < len(pie_configs):
                with c2:
                    cfg = pie_configs[i+1]
                    fig = create_pie_chart(*cfg)
                    if fig: st.plotly_chart(fig, use_container_width=True)
                    elif cfg[0] == 'Fixed Custom': st.info("Run simulation to see Fixed Custom data.")


        st.markdown("---")
        
        if latitude < 0:  # Southern Hemisphere
            season_lines = [
                (60, "Autumn"),   # ~Mar 1
                (152, "Winter"),  # ~Jun 1
                (244, "Spring"),  # ~Sep 1
                (335, "Summer")   # ~Dec 1
            ]
        else:  # Northern Hemisphere
            season_lines = [
                (60, "Spring"),   # ~Mar 1
                (152, "Summer"),  # ~Jun 1
                (244, "Autumn"),  # ~Sep 1
                (335, "Winter")   # ~Dec 1
            ]
        
        # --- Section 4: Annual Temperature & Generation Trends ---
        st.header("📅 Annual Temperature & Generation Trends")
        st.markdown("Daily average trends showing how **ambient temperature**, **cell temperature**, and **energy generation** vary throughout the year.")
        
        # Aggregate hourly data into daily averages
        # Note: The DataFrame df_hourly only contains rows for daylight hours (where elevation > 0).
        # Therefore, these averages are strictly over the daylight period, as requested.
        if df_hourly is not None:
            # Calculate Weighted Components for Smooth Averages
            # T_weighted = Sum(T * P) / Sum(P)
            # This eliminates "sawtooth" artifacts caused by discrete inclusion/exclusion of sunrise/sunset hours
            
            # 1. Create Weighted Columns
            # Weight Ambient Temp by Fixed Power (proxy for general solar availability)
            # This ensures T_amb is calculated over the same "effective" daylight window as cell temps
            if 'T_amb' in df_hourly.columns and 'P_Fixed' in df_hourly.columns:
                df_hourly['TxP_T_amb'] = df_hourly['T_amb'] * df_hourly['P_Fixed']

            temp_power_pairs = [
                ('T_cell_Horiz', 'P_Horiz'),
                ('T_cell_Fixed', 'P_Fixed'),
                ('T_cell_Fixed_EW', 'P_Fixed_EW'),
                ('T_cell_Fixed_NS', 'P_Fixed_NS'),
                ('T_cell_1Axis_Az', 'P_1Axis_Az'),
                ('T_cell_1Axis_Polar', 'P_1Axis_Polar'),
                ('T_cell_1Axis_Horiz', 'P_1Axis_Horiz'),
                ('T_cell_1Axis_El', 'P_1Axis_El'),
                ('T_cell_2Axis', 'P_2Axis')
            ]
            
            for t_col, p_col in temp_power_pairs:
                if t_col in df_hourly.columns and p_col in df_hourly.columns:
                    df_hourly[f'TxP_{t_col}'] = df_hourly[t_col] * df_hourly[p_col]

            # 2. Aggregate Sums
            agg_dict = {
                'TxP_T_amb': 'sum', # Weighted Ambient Sum
                'P_Horiz': 'sum',
                'P_Fixed': 'sum',
                'P_Fixed_EW': 'sum',
                'P_Fixed_NS': 'sum',
                'P_1Axis_Az': 'sum',
                'P_1Axis_Polar': 'sum',
                'P_1Axis_Horiz': 'sum',
                'P_1Axis_El': 'sum',
                'P_2Axis': 'sum',
                'P_Horiz_25C': 'sum',
                'P_Fixed_25C': 'sum',
                'P_Fixed_EW_25C': 'sum',
                'P_Fixed_NS_25C': 'sum',
                'P_1Axis_Az_25C': 'sum',
                'P_1Axis_Polar_25C': 'sum',
                'P_1Axis_Horiz_25C': 'sum',
                'P_1Axis_El_25C': 'sum',
                'P_2Axis_25C': 'sum'
            }
            
            # Add TxP columns to aggregation
            for t_col, _ in temp_power_pairs:
                if f'TxP_{t_col}' in df_hourly.columns:
                    agg_dict[f'TxP_{t_col}'] = 'sum'

            df_daily = df_hourly.groupby('Day').agg(agg_dict).reset_index()
            
            # 3. Calculate Weighted Averages
            
            # Ambient (Weighted by Fixed Power)
            df_daily['T_amb'] = df_daily.apply(
                lambda row: row['TxP_T_amb'] / row['P_Fixed'] if row['P_Fixed'] > 0 else 0, 
                axis=1
            )

            for t_col, p_col in temp_power_pairs:
                if f'TxP_{t_col}' in df_daily.columns:
                    # Avoid division by zero
                    df_daily[t_col] = df_daily.apply(
                        lambda row: row[f'TxP_{t_col}'] / row[p_col] if row[p_col] > 0 else 0, 
                        axis=1
                    )
            
            # Note: Removed 14-day rolling average smoothing. 
            # The weighted average method is robust enough to produce smooth curves without artificial smoothing.
            
            # Convert daily power from W/m² to kWh/m² (sum of hourly W/m² = Wh/m², then /1000)
            power_cols = [col for col in df_daily.columns if col.startswith('P_') and not col.startswith('TxP_')]
            for col in power_cols:
                df_daily[col] = df_daily[col] / 1000  # Wh/m² to kWh/m²
        
        
        # Mapping of modes to columns (name, T_cell, P_out, P_at_25C)
        mode_mapping = [
            ('Horizontal', 'T_cell_Horiz', 'P_Horiz', 'P_Horiz_25C'),
            ('Fixed Tilt', 'T_cell_Fixed', 'P_Fixed', 'P_Fixed_25C'),
            ('Fixed E-W', 'T_cell_Fixed_EW', 'P_Fixed_EW', 'P_Fixed_EW_25C'),
            ('Fixed N-S', 'T_cell_Fixed_NS', 'P_Fixed_NS', 'P_Fixed_NS_25C'),
            ('1-Axis Azimuth', 'T_cell_1Axis_Az', 'P_1Axis_Az', 'P_1Axis_Az_25C'),
            ('1-Axis Polar', 'T_cell_1Axis_Polar', 'P_1Axis_Polar', 'P_1Axis_Polar_25C'),
            ('1-Axis Horizontal', 'T_cell_1Axis_Horiz', 'P_1Axis_Horiz', 'P_1Axis_Horiz_25C'),
            ('1-Axis Elevation', 'T_cell_1Axis_El', 'P_1Axis_El', 'P_1Axis_El_25C'),
            ('2-Axis', 'T_cell_2Axis', 'P_2Axis', 'P_2Axis_25C')
        ]
        
        # Create tabs for each orientation
        tabs = st.tabs([name for name, _, _, _ in mode_mapping])
        
        for idx, (mode_name, t_cell_col, power_col, power_25c_col) in enumerate(mode_mapping):
            with tabs[idx]:
                # Skip if Fixed Tilt data not available
                if mode_name == 'Fixed Tilt' and t_cell_col not in df_daily.columns:
                    st.info("Run simulation with custom tilt/azimuth to see Fixed Tilt trends.")
                    continue
                
                # Create dual-axis figure
                fig = go.Figure()
                
                # Add ambient temperature trace (left y-axis)
                fig.add_trace(go.Scatter(
                    x=df_daily['Day'],
                    y=df_daily['T_amb'],
                    name='Ambient Temp',
                    line=dict(color='#95a5a6', width=2, dash='dot'),
                    yaxis='y1'
                ))
                
                # Add cell temperature trace (left y-axis)
                fig.add_trace(go.Scatter(
                    x=df_daily['Day'],
                    y=df_daily[t_cell_col],
                    name='Cell Temp',
                    line=dict(color='#e74c3c', width=2, dash='dot'),
                    yaxis='y1'
                ))
                
                # Add power generation trace (right y-axis)
                fig.add_trace(go.Scatter(
                    x=df_daily['Day'],
                    y=df_daily[power_col],
                    name='Daily Energy (Actual)',
                    line=dict(color='#2ecc71', width=3),
                    yaxis='y2',
                    fill='tozeroy',
                    fillcolor='rgba(46, 204, 113, 0.1)'
                ))
                
                # Add cooled power generation trace (right y-axis) - shows benefit of cooling
                fig.add_trace(go.Scatter(
                    x=df_daily['Day'],
                    y=df_daily[power_25c_col],
                    name='Daily Energy (if Cooled to 25°C)',
                    line=dict(color='#3498db', width=2),
                    yaxis='y2'
                ))
                
                # Add seasonal markers
                for day, season_name in season_lines:
                    fig.add_vline(
                        x=day,
                        line=dict(color='rgba(128, 128, 128, 0.3)', width=1, dash='dash'),
                        annotation_text=season_name,
                        annotation_position="top"
                    )
                
                # Update layout with dual y-axes
                fig.update_layout(
                    title=f"{mode_name} - Annual Trends",
                    xaxis=dict(title="Day of Year", range=[1, 365]),
                    yaxis=dict(
                        title=dict(
                            text="Temperature (°C)",
                            font=dict(color="#3498db")
                        ),
                        tickfont=dict(color="#3498db"),
                        range=[-10, 80]
                    ),
                    yaxis2=dict(
                        title=dict(
                            text="Energy Generation (kWh/m²/day)",
                            font=dict(color="#2ecc71")
                        ),
                        tickfont=dict(color="#2ecc71"),
                        overlaying='y',
                        side='right',
                        range=[0, 2]
                    ),
                    hovermode='x unified',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.08,
                        xanchor="right",
                        x=1
                    ),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)


        st.markdown("---")
        
        # --- Section 5: Interactive Hourly Day View ---
        st.header("⏱️ Hourly Performance for Selected Day")
        st.markdown("Use the slider to explore **hourly generation, temperatures, and cooling benefit** for any day of the year.")
        
        # Slider for day selection (default to summer solstice for demonstration)
        if latitude < 0:
            default_day = 355  # Southern Hemisphere summer (Dec 21)
            solstice_label = "Summer Solstice"
        else:
            default_day = 172  # Northern Hemisphere summer (Jun 21)
            solstice_label = "Summer Solstice"
        
        selected_day = st.slider(
            "Select Day of Year",
            min_value=1,
            max_value=365,
            value=default_day,
            help=f"Choose any day from 1 (Jan 1) to 365 (Dec 31). Default is {solstice_label} (Day {default_day})."
        )
        
        # Show selected date info
        import datetime
        date_obj = datetime.datetime(2024, 1, 1) + datetime.timedelta(days=selected_day - 1)
        date_str = date_obj.strftime("%B %d")
        st.info(f"**Day {selected_day}** corresponds to **{date_str}** (in a non-leap year)")
        
        # Create tabs for each tracker type
        hourly_tabs = st.tabs([name for name, _, _, _ in mode_mapping])
        
        for idx, (tab, (mode_name, t_cell_col, power_col, power_25c_col)) in enumerate(zip(hourly_tabs, mode_mapping)):
            with tab:
                # Filter hourly data for selected day
                df_day = df_hourly[df_hourly['Day'] == selected_day].copy()
                
                if len(df_day) == 0:
                    st.warning(f"No daylight hours on Day {selected_day} for this latitude. Sun does not rise.")
                else:
                    # Create figure with dual y-axes
                    fig = go.Figure()
                    
                    # Add 2-Axis tracker as faded background reference (except on 2-Axis tab itself)
                    if mode_name != '2-Axis':
                        # Background: 2-Axis power (faded, solid)
                        fig.add_trace(go.Scatter(
                            x=df_day['Hour'],
                            y=df_day['P_2Axis'] / 1000,
                            name='2-Axis (Reference)',
                            line=dict(color='#e74c3c', width=2),
                            opacity=0.3,
                            yaxis='y1'
                        ))
                        
                        # Background: 2-Axis cooled power (faded, solid)
                        fig.add_trace(go.Scatter(
                            x=df_day['Hour'],
                            y=df_day['P_2Axis_25C'] / 1000,
                            name='2-Axis Cooled (Reference)',
                            line=dict(color='#3498db', width=2),
                            opacity=0.3,
                            yaxis='y1'
                        ))
                        
                        # Background: 2-Axis cell temp (faded, dotted)
                        fig.add_trace(go.Scatter(
                            x=df_day['Hour'],
                            y=df_day['T_cell_2Axis'],
                            name='2-Axis Cell Temp (Reference)',
                            line=dict(color='#f39c12', width=1.5, dash='dot'),
                            opacity=0.3,
                            yaxis='y2'
                        ))
                    
                    # Left y-axis: Power generation (kW/m²) - solid lines
                    fig.add_trace(go.Scatter(
                        x=df_day['Hour'],
                        y=df_day[power_col] / 1000,  # W/m² to kW/m²
                        name=f'{mode_name} Power',
                        line=dict(color='#e74c3c', width=3),
                        yaxis='y1'
                    ))
                    
                    # Add cooled power (if at 25°C) - solid line
                    fig.add_trace(go.Scatter(
                        x=df_day['Hour'],
                        y=df_day[power_25c_col] / 1000,  # W/m² to kW/m²
                        name=f'{mode_name} Power (if Cooled to 25°C)',
                        line=dict(color='#3498db', width=2),
                        yaxis='y1'
                    ))
                    
                    # Right y-axis: Temperatures (°C) - dotted lines
                    fig.add_trace(go.Scatter(
                        x=df_day['Hour'],
                        y=df_day[t_cell_col],
                        name='Cell Temperature',
                        line=dict(color='#f39c12', width=2, dash='dot'),
                        yaxis='y2'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df_day['Hour'],
                        y=df_day['T_amb'],
                        name='Ambient Temperature',
                        line=dict(color='#95a5a6', width=2, dash='dot'),
                        yaxis='y2'
                    ))
                    
                    # Update layout with dual y-axes
                    fig.update_layout(
                        title=f"{mode_name} - Hourly Performance on Day {selected_day} ({date_str})",
                        xaxis=dict(
                            title="Hour of Day",
                            gridcolor='rgba(128, 128, 128, 0.2)',
                            range=[df_day['Hour'].min() - 0.5, df_day['Hour'].max() + 0.5]
                        ),
                        yaxis=dict(
                            title=dict(text="Power Output (kW/m²)", font=dict(color='#e74c3c')),
                            tickfont=dict(color='#e74c3c'),
                            gridcolor='rgba(128, 128, 128, 0.2)'
                        ),
                        yaxis2=dict(
                            title=dict(text="Temperature (°C)", font=dict(color='#f39c12')),
                            tickfont=dict(color='#f39c12'),
                            overlaying='y',
                            side='right'
                        ),
                        hovermode='x unified',
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        height=450
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show summary stats for this day
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        daily_energy = df_day[power_col].sum() / 1000  # Wh to kWh
                        st.metric("Daily Energy", f"{daily_energy:.2f} kWh/m²")
                    with col2:
                        daily_energy_25c = df_day[power_25c_col].sum() / 1000
                        cooling_benefit = daily_energy_25c - daily_energy
                        st.metric("Cooling Benefit", f"{cooling_benefit:.2f} kWh/m²", delta=f"{cooling_benefit/daily_energy*100:.1f}%")
                    with col3:
                        max_temp = df_day[t_cell_col].max()
                        st.metric("Peak Cell Temp", f"{max_temp:.1f} °C")
                    with col4:
                        avg_temp = df_day[t_cell_col].mean()
                        st.metric("Avg Cell Temp", f"{avg_temp:.1f} °C")

        st.markdown("---")

        # --- Section 6: Hourly Data ---
        with st.expander("📋 View Hourly Data"):
            st.dataframe(df_hourly)
            
        # Download Button
        csv = df_hourly.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Hourly Data as CSV",
            data=csv,
            file_name='solar_model_output.csv',
            mime='text/csv',
        )

else:
    if st.session_state['user_mode'] == 'Advanced':
        st.info("👈 Enter your location in the sidebar and click **Run Simulation** to see the results.")
