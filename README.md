# TokenFeeds App

TokenFeeds is Dash application running in Flask, serving crypto data on an interactive dashboard. 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all requirements for the application.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Running basic development server on external IP port 8000 by default

```python
python index.py
```

Running Gunicorn WSGI on external IP port 8000 by default

```python
gunicorn -b :8000 -w 3 index:server 
```

## API Data 

API data is collected by on the host server outside of the application. 
Continuous data is collected at set intervals by various looped scripts, loaded as systemd services. Other less frequent API calls are run using cron jobs. All data collected is stored in Redis where it is called when required from the application.

These scripts are located in /apis

The systemd services, among others, are located in /conf

