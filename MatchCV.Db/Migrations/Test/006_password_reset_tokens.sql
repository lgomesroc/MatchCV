USE MatchCVTest;
GO

IF OBJECT_ID('dbo.password_reset_tokens', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.password_reset_tokens (
        token_hash CHAR(64) NOT NULL PRIMARY KEY,
        user_id UNIQUEIDENTIFIER NOT NULL,
        created_at DATETIME2(7) NOT NULL,
        expires_at DATETIME2(7) NOT NULL,
        used_at DATETIME2(7) NULL,
        CONSTRAINT FK_password_reset_tokens_users FOREIGN KEY (user_id) REFERENCES dbo.users(id)
    );
END;
GO
