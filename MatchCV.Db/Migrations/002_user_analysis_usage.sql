IF OBJECT_ID(N'dbo.user_analysis_usage', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.user_analysis_usage
    (
        id UNIQUEIDENTIFIER NOT NULL,
        user_id UNIQUEIDENTIFIER NOT NULL,
        created_at DATETIME2 NOT NULL
            CONSTRAINT DF_user_analysis_usage_created_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_user_analysis_usage
            PRIMARY KEY (id),

        CONSTRAINT FK_user_analysis_usage_user
            FOREIGN KEY (user_id)
            REFERENCES dbo.users(id)
    );

    CREATE INDEX IX_user_analysis_usage_user_id
        ON dbo.user_analysis_usage(user_id);
END;
