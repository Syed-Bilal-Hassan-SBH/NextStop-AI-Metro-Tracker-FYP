-- Metro Bus Simulation Database Schema

-- Create stops table
CREATE TABLE IF NOT EXISTS stops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    route_id TEXT NOT NULL
);

-- Create routes table
CREATE TABLE IF NOT EXISTS routes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    total_distance REAL DEFAULT 0.0
);

-- Create buses table
CREATE TABLE IF NOT EXISTS buses (
    id TEXT PRIMARY KEY,
    route_id TEXT NOT NULL,
    current_lat REAL NOT NULL,
    current_lng REAL NOT NULL,
    speed REAL NOT NULL,
    status TEXT NOT NULL,
    next_stop_index INTEGER NOT NULL,
    last_update TEXT NOT NULL,
    direction TEXT DEFAULT 'forward',
    FOREIGN KEY (route_id) REFERENCES routes (id)
);

-- Initial data for FR-01 route
INSERT OR IGNORE INTO routes (id, name, source, destination)
VALUES ('FR-01', 'Metro FR-01', 'Khanna Pul Stop', 'NUST/G-12 Metro Station');

-- Initial stops data for FR-01 route
INSERT OR IGNORE INTO stops (name, latitude, longitude, route_id) VALUES
('Khanna Pul Stop', 33.62925827, 73.11352419, 'FR-01'),
('Kuri Road', 33.64226592, 73.10347458, 'FR-01'),
('Iqbal Town', 33.64587248, 73.10087402, 'FR-01'),
('Dhoke Kala Khan', 33.64980447, 73.09776893, 'FR-01'),
('Sohan', 33.65968816, 73.09081386, 'FR-01'),
('Faizabad', 33.66214676, 73.08304602, 'FR-01'),
('IJP', 33.65603214, 73.07197937, 'FR-01'),
('Potohar', 33.66061322, 73.06454244, 'FR-01'),
('MCI School', 33.65943948, 73.06055447, 'FR-01'),
('CDA Complaint Center', 33.65749922, 73.05689877, 'FR-01'),
('OGTI', 33.65537697, 73.05275726, 'FR-01'),
('SUI Gas', 33.65315702, 73.04858977, 'FR-01'),
('PTCL I-10', 33.64923647, 73.04125419, 'FR-01'),
('IESCO I-10', 33.64759881, 73.03812801, 'FR-01'),
('Korang Road', 33.64389472, 73.03097094, 'FR-01'),
('Mandi Morh', 33.63488067, 73.03179802, 'FR-01'),
('Sabzi Mandi', 33.63722481, 73.02496389, 'FR-01'),
('Metro CNC', 33.63982626, 73.02409564, 'FR-01'),
('Islamabad Medical Complex', 33.64831062, 73.01736156, 'FR-01'),
('PAEC General Hospital', 33.65134388, 73.0150703, 'FR-01'),
('FAST University', 33.65729305, 73.01580215, 'FR-01'),
('Islamic University', 33.65823121, 73.01770362, 'FR-01'),
('National Police Academy', 33.65524607, 73.01069052, 'FR-01'),
('Police Foundation Metro Station', 33.66253963, 73.0072021, 'FR-01');