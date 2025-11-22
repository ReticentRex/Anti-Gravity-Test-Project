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
st.sidebar.header("⚙️ Simulation")
if st.sidebar.button("Run Simulation", type="primary"):
    with st.spinner("Calculating annual profile..."):
        # Initialize Model
        model = SolarModel(latitude=latitude, longitude=longitude)
        
        # Run Simulation
        df, totals = model.generate_annual_profile()
        
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
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Horizontal", f"{totals['Annual_Yield_Horizontal_kWh_m2']:.1f} kWh/m²", 
                  delta=f"{totals['Ratio_Yield_Horizontal_vs_2Axis_Percent']:.1f}% of 2-Axis")
        
    with col2:
        st.metric("1-Axis Azimuth", f"{totals['Annual_Yield_1Axis_Azimuth_kWh_m2']:.1f} kWh/m²",
                  delta=f"{totals['Ratio_Yield_1Axis_Azimuth_vs_2Axis_Percent']:.1f}% of 2-Axis")
        
    with col3:
        st.metric("1-Axis Elevation", f"{totals['Annual_Yield_1Axis_Elevation_kWh_m2']:.1f} kWh/m²",
                  delta=f"{totals['Ratio_Yield_1Axis_Elevation_vs_2Axis_Percent']:.1f}% of 2-Axis")
        
    with col4:
        st.metric("2-Axis Tracking", f"{totals['Annual_Yield_2Axis_kWh_m2']:.1f} kWh/m²", 
                  delta="Reference")

    st.markdown("---")

    # --- Section 2: Performance Comparison Chart ---
    st.header("📈 Performance Comparison")
    
    # Prepare Data for Chart
    modes = ['Horizontal', '1-Axis Azimuth', '1-Axis Elevation', '2-Axis']
    yields = [
        totals['Annual_Yield_Horizontal_kWh_m2'],
        totals['Annual_Yield_1Axis_Azimuth_kWh_m2'],
        totals['Annual_Yield_1Axis_Elevation_kWh_m2'],
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
    st.header("📉 Loss Analysis")
    st.markdown("Breakdown of where the energy goes. **Useful Energy** is what you actually get.")
    
    # Prepare Data for Stacked Bar
    loss_data = {
        'Mode': modes,
        'Useful Energy': yields,
        'Thermal Loss': [
            totals['Annual_Loss_Therm_Horiz_kWh_m2'],
            totals['Annual_Loss_Therm_1Axis_Az_kWh_m2'],
            totals['Annual_Loss_Therm_1Axis_El_kWh_m2'],
            totals['Annual_Loss_Therm_2Axis_kWh_m2']
        ],
        'Angular Loss': [
            totals['Annual_Loss_Ang_Horiz_kWh_m2'],
            totals['Annual_Loss_Ang_1Axis_Az_kWh_m2'],
            totals['Annual_Loss_Ang_1Axis_El_kWh_m2'],
            totals['Annual_Loss_Ang_2Axis_kWh_m2']
        ]
    }
    
    df_loss = pd.DataFrame(loss_data)
    
    fig_loss = go.Figure()
    fig_loss.add_trace(go.Bar(name='Useful Energy', x=df_loss['Mode'], y=df_loss['Useful Energy'], marker_color='#2ecc71'))
    fig_loss.add_trace(go.Bar(name='Thermal Loss', x=df_loss['Mode'], y=df_loss['Thermal Loss'], marker_color='#e74c3c'))
    fig_loss.add_trace(go.Bar(name='Angular Loss', x=df_loss['Mode'], y=df_loss['Angular Loss'], marker_color='#f1c40f'))
    
    fig_loss.update_layout(barmode='stack', title="Energy Breakdown (Useful vs Losses)", yaxis_title="Energy (kWh/m²)")
    st.plotly_chart(fig_loss, use_container_width=True)
    
    # --- Section 4: Raw Data ---
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
