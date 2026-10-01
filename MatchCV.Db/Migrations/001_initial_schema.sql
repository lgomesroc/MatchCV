IF DB_ID(N'MatchCV') IS NULL
BEGIN
    CREATE DATABASE MatchCV;
END;
GO

USE MatchCV;
GO

IF OBJECT_ID(N'dbo.users', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.users
    (
        id UNIQUEIDENTIFIER NOT NULL,
        name NVARCHAR(150) NOT NULL,
        email NVARCHAR(255) NOT NULL,
        password_hash NVARCHAR(255) NOT NULL,
        role NVARCHAR(20) NOT NULL,
        created_at DATETIME2 NOT NULL
            CONSTRAINT DF_users_created_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_users
            PRIMARY KEY (id),

        CONSTRAINT UQ_users_email
            UNIQUE (email),

        CONSTRAINT CK_users_role
            CHECK (role IN (N'USER', N'ADMIN'))
    );
END;
GO

IF OBJECT_ID(N'dbo.job_descriptions', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.job_descriptions
    (
        id UNIQUEIDENTIFIER NOT NULL,
        content NVARCHAR(3000) NOT NULL,
        created_at DATETIME2 NOT NULL
            CONSTRAINT DF_job_descriptions_created_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_job_descriptions
            PRIMARY KEY (id)
    );
END;
GO

IF OBJECT_ID(N'dbo.analyses', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.analyses
    (
        id UNIQUEIDENTIFIER NOT NULL,
        resume_id UNIQUEIDENTIFIER NOT NULL,
        job_description_id UNIQUEIDENTIFIER NOT NULL,
        status NVARCHAR(30) NOT NULL,

        evidenced_requirements NVARCHAR(MAX) NOT NULL
            CONSTRAINT DF_analyses_evidenced_requirements
            DEFAULT N'[]',

        unevidenced_requirements NVARCHAR(MAX) NOT NULL
            CONSTRAINT DF_analyses_unevidenced_requirements
            DEFAULT N'[]',

        gaps NVARCHAR(MAX) NOT NULL
            CONSTRAINT DF_analyses_gaps
            DEFAULT N'[]',

        resume_issues NVARCHAR(MAX) NOT NULL
            CONSTRAINT DF_analyses_resume_issues
            DEFAULT N'[]',

        suggestions NVARCHAR(MAX) NOT NULL
            CONSTRAINT DF_analyses_suggestions
            DEFAULT N'[]',

        created_at DATETIME2 NOT NULL
            CONSTRAINT DF_analyses_created_at
            DEFAULT SYSUTCDATETIME(),

        completed_at DATETIME2 NULL,

        CONSTRAINT PK_analyses
            PRIMARY KEY (id),

        CONSTRAINT FK_analyses_job_description
            FOREIGN KEY (job_description_id)
            REFERENCES dbo.job_descriptions(id),

        CONSTRAINT CK_analyses_status
            CHECK (
                status IN (
                    N'PENDING',
                    N'PROCESSING',
                    N'COMPLETED',
                    N'FAILED'
                )
            )
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_analyses_job_description_id'
      AND object_id = OBJECT_ID(N'dbo.analyses')
)
BEGIN
    CREATE INDEX IX_analyses_job_description_id
        ON dbo.analyses(job_description_id);
END;
GO
