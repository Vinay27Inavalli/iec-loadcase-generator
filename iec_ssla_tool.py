from io import BytesIO
import streamlit as st
st.image("logo.png", width=200)  # or "banner.png" and adjust width
import pandas as pd

# ---- PAGE SETTINGS ----
st.set_page_config(page_title="IEC SSLA Load Case Matrix Generator", layout="centered")
st.title("IEC SSLA Load Case Matrix Generator (Ed. 4 Only)")
st.markdown("🌀 Generate DLC input matrices for **Site-Specific Load Assessments (SSLA)** as per **IEC 61400-1 Edition 4**.")

st.markdown("""
# **IEC Load Case Matrix Generator**
Generate SSLA load case matrices compliant with **IEC 61400-1 Ed. 4**  
Export formats: **Excel**, **Flex5**, **GH Bladed**

🚀 Supports site-specific wind turbine simulations  
🔧 Includes fault scenarios, grid loss, and user-defined DLCs  
🌐 Export-ready for certification tools
""")


# ---- FIXED INPUTS ----
turbine_type = st.selectbox("Turbine Type", ["Onshore", "Offshore", "Floating"])
wind_class = st.selectbox("Wind Class", ["I", "II", "III"])
turb_class = st.selectbox("Turbulence Class", ["A", "B", "C"])

pitch_control = st.checkbox("Pitch Control Enabled", value=True)
yaw_control = st.checkbox("Yaw Control Enabled", value=True)
grid_loss = st.checkbox("Include Grid Loss DLCs", value=True)
faults_enabled = st.checkbox("Include Fault Scenarios", value=True)

seeds = st.slider("Number of Seeds", 1, 12, 6)
duration = st.slider("Simulation Duration (s)", 10, 1200, 600)
wind_speed_range = st.slider("Mean Wind Speed Range (m/s)", 3, 25, (6, 24))

# ---- ADVANCED CLIMATE INPUTS ----
st.markdown("### 🌦️ Climate Inputs (Advanced)")
enable_advanced = st.toggle("Enable Advanced Climate Inputs", value=False)

# --- Defaults based on class ---
shear_by_class = {"I": 0.14, "II": 0.20, "III": 0.30}
turbulence_by_class = {"A": 0.18, "B": 0.14, "C": 0.10}
yaw_defaults = {
    "1.1": "5", "1.2": "5", "1.3": "5", "1.4": "5",
    "2.1": "5", "2.4": "5", "3.1": "3", "4.1": "3",
    "6.4": "0",  # Parked
}

# --- Advanced override inputs ---
if enable_advanced:
    st.markdown("#### Override Climate Values")
    global_yaw = st.text_input("Yaw Error (deg)", value="5")
    global_ti = st.number_input("Turbulence Intensity", value=turbulence_by_class[turb_class])
    global_shear = st.number_input("Wind Shear Exponent α", value=shear_by_class[wind_class])
    global_temp = st.text_input("Temperature (°C)", value="15")
    global_iec = st.selectbox("IEC Class Override", ["I", "II", "III"], index=["I", "II", "III"].index(wind_class))

# ---- PREDEFINED SSLA DLCs ----
dlc_options = {
    "1.1": {"Type": "Power Prod", "Vmean": None, "Fault": "No", "Grid Loss": "No"},
    "1.2": {"Type": "EOG", "Vmean": "Vref", "Fault": "No", "Grid Loss": "No"},
    "1.3": {"Type": "EWS", "Vmean": "Vhub", "Fault": "No", "Grid Loss": "No"},
    "1.4": {"Type": "Turbulence Faults", "Vmean": "Vhub", "Fault": "Yes", "Grid Loss": "No"},
    "2.1": {"Type": "Fault During Operation", "Vmean": "Vhub", "Fault": "Yes", "Grid Loss": "No"},
    "2.4": {"Type": "Grid Loss", "Vmean": "Vhub", "Fault": "No", "Grid Loss": "Yes"},
    "3.1": {"Type": "Start-up", "Vmean": "10", "Fault": "No", "Grid Loss": "No"},
    "4.1": {"Type": "Shut-down", "Vmean": "10", "Fault": "No", "Grid Loss": "No"},
    "6.4": {"Type": "Parked (extreme)", "Vmean": "50-year Gust", "Fault": "N/A", "Grid Loss": "N/A"},
}

default_dlcs = list(dlc_options.keys())
selected_dlcs = st.multiselect(
    "Select SSLA-relevant DLCs to include:",
    options=default_dlcs,
    default=default_dlcs
)

# ---- CUSTOM DLC INPUT ----
st.subheader("➕ Add Custom DLC")
with st.form("custom_dlc_form", clear_on_submit=True):
    dlc_name = st.text_input("DLC Code", value="X.1")
    dlc_type = st.text_input("Type", value="Custom")
    vmean = st.text_input("Vmean (e.g. 8 or 6–24)", value="12")
    custom_seeds = st.number_input("Seeds", min_value=1, value=6, step=1)
    custom_duration = st.number_input("Duration (s)", min_value=10, value=600, step=10)
    custom_fault = st.selectbox("Fault", ["No", "Yes", "N/A"])
    custom_gridloss = st.selectbox("Grid Loss", ["No", "Yes", "N/A"])
    submitted = st.form_submit_button("Add Custom DLC")

