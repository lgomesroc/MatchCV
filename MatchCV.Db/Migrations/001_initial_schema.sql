CREATE EXTENSION IF NOT EXISTS "pgcrypto";


CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_users_role
        CHECK (role IN ('USER', 'ADMIN'))
);


CREATE TABLE job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL,
    job_description_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    evidenced_requirements JSONB NOT NULL DEFAULT '[]'::jsonb,
    unevidenced_requirements JSONB NOT NULL DEFAULT '[]'::jsonb,
    gaps JSONB NOT NULL DEFAULT '[]'::jsonb,
    resume_issues JSONB NOT NULL DEFAULT '[]'::jsonb,
    suggestions JSONB NOT NULL DEFAULT '[]'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CONSTRAINT fk_analyses_job_description
        FOREIGN KEY (job_description_id)
        REFERENCES job_descriptions (id),

    CONSTRAINT ck_analyses_status
        CHECK (
            status IN (
                'PENDING',
                'PROCESSING',
                'COMPLETED',
                'FAILED'
            )
        )
);


CREATE INDEX ix_users_email
    ON users (email);


CREATE INDEX ix_analyses_job_description_id
    ON analyses (job_description_id);


CREATE INDEX ix_analyses_status
    ON analyses (status);


CREATE INDEX ix_analyses_created_at
    ON analyses (created_at);
