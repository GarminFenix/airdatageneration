
# Pollution Web Service

A Python-based Flask service that simulates and serves air-quality data for 130 monitoring sites. It includes dynamic and static data generators, a REST API, live-data simulation with scheduled pushes to subscribers, and a suite of integration and unit tests.

Developed by Ross Cochrane as part of a submission for MSc Software Development
dissertation.
Part of Pollution Avoidance Navigation Tool (PANT):
Flask Pollution Data Generation Web Service (This)
Spring API
Flask API
Flutter Front End

---

## 🚀 Quickstart

1. **Clone the repository**
   ```bash
   git clone https://github.com/GarminFenix/airdatageneration.git
   cd airdatageneration
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows PowerShell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate pollution data**
   ```bash
   python src/air_data_generation.py
   # Output → data/pollution_data.json
   ```

5. **Generate site metadata**
   ```bash
   python src/static_air_site_generation.py
   # Output → data/metadata.json
   ```

6. **Run the Flask service**
   ```bash
   export FLASK_APP=src/app.py
   flask run --host=0.0.0.0 --port=8182
   ```

---

## 🧱 Repository Structure

```
├── data/
│   ├── pollution_data.json       # Generated dynamic readings
│   └── metadata.json             # Generated static site metadata
├── src/
│   ├── air_data_generation.py    # Generates pollution_data.json
│   ├── metadata_generator.py     # Converts CSV to metadata.json
│   ├── pseudo_air_pollution_data.py
│   ├── subscription_utils.py
│   ├── routes.py
│   └── app.py
└── tests/
    ├── integration/              # End-to-end tests for data generation
    └── unit/                     # Unit tests for loader, PollutionData, routes
```

---

## ⚙️ Prerequisites

- Python 3.8+  
- No database required — data is served from generated JSON files  
- Required Python packages:
  ```bash
  pip install flask requests numpy pandas pyproj apscheduler
  ```

---

## 🔄 Data Generation

### Dynamic Pollution Data

Generates 24 hours of readings at 10-minute intervals for 130 sites, simulating busy and quiet periods.

```bash
python src/air_data_generation.py
```

### Static Site Metadata

Reads `data/AIRQUALITY_DEFINITION.csv`, transforms OSGB coordinates to WGS84, and outputs metadata:

```bash
python src/metadata_generator.py
```

---

## 🌐 Running the Flask Web Service 

1. Ensure `data/pollution_data.json` and `data/metadata.json` exist  
2. Launch the service:
   ```bash
   export FLASK_APP=src/app.py
   flask run --host=0.0.0.0 --port=8182
   ```

3. Health check:
   ```bash
   curl http://localhost:8182/health
   ```

---

## 📡 API Endpoints

All routes are prefixed with `/pollutiondata`

| Method | Path                       | Description                                                        |
|--------|----------------------------|--------------------------------------------------------------------|
| POST   | `/subscribe`               | Register a webhook URL and subscription types; pushes latest data |
| GET    | `/simtime`                 | Retrieve current simulation timestamp                              |
| POST   | `/simtime`                 | Manually set simulation timestamp                                  |
| GET    | `/`                        | Query pollution data for a given `timestamp` & `site`              |
| GET    | `/sitemetadata`            | Retrieve all site coordinates and system codes                     |

---

## 🔔 Subscription Notifications

- Subscriptions are stored in `subscription_utils.py`
- `notify_subscribers()` builds a UTMC-style payload and POSTs to each subscriber’s `notificationUrl`
- Triggered on new subscription and every simulated minute via APScheduler

---

## 🧪 Testing

### Integration Tests

```bash
pytest tests/integration
```

Validates:
- 130 sites  
- 10-minute timestamp spacing  
- Value ranges for busy/quiet periods  

### Unit Tests

```bash
pytest tests/unit
```

Covers:
- `load_json()` type conversions  
- `PollutionData` methods  
- Flask routes via test client  

---

