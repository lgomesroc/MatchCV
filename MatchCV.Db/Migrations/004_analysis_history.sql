IF COL_LENGTH('dbo.analyses', 'user_id') IS NULL
BEGIN
    ALTER TABLE dbo.analyses
    ADD user_id UNIQUEIDENTIFIER NULL;
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.foreign_keys
    WHERE name = 'FK_analyses_users'
)
BEGIN
    ALTER TABLE dbo.analyses
    ADD CONSTRAINT FK_analyses_users
    FOREIGN KEY (user_id)
    REFERENCES dbo.users(id);
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_analyses_user_created_at'
      AND object_id = OBJECT_ID('dbo.analyses')
)
BEGIN
    CREATE INDEX IX_analyses_user_created_at
    ON dbo.analyses(user_id, created_at DESC);
END;
GO
