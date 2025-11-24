-- Create energy_data database for storing normalized data
CREATE DATABASE energy_data;

-- Connect to energy_data database
\c energy_data;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS production;

-- Create tables for normalized energy data
CREATE TABLE IF NOT EXISTS production.energy_demand (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    demand_mw DECIMAL(10, 2) NOT NULL,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp, region)
);

CREATE TABLE IF NOT EXISTS production.weather_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    precipitation DECIMAL(5, 2),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp, region)
);

CREATE TABLE IF NOT EXISTS production.calendar_features (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    day_of_week INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name VARCHAR(100),
    month INTEGER,
    quarter INTEGER,
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS production.forecasts (
    id SERIAL PRIMARY KEY,
    forecast_timestamp TIMESTAMP NOT NULL,
    target_timestamp TIMESTAMP NOT NULL,
    predicted_demand_mw DECIMAL(10, 2) NOT NULL,
    confidence_lower DECIMAL(10, 2),
    confidence_upper DECIMAL(10, 2),
    model_version VARCHAR(50),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(forecast_timestamp, target_timestamp, region)
);

CREATE TABLE IF NOT EXISTS production.anomalies (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    anomaly_type VARCHAR(50),
    severity VARCHAR(20),
    actual_value DECIMAL(10, 2),
    expected_value DECIMAL(10, 2),
    deviation DECIMAL(10, 2),
    description TEXT,
    region VARCHAR(50),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp, region)
);

-- Create indexes for performance
CREATE INDEX idx_energy_demand_timestamp ON production.energy_demand(timestamp);
CREATE INDEX idx_energy_demand_region ON production.energy_demand(region);
CREATE INDEX idx_weather_timestamp ON production.weather_data(timestamp);
CREATE INDEX idx_weather_region ON production.weather_data(region);
CREATE INDEX idx_calendar_date ON production.calendar_features(date);
CREATE INDEX idx_forecasts_target ON production.forecasts(target_timestamp);
CREATE INDEX idx_anomalies_timestamp ON production.anomalies(timestamp);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE energy_data TO airflow;
GRANT ALL PRIVILEGES ON SCHEMA raw, staging, production TO airflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw, staging, production TO airflow;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA raw, staging, production TO airflow;

-- Create raw data tables for API ingestion
CREATE TABLE IF NOT EXISTS raw.api_responses (
    id SERIAL PRIMARY KEY,
    api_name VARCHAR(100),
    endpoint VARCHAR(255),
    response_data JSONB,
    status_code INTEGER,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_responses_name ON raw.api_responses(api_name);
CREATE INDEX idx_api_responses_fetched ON raw.api_responses(fetched_at);
