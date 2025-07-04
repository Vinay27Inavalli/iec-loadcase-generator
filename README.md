# IEC SSLA Load Case Matrix Generator

[Live App 🔗](https://iec-loadcase-generator.streamlit.app/) • [Author: Vinay Inavalli](https://www.linkedin.com/in/vinayinavalli/)

---

## 📌 Description
A web-based tool to generate compliant Load Case Matrices for **Site-Specific Load Assessment (SSLA)**  
based on **IEC 61400-1 Edition 4**. Built for wind engineers, certification teams, and simulation specialists.

---

## ⚙️ Features
- ✅ Generate load case matrices for IEC Ed. 4 (SSLA only)
- ✅ Select turbine type, wind class, turbulence class
- ✅ Enable/disable pitch, yaw, fault, and grid loss
- ✅ Add custom DLCs
- ✅ Export to Excel, Bladed CSV, and Flex5 TXT formats
- ✅ Optional climate inputs: TI, shear exponent, yaw error

---

---

## 📬 Feedback

Have a suggestion, bug, or feature idea?  
[👉 Submit your feedback here](https://forms.gle/tpPc4HddTKQdUyB19)


---

## 🚀 Getting Started

To run locally:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
streamlit run iec_ssla_tool.py
