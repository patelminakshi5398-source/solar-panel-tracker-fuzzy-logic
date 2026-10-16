# Solar Panel Tracker — Streamlit Fuzzy Logic Demo

## Features
- Clean Streamlit dashboard for a dual-axis solar tracker simulation.
- The only user-adjustable parameter is time, restricted to 06:00 AM–06:00 PM.
- Uses triangular membership functions and three fuzzy rules: Negative, Zero, Positive.
- Displays estimated azimuth/tilt, fuzzy correction, panel illustration, and daytime profile.
- No ESP32, Arduino, sensors, motors, or hardware connection is required.

## Run on Windows
1. Install Python 3.10 or newer from https://www.python.org/downloads/
2. Extract `solar_fuzzy_tracker.zip`.
3. Open the extracted folder in VS Code.
4. Open Terminal → New Terminal.
5. Create a virtual environment (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run:
   ```bat
   .venv\Scripts\activate.bat
   ```

6. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
7. Start the website:
   ```powershell
   python -m streamlit run app.py
   ```
8. Streamlit will show a local URL, usually `http://localhost:8501`. Open it in your browser.

## Run without a virtual environment
```powershell
python -m pip install streamlit pandas plotly
python -m streamlit run app.py
```

## Important project note
This is a software simulation. Time is the only manual input, and the app estimates the panel's orientation using a simplified daytime model. The fuzzy rules demonstrate the control concept but do not drive real motors or use real LDR measurements.
