--create user
CREATE USER IF NOT EXISTS user IDENTIFIED BY 'password';

GRANT ALL ON default.* TO user;

-- create demo tables

CREATE DATABASE IF NOT EXISTS default;

-- source data
CREATE TABLE IF NOT EXISTS demo_data (
    x1 Float64,
    x2 Float64,
    y  Float64
) ENGINE = MergeTree()
ORDER BY tuple()
SETTINGS index_granularity = 8192;

-- model coefficients
CREATE TABLE IF NOT EXISTS model_coefficients (
    coef_x1      Float64,
    coef_x2      Float64,
    intercept    Float64,
    model_version String,
    created_at   DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY created_at;

-- test data (1000 lines)
INSERT INTO demo_data (x1, x2, y)
SELECT
    randNormal(10, 3) AS x1,
    randNormal(5, 2)  AS x2,
    x1 * 2.5 + x2 * 1.7 + randNormal(0, 5) AS y
FROM numbers(1000);
