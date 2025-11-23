import streamlit as st
import pandas as pd
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
            st.info("🔍 Finding optimal tilt angle...")
            
            lat_abs = abs(latitude)
            # Test from (latitude - 5°) to (latitude + 5°), clamped to 0-90°
            tilt_min = max(0, lat_abs - 5)
            tilt_max = min(90, lat_abs + 5)
            
            best_tilt = lat_abs
            best_yield = 0
            
            # Quick optimization: test every 1 degree
            for test_tilt in range(int(tilt_min), int(tilt_max) + 1):
                test_model = SolarModel(latitude, longitude)
                _, test_totals = test_model.generate_annual_profile(
                    fixed_tilt=float(test_tilt),
                    fixed_azimuth=azimuth,
                    efficiency=efficiency
                )
                test_yield = test_totals['Annual_Yield_Fixed_kWh_m2']
                
                if test_yield > best_yield:
                    best_yield = test_yield
                    best_tilt = test_tilt
            
            tilt_ideal = float(best_tilt)
            
            # 2. Run Model 1: Standard Fixed (25 deg)
            model_std = SolarModel(latitude, longitude)
            df_std, totals_std = model_std.generate_annual_profile(
                fixed_tilt=tilt_std, 
                fixed_azimuth=azimuth, 
                efficiency=efficiency
            )
            
            # 3. Run Model 2: Optimal Fixed (calculated above)
            model_ideal = SolarModel(latitude, longitude)
            df_ideal, totals_ideal = model_ideal.generate_annual_profile(
                fixed_tilt=tilt_ideal, 
                fixed_azimuth=azimuth, 
                efficiency=efficiency
            )
            
            # 4. Display Results
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
            # Approx 4.5 kWh per person per day
            daily_usage_kwh = num_people * 4.5
            
            # Typical residential profile weights (0-23h)
            # Morning peak (7-9am), Evening peak (5-9pm)
            profile_weights = [
                0.02, 0.02, 0.02, 0.02, 0.02, 0.03, # 0-5 (Night)
                0.05, 0.08, 0.06, 0.04, 0.03, 0.03, # 6-11 (Morning Peak)
                0.03, 0.03, 0.03, 0.04, 0.06, 0.09, # 12-17 (Day/Early Eve)
                0.10, 0.09, 0.06, 0.04, 0.03, 0.03  # 18-23 (Evening Peak)
            ]
            # Normalize just in case
            total_weight = sum(profile_weights)
            profile_weights = [w/total_weight for w in profile_weights]
            
            demand_profile_kw = [w * daily_usage_kwh for w in profile_weights]
            
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
            
            # 3. Create Visualization (2x2 Grid)
            from plotly.subplots import make_subplots
            
            seasons = ['Summer', 'Autumn', 'Winter', 'Spring']
            fig_seasonal = make_subplots(rows=2, cols=2, subplot_titles=seasons, vertical_spacing=0.15)
            
            for i, season in enumerate(seasons):
                row = (i // 2) + 1
                col = (i % 2) + 1
                
                # Solar Data
                solar_data = seasonal_profiles[seasonal_profiles['Season'] == season]['System_Gen_kW'].values
                hours = list(range(24))
                
                # Add Solar Area
                fig_seasonal.add_trace(
                    go.Scatter(x=hours, y=solar_data, fill='tozeroy', name='Solar Generation',
                               line=dict(color='#f1c40f'), showlegend=(i==0)),
                    row=row, col=col
                )
                
                # Add Demand Line
                fig_seasonal.add_trace(
                    go.Scatter(x=hours, y=demand_profile_kw, mode='lines', name='Household Demand',
                               line=dict(color='#e74c3c', width=3), showlegend=(i==0)),
                    row=row, col=col
                )
                
                fig_seasonal.update_xaxes(title_text="Hour of Day", row=row, col=col, tickvals=[0,6,12,18,23])
                fig_seasonal.update_yaxes(title_text="Power (kW)", row=row, col=col)

            fig_seasonal.update_layout(height=600, title_text="Average Daily Profiles by Season")
            st.plotly_chart(fig_seasonal, use_container_width=True)
            
            st.info(f"Analysis based on {hemisphere} Hemisphere location. Azimuth set to {'North (0°)' if azimuth==0 else 'South (180°)'}.")

# --- Advanced Version (Existing App) ---
elif st.session_state['user_mode'] == 'Advanced':
    st.sidebar.button("🔄 Switch Mode", on_click=lambda: st.session_state.update({'user_mode': None}))
    
    # Title and Intro
    st.title("☀️ Solar Resource & PV Performance Model")
    st.markdown("""
    This tool simulates the hourly solar energy yield for different collector orientations based on the **Ryan Coble-Neal Thesis**.
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
    if st.sidebar.button("Run Simulation", type="primary"):
        with st.spinner("Calculating annual profile..."):
            # Initialize Model
            model = SolarModel(latitude=latitude, longitude=longitude)
            
            # Run Simulation
            df, totals = model.generate_annual_profile(fixed_tilt=fixed_tilt, fixed_azimuth=fixed_azimuth, efficiency=efficiency_percent/100.0)
            
            # Store in session state to persist
            st.session_state['df'] = df
            st.session_state['totals'] = totals
            st.session_state['run_done'] = True
    
    # Main Content
    if st.session_state.get('run_done'):
        totals = st.session_state['totals']
        df = st.session_state['df']
        
        # --- Section 1: Key Metrics ---
        st.header("📊 Annual Energy Yield")
        
        # Define columns for layout
        # Order: Horizontal, Fixed Custom, Fixed E-W, Fixed N-S, 1-Axis Az, 1-Axis Polar, 1-Axis El, 2-Axis
        cols = st.columns(8)
        
        metric_cols = [
            ('Horizontal', 'Annual_Yield_Horizontal_kWh_m2', 'Horizontal'),
            ('Fixed Custom', 'Annual_Yield_Fixed_kWh_m2', 'Fixed Custom'),
            ('Fixed E-W', 'Annual_Yield_Fixed_EW_kWh_m2', 'Fixed East-West'),
            ('Fixed N-S', 'Annual_Yield_Fixed_NS_kWh_m2', 'Fixed North-South'),
            ('1-Axis Azimuth', 'Annual_Yield_1Axis_Azimuth_kWh_m2', '1-Axis Azimuth'),
            ('1-Axis Polar', 'Annual_Yield_1Axis_Polar_kWh_m2', '1-Axis Polar'),
            ('1-Axis Elevation', 'Annual_Yield_1Axis_Elevation_kWh_m2', '1-Axis Elevation'),
            ('2-Axis', 'Annual_Yield_2Axis_kWh_m2', '2-Axis')
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

        for i, (label, key, help_text) in enumerate(metric_cols):
            with cols[i]:
                val = totals.get(key, 0)
                
                # Calculate Delta % vs 2-Axis
                ref_val = totals.get('Annual_Yield_2Axis_kWh_m2', 1)
                if ref_val > 0:
                    pct = (val / ref_val) * 100
                    delta_val = pct - 100 # e.g. 80% -> -20%
                else:
                    delta_val = 0
                    
                is_ref = (label == '2-Axis')
                
                display_custom_metric(
                    label=label, 
                    value=val, 
                    unit="kWh/m²", 
                    delta_val=delta_val if not is_ref else None,
                    delta_text="%",
                    is_ref=is_ref
                )
                
                # Add schematic image
                if label == 'Horizontal':
                    st.image("C:/Users/Ryan/.gemini/antigravity/brain/855624a4-2414-475b-99c8-2ec59a5dcf49/horizontal_panel_schematic_1763815355294.png", use_container_width=True)
                elif label == 'Fixed Custom':
                    st.image("C:/Users/Ryan/.gemini/antigravity/brain/855624a4-2414-475b-99c8-2ec59a5dcf49/fixed_custom_schematic_1763815554067.png", use_container_width=True)
                elif label == '1-Axis Azimuth':
                    st.image("C:/Users/Ryan/.gemini/antigravity/brain/855624a4-2414-475b-99c8-2ec59a5dcf49/one_axis_azimuth_schematic_1763815278060.png", use_container_width=True)
                elif label == '1-Axis Elevation':
                    st.image("C:/Users/Ryan/.gemini/antigravity/brain/855624a4-2414-475b-99c8-2ec59a5dcf49/one_axis_elevation_schematic_1763815294214.png", use_container_width=True)
                elif label == '2-Axis':
                    st.image("C:/Users/Ryan/.gemini/antigravity/brain/855624a4-2414-475b-99c8-2ec59a5dcf49/two_axis_tracking_schematic_1763815319309.png", use_container_width=True)
                elif label == '1-Axis Polar':
                    st.info("🖼️ 1-Axis Polar\n(Image Coming Soon)")
                elif label == 'Fixed E-W':
                    st.info("🖼️ Fixed East-West\n(Image Coming Soon)")
                elif label == 'Fixed N-S':
                    st.info("🖼️ Fixed North-South\n(Image Coming Soon)")

                # Capacity Factor Stats
                # Map key to CF suffix
                cf_key_map = {
                    'Annual_Yield_Horizontal_kWh_m2': 'Horizontal',
                    'Annual_Yield_Fixed_kWh_m2': 'Fixed',
                    'Annual_Yield_Fixed_EW_kWh_m2': 'Fixed_EW',
                    'Annual_Yield_Fixed_NS_kWh_m2': 'Fixed_NS',
                    'Annual_Yield_1Axis_Azimuth_kWh_m2': '1Axis_Azimuth',
                    'Annual_Yield_1Axis_Polar_kWh_m2': '1Axis_Polar',
                    'Annual_Yield_1Axis_Elevation_kWh_m2': '1Axis_Elevation',
                    'Annual_Yield_2Axis_kWh_m2': '2Axis'
                }
                cf_suffix = cf_key_map.get(key)
                cf_overall = totals.get(f"CF_Overall_{cf_suffix}", 0)
                cf_daylight = totals.get(f"CF_Daylight_{cf_suffix}", 0)
                
                st.markdown(f"""
                <div style="font-size: 0.75rem; color: #666; margin-top: 2px;">
                CF (24h): <b>{cf_overall:.1f}%</b><br>
                CF (Day): <b>{cf_daylight:.1f}%</b>
                </div>
                """, unsafe_allow_html=True)

        # Insight for Capacity Factors
        st.markdown("### 💡 Capacity Factor Insight")
        st.info(f"""
        **Daylight Capacity Factor** reveals the system's efficiency specifically during sun-up hours. 
        
        For your **{system_capacity_kw} kW** system, it is calculated as:  
        `Daylight CF = (Annual Energy Yield) / ({system_capacity_kw} kW × Daylight Hours)`
        
        This metric filters out night-time hours to show how effectively the tracking system captures available solar energy when it matters most.
        """)

        st.markdown("---")

        # --- Section 1.5: Total System Yield ---
        st.header(f"⚡ Your {system_capacity_kw} kW System Annual Energy Yield")
        
        # Calculate Array Area (m2) = Rated Power (kW) / Efficiency (kW/m2)
        rated_power_per_m2 = efficiency_percent / 100.0
        array_area_m2 = system_capacity_kw / rated_power_per_m2
        
        st.markdown(f"Based on your **{efficiency_percent}%** efficient panels, your system requires approximately **{array_area_m2:.1f} m²** of active solar area.")
        
        sys_cols = st.columns(8)
        
        # Reference Yield for Delta (2-Axis)
        ref_yield_per_m2 = totals.get('Annual_Yield_2Axis_kWh_m2', 0)
        
        for i, (label, key, _) in enumerate(metric_cols):
            with sys_cols[i]:
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
                
                display_custom_metric(
                    label=label, 
                    value=total_energy_kwh, 
                    unit="kWh", 
                    delta_val=delta_val if not is_ref else None,
                    delta_text=" kWh",
                    is_ref=is_ref
                )

        st.markdown("---")

        # --- Section 2: Performance Comparison Chart ---
        st.header("📈 Performance Comparison")
        
        # Prepare Data for Chart
        modes = [m[0] for m in metric_cols]
        yields = [totals.get(m[1], 0) for m in metric_cols]
        
        fig_perf = px.bar(
            x=modes, 
            y=yields, 
            labels={'x': 'Collector Orientation', 'y': 'Annual Energy Yield (kWh/m²)'},
            title="Annual PV Energy Yield by Orientation",
            color=yields,
            color_continuous_scale='Oranges'
        )
        st.plotly_chart(fig_perf, use_container_width=True)
        
        # --- Section 3: Loss Analysis ---
        st.header("📉 Loss Analysis")
        st.markdown("Comparison of **Useful Energy** vs **Thermal** and **Angular** Losses.")
        st.info("""
        **Thermal Loss:** Power lost due to panel temperature rising above 25°C.
        **Angular Loss:** Energy reflected off the panel surface due to non-perpendicular incidence angles.
        """)
        
        # Map keys for losses
        loss_therm_keys = [
            'Annual_Loss_Therm_Horiz_kWh_m2', 'Annual_Loss_Therm_Fixed_kWh_m2', 
            'Annual_Loss_Therm_Fixed_EW_kWh_m2', 'Annual_Loss_Therm_Fixed_NS_kWh_m2',
            'Annual_Loss_Therm_1Axis_Az_kWh_m2', 'Annual_Loss_Therm_1Axis_Polar_kWh_m2',
            'Annual_Loss_Therm_1Axis_El_kWh_m2', 'Annual_Loss_Therm_2Axis_kWh_m2'
        ]
        loss_ang_keys = [
            'Annual_Loss_Ang_Horiz_kWh_m2', 'Annual_Loss_Ang_Fixed_kWh_m2',
            'Annual_Loss_Ang_Fixed_EW_kWh_m2', 'Annual_Loss_Ang_Fixed_NS_kWh_m2',
            'Annual_Loss_Ang_1Axis_Az_kWh_m2', 'Annual_Loss_Ang_1Axis_Polar_kWh_m2',
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

        # --- Section 5: Hourly Data ---
        with st.expander("📋 View Hourly Data"):
            st.dataframe(df)
            
        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Hourly Data as CSV",
            data=csv,
            file_name='solar_model_output.csv',
            mime='text/csv',
        )

else:
    if st.session_state['user_mode'] == 'Advanced':
        st.info("👈 Enter your location in the sidebar and click **Run Simulation** to see the results.")
