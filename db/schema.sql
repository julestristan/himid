-- Executed once by the postgres container on first start (docker-entrypoint-initdb.d)

-- Every buy / sell. Source of truth for positions and PRU.
CREATE TABLE IF NOT EXISTS transactions (
    id     serial  PRIMARY KEY,
    date   date    NOT NULL,
    ticker text    NOT NULL,
    qty    numeric NOT NULL,            -- > 0 buy, < 0 sell
    price  numeric NOT NULL,            -- unit price
    fees   numeric NOT NULL DEFAULT 0,
    note   text
);

-- Daily close for every ticker ever held + the benchmark
CREATE TABLE IF NOT EXISTS prices (
    date   date    NOT NULL,
    ticker text    NOT NULL,
    close  numeric NOT NULL,
    PRIMARY KEY (date, ticker)
);

-- One point per trading day, fully recomputed by src/daily.py
CREATE TABLE IF NOT EXISTS daily_portfolio (
    date         date    PRIMARY KEY,
    value        numeric NOT NULL,      -- market value of the positions
    cash_flow    numeric NOT NULL,      -- net amount invested that day
    invested     numeric NOT NULL,      -- cumulated net amount invested
    twr_index    numeric NOT NULL,      -- time-weighted return, base 100
    bench_index  numeric NOT NULL,      -- benchmark, base 100
    shadow_value numeric NOT NULL       -- same cash flows invested in the benchmark
);