if "custom_dlcs" not in st.session_state:
    st.session_state.custom_dlcs = []

if submitted:
    new_dlc = {
        "DLC": dlc_name,
        "Type": dlc_type,
        "Vmean": vmean,
        "Seeds": custom_seeds,
        "Duration": custom_duration,
        "Fault": custom_fault,
        "Grid Loss": custom_gridloss,
        "YawError": global_yaw if enable_advanced else "0",
        "Turbulence": global_ti if enable_advanced else turbulence_by_class[turb_class],
        "ShearExp": global_shear if enable_advanced else shear_by_class[wind_class],
        "IEC Class": global_iec if enable_advanced else wind_class,
        "Temperature": global_temp if enable_advanced else "15"
    }
    st.session_state.custom_dlcs.append(new_dlc)
    st.success(f"✅ Custom DLC '{dlc_name}' added.")

# ---- BUILD DLC TABLE ----
dlcs = []
for code in selected_dlcs:
    item = dlc_options[code]
    row = {
        "DLC": code,
        "Type": item["Type"],
        "Vmean": f"{wind_speed_range[0]}–{wind_speed_range[1]}" if item["Vmean"] is None else item["Vmean"],
        "Seeds": seeds if item["Vmean"] != "50-year Gust" else 1,
        "Duration": duration if item["Vmean"] != "50-year Gust" else 60,
        "Fault": item["Fault"],
        "Grid Loss": item["Grid Loss"],
        "YawError": global_yaw if enable_advanced else yaw_defaults.get(code, "0"),
        "Turbulence": global_ti if enable_advanced else turbulence_by_class[turb_class],
        "ShearExp": global_shear if enable_advanced else shear_by_class[wind_class],
        "IEC Class": global_iec if enable_advanced else wind_class,
        "Temperature": global_temp if enable_advanced else "15"
    }
    dlcs.append(row)

df = pd.DataFrame(dlcs)

# Append custom DLCs
if st.session_state.custom_dlcs:
    df = pd.concat([df, pd.DataFrame(st.session_state.custom_dlcs)], ignore_index=True)

# ---- EXPORT FORMAT SELECTION ----
st.subheader("⬇️ Export Format")
output_format = st.selectbox("Choose Format", ["Excel", "Bladed", "Flex5"])

st.subheader("📋 Generated Load Case Matrix")
st.dataframe(df, use_container_width=True)

# ---- EXPORT: EXCEL ----
if output_format == "Excel":
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="LoadCases")
    st.download_button(
        label="📥 Download Excel",
        data=excel_buffer.getvalue(),
        file_name="IEC_Load_Case_Matrix.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ---- EXPORT: BLADED CSV ----
elif output_format == "Bladed":
    bladed_df = df.rename(columns={
        "DLC": "Case",
        "Vmean": "Vhub",
        "Seeds": "Seeds",
        "Duration": "Time (s)",
        "Fault": "Fault Enabled",
        "Grid Loss": "Grid Loss",
        "YawError": "Yaw Error",
        "Turbulence": "TI",
        "ShearExp": "Shear Exp",
        "IEC Class": "IEC Class",
        "Temperature": "Temperature"
    })

    ordered_cols = ["Case", "Vhub", "Seeds", "Time (s)", "Fault Enabled", "Grid Loss",
                    "Yaw Error", "TI", "Shear Exp", "IEC Class", "Temperature"]
    bladed_df = bladed_df[[col for col in ordered_cols if col in bladed_df.columns]]

    csv_buffer = BytesIO()
    bladed_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Bladed CSV",
        data=csv_buffer.getvalue(),
        file_name="bladed_dlc_matrix.csv",
        mime="text/csv"
    )

# ---- EXPORT: FLEX5 ----
elif output_format == "Flex5":
    # Define export order
    flex5_cols = ["DLC", "Vmean", "Seeds", "Duration", "Fault", "Grid Loss",
                  "YawError", "Turbulence", "ShearExp", "IEC Class", "Temperature"]

    # Ensure only available columns are included
    flex5_df = df[flex5_cols]

    # Format each row into a line of space-separated values
    flex_lines = []
    for _, row in flex5_df.iterrows():
        line = " ".join(str(val) for val in row.values)
        flex_lines.append(line)

    flex5_text = "\n".join(flex_lines)

    st.download_button(
        label="📥 Download Flex5 Format (.txt)",
        data=flex5_text,
        file_name="load_matrix_flex5.txt",
        mime="text/plain"
    )

# === A3: Footer ===
st.markdown("---")
st.markdown("""
#### ℹ️ About this Tool  
This tool helps wind engineers and certification specialists generate compliant DLC matrices for **site-specific load assessments (SSLA)**.  
Developed as a side project by [Vinay Inavalli](https://www.linkedin.com/in/vinayinavalli/) 🇮🇳

📬 Feedback & collaboration: [vinayinavalli@gmail.com](mailto:vinayinavalli@gmail.com)
""")
