PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS coverage (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    country   TEXT    NOT NULL,  
    vaccine   TEXT    NOT NULL, 
    year      INTEGER NOT NULL,
    coverage  REAL    NOT NULL CHECK(coverage >= 0 AND coverage <= 100),
    UNIQUE(country, vaccine, year)
);

INSERT OR IGNORE INTO coverage (country, vaccine, year, coverage) VALUES
-- Australia
('AUS','MMR',2022,93.8), ('AUS','MMR',2023,94.0), ('AUS','MMR',2024,94.2),
('AUS','POL',2023,95.1), ('AUS','DTP3',2023,95.4),

-- United Kingdom
('GBR','MMR',2022,90.8), ('GBR','MMR',2023,91.1), ('GBR','MMR',2024,91.5),
('GBR','POL',2023,92.4), ('GBR','DTP3',2023,93.2),

-- New Zealand
('NZL','MMR',2022,92.1), ('NZL','MMR',2023,92.7), ('NZL','MMR',2024,93.0),
('NZL','POL',2023,93.5), ('NZL','DTP3',2023,93.9),

-- United States
('USA','MMR',2022,92.5), ('USA','MMR',2023,92.6), ('USA','MMR',2024,92.8),
('USA','POL',2023,93.2), ('USA','DTP3',2023,93.6),

-- Canada
('CAN','MMR',2022,94.1), ('CAN','MMR',2023,94.3), ('CAN','MMR',2024,94.6),
('CAN','POL',2023,95.0), ('CAN','DTP3',2023,95.3),

-- Japan
('JPN','MMR',2022,96.4), ('JPN','MMR',2023,96.7), ('JPN','MMR',2024,96.9),
('JPN','POL',2023,97.3), ('JPN','DTP3',2023,97.5),

-- Germany
('DEU','MMR',2022,93.3), ('DEU','MMR',2023,93.6), ('DEU','MMR',2024,93.8),
('DEU','POL',2023,94.0), ('DEU','DTP3',2023,94.2),

-- France
('FRA','MMR',2022,92.7), ('FRA','MMR',2023,93.0), ('FRA','MMR',2024,93.3),
('FRA','POL',2023,93.8), ('FRA','DTP3',2023,94.0),

-- Italy
('ITA','MMR',2022,91.9), ('ITA','MMR',2023,92.2), ('ITA','MMR',2024,92.5),
('ITA','POL',2023,92.9), ('ITA','DTP3',2023,93.2);

CREATE INDEX IF NOT EXISTS idx_cov_country ON coverage(country);
CREATE INDEX IF NOT EXISTS idx_cov_vaccine ON coverage(vaccine);
CREATE INDEX IF NOT EXISTS idx_cov_year    ON coverage(year);

CREATE TABLE IF NOT EXISTS vaccine_info (
    vaccine_code TEXT PRIMARY KEY,
    vaccine_name TEXT NOT NULL,
    manufacturer TEXT NOT NULL
);

INSERT OR IGNORE INTO vaccine_info (vaccine_code, vaccine_name, manufacturer) VALUES
('MMR',  'Measles, Mumps, Rubella', 'Pfizer'),
('POL',  'Polio',                    'Moderna'),
('DTP3', 'Diphtheria, Tetanus, Pertussis (3rd dose)', 'GSK');

CREATE VIEW IF NOT EXISTS coverage_norm AS
SELECT
    country,
    CASE WHEN vaccine='DTP3' THEN 'DTP' ELSE vaccine END AS vaccine_readable,
    vaccine AS vaccine_code,
    year,
    coverage
FROM coverage;
