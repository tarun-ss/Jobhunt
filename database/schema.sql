-- JobHunter AI Database Schema
-- PostgreSQL 16 with pgvector extension

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    size VARCHAR(50),
    founded INTEGER,
    headquarters VARCHAR(255),
    website VARCHAR(255),
    glassdoor_rating DECIMAL(2,1),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tech stacks
CREATE TABLE IF NOT EXISTS tech_stacks (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(255) REFERENCES companies(company_id) ON DELETE CASCADE,
    languages TEXT[],
    frameworks TEXT[],
    tools TEXT[],
    confidence DECIMAL(3,2),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Job postings
CREATE TABLE IF NOT EXISTS job_postings (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    company_id VARCHAR(255) REFERENCES companies(company_id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    posted_date DATE,
    is_ghost_job BOOLEAN DEFAULT FALSE,
    ghost_score DECIMAL(3,2),
    salary_min INTEGER,
    salary_max INTEGER,
    location VARCHAR(255),
    remote_type VARCHAR(50),
    url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Hiring patterns
CREATE TABLE IF NOT EXISTS hiring_patterns (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(255) REFERENCES companies(company_id) ON DELETE CASCADE,
    ghost_job_frequency DECIMAL(3,2),
    avg_time_to_hire INTEGER,
    response_rate DECIMAL(3,2),
    interview_difficulty VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id)
);

-- Resumes
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    resume_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    content TEXT,
    parsed_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Applications
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    application_id UUID DEFAULT uuid_generate_v4(),
    resume_id VARCHAR(255) REFERENCES resumes(resume_id),
    job_id VARCHAR(255) REFERENCES job_postings(job_id),
    status VARCHAR(50) DEFAULT 'pending',
    applied_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    notes TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_companies_company_id ON companies(company_id);
CREATE INDEX IF NOT EXISTS idx_job_postings_company_id ON job_postings(company_id);
CREATE INDEX IF NOT EXISTS idx_job_postings_ghost_score ON job_postings(ghost_score);
CREATE INDEX IF NOT EXISTS idx_applications_resume_id ON applications(resume_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);

-- Insert sample data
INSERT INTO companies (company_id, name, industry, size, headquarters, glassdoor_rating) VALUES
('google', 'Google LLC', 'Technology', '100,000+', 'Mountain View, CA', 4.3),
('microsoft', 'Microsoft Corporation', 'Technology', '100,000+', 'Redmond, WA', 4.2),
('amazon', 'Amazon.com Inc.', 'E-commerce', '1,000,000+', 'Seattle, WA', 3.9)
ON CONFLICT (company_id) DO NOTHING;

INSERT INTO tech_stacks (company_id, languages, frameworks, tools, confidence, source) VALUES
('google', ARRAY['Python', 'Java', 'Go', 'C++'], ARRAY['TensorFlow', 'Angular', 'Kubernetes'], ARRAY['Bazel', 'Bigtable'], 0.95, 'job_postings'),
('microsoft', ARRAY['C#', 'TypeScript', 'Python'], ARRAY['.NET', 'Azure', 'React'], ARRAY['Visual Studio', 'Azure DevOps'], 0.92, 'job_postings'),
('amazon', ARRAY['Java', 'Python', 'JavaScript'], ARRAY['AWS', 'React', 'Spring'], ARRAY['DynamoDB', 'S3'], 0.90, 'job_postings')
ON CONFLICT DO NOTHING;

-- Sample job postings
INSERT INTO job_postings (job_id, company_id, title, description, posted_date, is_ghost_job, ghost_score, location, remote_type, url) VALUES
('job_001', 'google', 'Senior Software Engineer', 'Looking for experienced engineer with Python and cloud experience', '2025-01-15', FALSE, 0.12, 'Mountain View, CA', 'Hybrid', 'https://careers.google.com/job_001'),
('job_002', 'microsoft', 'Cloud Solutions Architect', 'Azure expert needed for enterprise solutions', '2025-01-18', FALSE, 0.08, 'Redmond, WA', 'Remote', 'https://careers.microsoft.com/job_002'),
('job_003', 'amazon', 'Full Stack Developer', 'Build scalable web applications', '2025-01-20', FALSE, 0.15, 'Seattle, WA', 'On-site', 'https://amazon.jobs/job_003')
ON CONFLICT (job_id) DO NOTHING;

-- Sample hiring patterns
INSERT INTO hiring_patterns (company_id, ghost_job_frequency, avg_time_to_hire, response_rate, interview_difficulty) VALUES
('google', 0.12, 45, 0.68, 'Hard'),
('microsoft', 0.08, 38, 0.72, 'Medium'),
('amazon', 0.15, 42, 0.65, 'Hard')
ON CONFLICT (company_id) DO NOTHING;
