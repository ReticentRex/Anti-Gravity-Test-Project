import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from solar_model import SolarModel

# Page Config
st.set_page_config(
    page_title="Solar Resource Model",
    page_icon="☀️",
    layout="wide"
)

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
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Horizontal", f"{totals['Annual_Yield_Horizontal_kWh_m2']:.1f} kWh/m²", 
                  delta=f"{totals['Ratio_Yield_Horizontal_vs_2Axis_Percent']:.1f}% of 2-Axis")
        st.image("C:/Users/Ryan/.gemini/antigravity/brain/855624a4-2414-475b-99c8-2ec59a5dcf49/horizontal_panel_schematic_1763815355294.png", use_container_width=True)
        st.markdown(f"**Overall CF:** {totals['CF_Overall_Horizontal']:.1f}%")
        st.markdown(f"**Daylight CF:** {totals['CF_Daylight_Horizontal']:.1f}%")
        
    with col2:
        st.metric("1-Axis Azimuth", f"{totals['Annual_Yield_1Axis_Azimuth_kWh_m2']:.1f} kWh/m²",
                  delta=f"{totals['Ratio_Yield_1Axis_Azimuth_vs_2Axis_Percent']:.1f}% of 2-Axis")
        st.image("C:/Users/Ryan/.gemini/antigravity/brain/855624a4-2414-475b-99c8-2ec59a5dcf49/one_axis_azimuth_schematic_1763815278060.png", use_container_width=True)
        st.markdown(f"**Overall CF:** {totals['CF_Overall_1Axis_Azimuth']:.1f}%")
        st.markdown(f"**Daylight CF:** {totals['CF_Daylight_1Axis_Azimuth']:.1f}%")
        
    with col3:
        st.metric("1-Axis Elevation", f"{totals['Annual_Yield_1Axis_Elevation_kWh_m2']:.1f} kWh/m²",
                  delta=f"{totals['Ratio_Yield_1Axis_Elevation_vs_2Axis_Percent']:.1f}% of 2-Axis")
        st.image("C:/Users/Ryan/.gemini/antigravity/brain/855624a4-2414-475b-99c8-2ec59a5dcf49/one_axis_elevation_schematic_1763815294214.png", use_container_width=True)
        st.markdown(f"**Overall CF:** {totals['CF_Overall_1Axis_Elevation']:.1f}%")
        st.markdown(f"**Daylight CF:** {totals['CF_Daylight_1Axis_Elevation']:.1f}%")
        
    with col4:
        st.metric("Fixed Custom", f"{totals['Annual_Yield_Fixed_kWh_m2']:.1f} kWh/m²",
                  delta=f"{totals['Ratio_Yield_Fixed_vs_2Axis_Percent']:.1f}% of 2-Axis")
        st.image("C:/Users/Ryan/.gemini/antigravity/brain/855624a4-2414-475b-99c8-2ec59a5dcf49/fixed_custom_schematic_1763815554067.png", use_container_width=True)
        st.markdown(f"**Overall CF:** {totals['CF_Overall_Fixed']:.1f}%")
        st.markdown(f"**Daylight CF:** {totals['CF_Daylight_Fixed']:.1f}%")

    with col5:
        st.metric("2-Axis Tracking", f"{totals['Annual_Yield_2Axis_kWh_m2']:.1f} kWh/m²", 
                  delta="Reference")
        st.image("C:/Users/Ryan/.gemini/antigravity/brain/855624a4-2414-475b-99c8-2ec59a5dcf49/two_axis_tracking_schematic_1763815319309.png", use_container_width=True)
        st.markdown(f"**Overall CF:** {totals['CF_Overall_2Axis']:.1f}%")
        st.markdown(f"**Daylight CF:** {totals['CF_Daylight_2Axis']:.1f}%")

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
    # Efficiency is in %, so divide by 100. Rated Power of 1 m2 at STC is 1 kW * Efficiency.
    # So Rated_Power_m2 = efficiency_percent / 100.
    rated_power_per_m2 = efficiency_percent / 100.0
    array_area_m2 = system_capacity_kw / rated_power_per_m2
    
    st.markdown(f"Based on your **{efficiency_percent}%** efficient panels, your system requires approximately **{array_area_m2:.1f} m²** of active solar area.")
    
    col_sys1, col_sys2, col_sys3, col_sys4, col_sys5 = st.columns(5)
    
    def display_system_metric(col, label, yield_per_m2, ref_yield_per_m2):
        total_yield = yield_per_m2 * array_area_m2
        ref_total = ref_yield_per_m2 * array_area_m2
        delta_val = total_yield - ref_total
        
        with col:
            st.metric(
                label=label,
                value=f"{total_yield:,.0f} kWh",
                delta=f"{delta_val:,.0f} kWh vs 2-Axis" if label != "2-Axis Tracking" else "Reference"
            )

    display_system_metric(col_sys1, "Horizontal", totals['Annual_Yield_Horizontal_kWh_m2'], totals['Annual_Yield_2Axis_kWh_m2'])
    display_system_metric(col_sys2, "1-Axis Azimuth", totals['Annual_Yield_1Axis_Azimuth_kWh_m2'], totals['Annual_Yield_2Axis_kWh_m2'])
    display_system_metric(col_sys3, "1-Axis Elevation", totals['Annual_Yield_1Axis_Elevation_kWh_m2'], totals['Annual_Yield_2Axis_kWh_m2'])
    display_system_metric(col_sys4, "Fixed Custom", totals['Annual_Yield_Fixed_kWh_m2'], totals['Annual_Yield_2Axis_kWh_m2'])
    display_system_metric(col_sys5, "2-Axis Tracking", totals['Annual_Yield_2Axis_kWh_m2'], totals['Annual_Yield_2Axis_kWh_m2'])

    st.markdown("---")

    # --- Section 2: Performance Comparison Chart ---
    st.header("📈 Performance Comparison")
    
    # Prepare Data for Chart
    modes = ['Horizontal', '1-Axis Azimuth', '1-Axis Elevation', 'Fixed Custom', '2-Axis']
    yields = [
        totals['Annual_Yield_Horizontal_kWh_m2'],
        totals['Annual_Yield_1Axis_Azimuth_kWh_m2'],
        totals['Annual_Yield_1Axis_Elevation_kWh_m2'],
        totals['Annual_Yield_Fixed_kWh_m2'],
        totals['Annual_Yield_2Axis_kWh_m2']
    ]
    
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
    # --- Section 3: Loss Analysis (Stacked Bar) ---
    st.header("📉 Loss Analysis")
    st.markdown("Comparison of **Useful Energy** vs **Thermal** and **Angular** Losses.")
    
    # Prepare Data for Stacked Bar
    # Note: This does NOT include Conversion Loss (Efficiency Limit) to keep the scale readable
    # relative to the useful output.
    
    fig_loss = go.Figure()
    fig_loss.add_trace(go.Bar(name='Useful Energy', x=modes, y=yields, marker_color='#2ecc71'))
    fig_loss.add_trace(go.Bar(name='Thermal Loss', x=modes, y=[
        totals['Annual_Loss_Therm_Horiz_kWh_m2'],
        totals['Annual_Loss_Therm_1Axis_Az_kWh_m2'],
        totals['Annual_Loss_Therm_1Axis_El_kWh_m2'],
        totals['Annual_Loss_Therm_Fixed_kWh_m2'],
        totals['Annual_Loss_Therm_2Axis_kWh_m2']
    ], marker_color='#e74c3c'))
    fig_loss.add_trace(go.Bar(name='Angular Loss', x=modes, y=[
        totals['Annual_Loss_Ang_Horiz_kWh_m2'],
        totals['Annual_Loss_Ang_1Axis_Az_kWh_m2'],
        totals['Annual_Loss_Ang_1Axis_El_kWh_m2'],
        totals['Annual_Loss_Ang_Fixed_kWh_m2'],
        totals['Annual_Loss_Ang_2Axis_kWh_m2']
    ], marker_color='#f1c40f'))
    
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

    # Create Grid Layout
    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        fig = create_pie_chart('Horizontal', 'Annual_I_Horizontal_kWh_m2', 'Annual_Loss_Ang_Horiz_kWh_m2', 'Annual_Loss_Therm_Horiz_kWh_m2', 'Annual_Yield_Horizontal_kWh_m2')
        if fig: st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        fig = create_pie_chart('1-Axis Azimuth', 'Annual_I_1Axis_Azimuth_kWh_m2', 'Annual_Loss_Ang_1Axis_Az_kWh_m2', 'Annual_Loss_Therm_1Axis_Az_kWh_m2', 'Annual_Yield_1Axis_Azimuth_kWh_m2')
        if fig: st.plotly_chart(fig, use_container_width=True)

    # Row 2
    c3, c4 = st.columns(2)
    with c3:
        fig = create_pie_chart('1-Axis Elevation', 'Annual_I_1Axis_Elevation_kWh_m2', 'Annual_Loss_Ang_1Axis_El_kWh_m2', 'Annual_Loss_Therm_1Axis_El_kWh_m2', 'Annual_Yield_1Axis_Elevation_kWh_m2')
        if fig: st.plotly_chart(fig, use_container_width=True)
        
    with c4:
        fig = create_pie_chart('Fixed Custom', 'Annual_I_Fixed_kWh_m2', 'Annual_Loss_Ang_Fixed_kWh_m2', 'Annual_Loss_Therm_Fixed_kWh_m2', 'Annual_Yield_Fixed_kWh_m2')
        if fig: 
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Run simulation to see Fixed Custom data.")

    # Row 3
    c5, c6 = st.columns(2)
    with c5:
        fig = create_pie_chart('2-Axis Tracking', 'Annual_I_2Axis_kWh_m2', 'Annual_Loss_Ang_2Axis_kWh_m2', 'Annual_Loss_Therm_2Axis_kWh_m2', 'Annual_Yield_2Axis_kWh_m2')
        if fig: st.plotly_chart(fig, use_container_width=True)
    
    with c6:
        # Placeholder or Summary Text
        st.markdown("### 💡 Insight")
        st.info("""
        **Conversion Loss** (Grey) typically dominates due to the Shockley-Queisser limit of single-junction silicon cells.
        
        **Angular Loss** (Yellow) is highest for fixed panels at high incidence angles (morning/evening).
        
        **Thermal Loss** (Red) increases when panels get hot (high irradiance + high ambient temp).
        """)
    
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
    st.info("👈 Enter your location in the sidebar and click **Run Simulation** to see the results.")
