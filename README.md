# IEC Load Case Matrix Generator (IEC 61400-1 Ed. 4)

This web-based tool helps wind turbine engineers generate load case input matrices for **site-specific load assessments (SSLA)** as per **IEC 61400-1 Edition 4**.

Built using Python and Streamlit.

## ✨ Features

- Select and customize IEC Design Load Cases (DLCs)
- Add your own custom load cases
- Optional climate inputs (Yaw Error, Turbulence Intensity, Wind Shear, etc.)
- Export to:
  - 📊 Excel (.xlsx)
  - 📄 Bladed format (.csv)
  - 🧾 Flex5 format (.txt)

## 🚀 How to Run Locally

```bash
pip install -r requirements.txt
streamlit run iec_ssla_tool.py
