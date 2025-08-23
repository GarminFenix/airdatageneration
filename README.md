# Pollution Web Service

A Python-based web service that simulates and serves air‐quality data for 130 monitoring sites.  
It consists of two data generators (dynamic and static), a Flask REST API, live‐data simulation with scheduled pushes to subscribers, and a suite of integration and unit tests.

---

## Table of Contents

1. [Repository Structure](#repository-structure)  
2. [Prerequisites](#prerequisites)  
3. [Data Generation](#data-generation)  
   - [Dynamic Pollution Data](#dynamic-pollution-data)  
   - [Static Site Metadata](#static-site-metadata)  
4. [Running the Flask Service](#running-the-flask-service)  
5. [API Endpoints](#api-endpoints)  
6. [Subscription Notifications](#subscription-notifications)  
7. [Testing](#testing)  
8. [Future Improvements](#future-improvements)  

---

## Repository Structure

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
    ├── integration/              # End‐to‐end tests for data generation  
    └── unit/                     # Unit tests for loader, PollutionData, routes  
```

---

## Prerequisites

- Python 3.8+  
- PostgreSQL not required (data is read from JSON)  
- pip packages:
  ```
  pip install flask requests numpy pandas pyproj apscheduler
  ```

---

## Data Generation

### Dynamic Pollution Data

Generates 24 hours of readings at 10-minute intervals for 130 sites, varying values based on “busy” vs “quiet” periods.

```bash
python src/air_data_generation.py
# Output → data/pollution_data.json
```

### Static Site Metadata

Reads `data/AIRQUALITY_DEFINITION.csv`, transforms OSGB coordinates to WGS84, and outputs:

```bash
python src/metadata_generator.py
# Output → data/metadata.json
```

---

## Running the Flask Service

1. **Ensure** `data/pollution_data.json` and `data/metadata.json` exist.  
2. From project root, launch:
   ```bash
   export FLASK_APP=src/app.py
   flask run --host=0.0.0.0 --port=8182
   ```
3. Health check:
   ```
   GET http://localhost:8182/health
   ```

---

## API Endpoints

All routes are prefixed with `/pollutiondata`

| Method | Path                       | Description                                                        |
| ------ | -------------------------- | ------------------------------------------------------------------ |
| POST   | `/subscribe`               | Register a webhook URL and subscription types; immediately pushes latest data. |
| GET    | `/simtime`                 | Retrieve current simulation timestamp.                             |
| POST   | `/simtime`                 | Manually set simulation timestamp (JSON body: `{"timestamp":"..."}`). |
| GET    | `/`                        | Query pollution data for a given `timestamp` & `site` (query params). |
| GET    | `/sitemetadata`            | Retrieve all site coordinates and system codes.                    |

---

## Subscription Notifications

- **Global** list `subscriptions` in `subscription_utils.py`.  
- `notify_subscribers()` builds a UTMC‐style payload for each subscriber and POSTs JSON to their `notificationUrl`.  
- Triggered on new subscription and every simulated minute via APScheduler.

---

## Testing

### Integration Tests (data generation)

```bash
pytest tests/integration
```

Validates:
- 130 sites  
- 10-minute timestamp spacing  
- Value ranges for busy/quiet periods  

### Unit Tests (core logic & endpoints)

```bash
pytest tests/unit
```

Covers:
- `load_json()` type conversions  
- `PollutionData` methods  
- Flask routes via test client  


---

