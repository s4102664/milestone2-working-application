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
-- Oceania
('AUS','MMR',2024,95.1), ('AUS','POL',2024,95.0), ('AUS','DTP3',2024,94.9),
('NZL','MMR',2024,94.5), ('NZL','POL',2024,94.2), ('NZL','DTP3',2024,94.1),

-- Europe
('GBR','MMR',2024,94.2), ('GBR','POL',2024,94.0), ('GBR','DTP3',2024,93.8),
('FRA','MMR',2024,93.6), ('FRA','POL',2024,93.4), ('FRA','DTP3',2024,93.1),
('DEU','MMR',2024,95.0), ('DEU','POL',2024,94.7), ('DEU','DTP3',2024,94.5),
('ITA','MMR',2024,92.3), ('ITA','POL',2024,92.0), ('ITA','DTP3',2024,91.9),
('ESP','MMR',2024,94.7), ('ESP','POL',2024,94.4), ('ESP','DTP3',2024,94.2),
('NLD','MMR',2024,96.0), ('NLD','POL',2024,95.8), ('NLD','DTP3',2024,95.6),
('SWE','MMR',2024,97.1), ('SWE','POL',2024,96.9), ('SWE','DTP3',2024,96.7),
('POL','MMR',2024,92.8), ('POL','POL',2024,92.5), ('POL','DTP3',2024,92.2),
('CHE','MMR',2024,98.1), ('CHE','POL',2024,97.9), ('CHE','DTP3',2024,97.7),
('BEL','MMR',2024,95.6), ('BEL','POL',2024,95.3), ('BEL','DTP3',2024,95.1),
('IRL','MMR',2024,96.2), ('IRL','POL',2024,96.0), ('IRL','DTP3',2024,95.8),
('PRT','MMR',2024,94.9), ('PRT','POL',2024,94.7), ('PRT','DTP3',2024,94.5),
('GRC','MMR',2024,92.0), ('GRC','POL',2024,91.8), ('GRC','DTP3',2024,91.5),

-- Asia
('JPN','MMR',2024,96.4), ('JPN','POL',2024,96.2), ('JPN','DTP3',2024,96.0),
('CHN','MMR',2024,99.0), ('CHN','POL',2024,98.8), ('CHN','DTP3',2024,98.6),
('IND','MMR',2024,91.2), ('IND','POL',2024,91.0), ('IND','DTP3',2024,90.8),
('KOR','MMR',2024,98.5), ('KOR','POL',2024,98.3), ('KOR','DTP3',2024,98.0),
('THA','MMR',2024,97.0), ('THA','POL',2024,96.8), ('THA','DTP3',2024,96.6),
('VNM','MMR',2024,96.8), ('VNM','POL',2024,96.5), ('VNM','DTP3',2024,96.3),

-- Americas
('USA','MMR',2024,94.8), ('USA','POL',2024,94.6), ('USA','DTP3',2024,94.4),
('CAN','MMR',2024,96.2), ('CAN','POL',2024,96.0), ('CAN','DTP3',2024,95.8),
('BRA','MMR',2024,95.5), ('BRA','POL',2024,95.3), ('BRA','DTP3',2024,95.0),
('MEX','MMR',2024,94.0), ('MEX','POL',2024,93.8), ('MEX','DTP3',2024,93.6),
('ARG','MMR',2024,93.2), ('ARG','POL',2024,93.0), ('ARG','DTP3',2024,92.8),
('CHL','MMR',2024,97.4), ('CHL','POL',2024,97.2), ('CHL','DTP3',2024,97.0),

-- Africa & Middle East
('ZAF','MMR',2024,91.5), ('ZAF','POL',2024,91.2), ('ZAF','DTP3',2024,91.0),
('EGY','MMR',2024,93.8), ('EGY','POL',2024,93.6), ('EGY','DTP3',2024,93.4),
('KEN','MMR',2024,89.5), ('KEN','POL',2024,89.2), ('KEN','DTP3',2024,88.9),
('NGA','MMR',2024,88.2), ('NGA','POL',2024,88.0), ('NGA','DTP3',2024,87.8),
('TUR','MMR',2024,92.7), ('TUR','POL',2024,92.5), ('TUR','DTP3',2024,92.3),
('SAU','MMR',2024,95.3), ('SAU','POL',2024,95.1), ('SAU','DTP3',2024,94.9),
('ISR','MMR',2024,97.8), ('ISR','POL',2024,97.5), ('ISR','DTP3',2024,97.3);

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
