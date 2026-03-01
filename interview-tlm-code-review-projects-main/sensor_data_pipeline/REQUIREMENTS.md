# Design a Sensor Data Pipeline Framework

## 📝 Summary

Design a modular, extensible data pipeline to process time-series sensor data. You will take raw sensor readings and pass them through a series of transformation and analysis steps, producing a clean, enriched output.

## 📦 Input Dataset

Each row in the dataset is a JSON object representing a single sensor reading. The dataset is a list of readings like this:

```json
{
  "mesh_id": "mesh-001",
  "device_id": "device-A",
  "timestamp": "2025-03-26T13:45:00Z",
  "temperature_c": 22.4,
  "humidity": 41.2,
  "status": "ok"
}
```

## 🔁 Required Pipeline Steps

Implement a pipeline that performs the following steps in order:

1. Convert timestamps to EST
    - Convert each `timestamp` from UTC to Eastern Standard Time (EST).
    - Retain both original and converted timestamps.

2. Convert temperature from Celsius to Fahrenheit
    - Add a `temperature_f` field.
    - Formula: `temp_f = (temp_c * 9/5) + 32`.

3. Group and aggregate by mesh network
    - Group readings by `mesh_id`.
    - For each group, compute:
        - Average temperature (C and F)
        - Average humidity
        - Total readings
    - Output one summary per `mesh_id`.

4. Anomaly detection
    - Add a `temperature_alert` boolean if:
        - Temp (C) < -10 or > 60
    - Add a `humidity_alert` boolean if:
        - Humidity < 10% or > 90%
    - You may also include a `status != "ok"` flag.
