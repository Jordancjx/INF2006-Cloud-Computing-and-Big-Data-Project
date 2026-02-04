-- =====================================================
-- MySQL Database Schema for Singapore Education Data
-- =====================================================

-- Create database (if needed)
-- CREATE DATABASE IF NOT EXISTS education_data;
-- USE education_data;

-- =====================================================
-- 1. SCHOOLS LOOKUP TABLE (Master Reference Table)
-- =====================================================
CREATE TABLE IF NOT EXISTS schools (
    school_id INT PRIMARY KEY,
    school_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 2. GRADUATE EMPLOYMENT SURVEY (GES) TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS graduate_employment_survey (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    school_id INT NOT NULL,
    university VARCHAR(255) NOT NULL,
    school VARCHAR(255),
    degree VARCHAR(255),
    employment_rate_overall DECIMAL(5,2),
    employment_rate_ft_perm DECIMAL(5,2),
    basic_monthly_mean DECIMAL(10,2),
    basic_monthly_median DECIMAL(10,2),
    gross_monthly_mean DECIMAL(10,2),
    gross_monthly_median DECIMAL(10,2),
    gross_mthly_25_percentile DECIMAL(10,2),
    gross_mthly_75_percentile DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes for faster queries
    INDEX idx_year (year),
    INDEX idx_school_id (school_id),
    INDEX idx_year_school (year, school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 3. ENROLMENT BY INSTITUTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS enrolment_by_institutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    sex VARCHAR(10) NOT NULL,
    school_id INT NOT NULL,
    school_name VARCHAR(255) NOT NULL,
    enrolment INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes for faster queries
    INDEX idx_year (year),
    INDEX idx_school_id (school_id),
    INDEX idx_year_school (year, school_id),
    INDEX idx_sex (sex),
    
    -- Unique constraint to prevent duplicate entries
    UNIQUE KEY unique_enrolment (year, sex, school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 4. GRADUATES BY INSTITUTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS graduates_by_institutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    sex VARCHAR(10) NOT NULL,
    school_id INT NOT NULL,
    school_name VARCHAR(255) NOT NULL,
    graduates INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes for faster queries
    INDEX idx_year (year),
    INDEX idx_school_id (school_id),
    INDEX idx_year_school (year, school_id),
    INDEX idx_sex (sex),
    
    -- Unique constraint to prevent duplicate entries
    UNIQUE KEY unique_graduates (year, sex, school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- LOAD DATA (Example commands - adjust paths as needed)
-- =====================================================

-- Load schools lookup table
-- LOAD DATA LOCAL INFILE 'schools_lookup.csv'
-- INTO TABLE schools
-- FIELDS TERMINATED BY ',' 
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (school_id, school_name);

-- Load GES data
-- LOAD DATA LOCAL INFILE 'GES_with_ids.csv'
-- INTO TABLE graduate_employment_survey
-- FIELDS TERMINATED BY ',' 
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (year, university, school_id, school, degree, employment_rate_overall, 
--  employment_rate_ft_perm, basic_monthly_mean, basic_monthly_median,
--  gross_monthly_mean, gross_monthly_median, gross_mthly_25_percentile,
--  gross_mthly_75_percentile);

-- Load Enrolment data
-- LOAD DATA LOCAL INFILE 'EnrolmentbyInstitutions_with_ids.csv'
-- INTO TABLE enrolment_by_institutions
-- FIELDS TERMINATED BY ',' 
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (year, sex, school_id, school_name, enrolment);

-- Load Graduates data
-- LOAD DATA LOCAL INFILE 'Graduatesbyinstitutions_with_ids.csv'
-- INTO TABLE graduates_by_institutions
-- FIELDS TERMINATED BY ',' 
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (year, sex, school_id, school_name, graduates);

-- =====================================================
-- USEFUL QUERIES
-- =====================================================

-- View all schools
-- SELECT * FROM schools ORDER BY school_id;

-- Get enrolment data with school names
-- SELECT e.year, e.sex, s.school_name, e.enrolment
-- FROM enrolment_by_institutions e
-- JOIN schools s ON e.school_id = s.school_id
-- ORDER BY e.year, e.school_id;

-- Get employment stats by school
-- SELECT g.year, s.school_name, g.degree,
--        g.employment_rate_overall, g.gross_monthly_median
-- FROM graduate_employment_survey g
-- JOIN schools s ON g.school_id = s.school_id
-- WHERE g.year = 2020
-- ORDER BY g.employment_rate_overall DESC;

-- Compare enrolment vs graduates for a specific year
-- SELECT s.school_name, 
--        e.enrolment, 
--        g.graduates,
--        ROUND((g.graduates / e.enrolment) * 100, 2) as graduation_rate
-- FROM schools s
-- LEFT JOIN enrolment_by_institutions e ON s.school_id = e.school_id AND e.year = 2020 AND e.sex = 'MF'
-- LEFT JOIN graduates_by_institutions g ON s.school_id = g.school_id AND g.year = 2020 AND g.sex = 'MF'
-- WHERE e.enrolment IS NOT NULL AND g.graduates IS NOT NULL
-- ORDER BY s.school_name;
