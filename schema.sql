-- Each row belongs to a state, year and quarter.
-- Counts are whole numbers. Amounts are in Indian rupees.
CREATE TABLE IF NOT EXISTS aggregated_transaction (
    state TEXT, year INTEGER, quarter INTEGER, category TEXT,
    transaction_count INTEGER, amount REAL,
    PRIMARY KEY (state, year, quarter, category)
);
CREATE TABLE IF NOT EXISTS aggregated_insurance (
    state TEXT, year INTEGER, quarter INTEGER, category TEXT,
    transaction_count INTEGER, amount REAL,
    PRIMARY KEY (state, year, quarter, category)
);
CREATE TABLE IF NOT EXISTS aggregated_user (
    state TEXT, year INTEGER, quarter INTEGER,
    registered_users INTEGER, app_opens INTEGER,
    PRIMARY KEY (state, year, quarter)
);
-- map_map is the PDF's name for district transaction data.
CREATE TABLE IF NOT EXISTS map_map (
    state TEXT, year INTEGER, quarter INTEGER, district TEXT,
    transaction_count INTEGER, amount REAL,
    PRIMARY KEY (state, year, quarter, district)
);
CREATE TABLE IF NOT EXISTS map_insurance (
    state TEXT, year INTEGER, quarter INTEGER, district TEXT,
    transaction_count INTEGER, amount REAL,
    PRIMARY KEY (state, year, quarter, district)
);
CREATE TABLE IF NOT EXISTS map_user (
    state TEXT, year INTEGER, quarter INTEGER, district TEXT,
    registered_users INTEGER, app_opens INTEGER,
    PRIMARY KEY (state, year, quarter, district)
);
-- scope_state = india means the source's national top list.
-- Otherwise this is a top list within one state.
-- Top lists are subsets, so never use them to calculate national totals.
CREATE TABLE IF NOT EXISTS top_map (
    scope_state TEXT, year INTEGER, quarter INTEGER,
    entity_type TEXT, entity_name TEXT,
    transaction_count INTEGER, amount REAL,
    PRIMARY KEY (scope_state, year, quarter, entity_type, entity_name)
);
CREATE TABLE IF NOT EXISTS top_insurance (
    scope_state TEXT, year INTEGER, quarter INTEGER,
    entity_type TEXT, entity_name TEXT,
    transaction_count INTEGER, amount REAL,
    PRIMARY KEY (scope_state, year, quarter, entity_type, entity_name)
);
CREATE TABLE IF NOT EXISTS top_user (
    scope_state TEXT, year INTEGER, quarter INTEGER,
    entity_type TEXT, entity_name TEXT, registered_users INTEGER,
    PRIMARY KEY (scope_state, year, quarter, entity_type, entity_name)
);
