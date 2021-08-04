# PSD_update

## Using the Python GUI
1. Install the drivers for the RS-232 adapter (the Windows ones for Moxa Uport 1100 Series are contained in this folder);
3. Power up and connect the PSD box;
4. Launch `main.exe`. The measurement parameters (measurement time, sampling interval, COM port) need to be set before pressing *START*. When pressing *START*, the export folder can be chosen (or not, by canceling the operation). Afterwards, the measurment starts.

## Building the Python GUI
1. Install [Python 3.9](https:/https://www.python.org/downloads/);
2. Change directories to be in the main folder (containing all the `.py` files);
3. (Optionnal) create and activate a [virtual environment](https://docs.python.org/3/library/venv.html) by using
    * `py -m venv .venv`
    * `.\.venv\Scripts\activate`
5. Install the package requirements with `pip install -r requirements.txt`;
6. Use pyinstaller to create an executable, by using e.g `pyinstaller .\main.py --onefile`.

Optionnally, run `main.py` directly with Python (e.g for debugging purposes) with `py main.py`