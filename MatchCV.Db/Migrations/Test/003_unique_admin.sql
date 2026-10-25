SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET ARITHABORT ON;
SET NUMERIC_ROUNDABORT OFF;
GO

USE MatchCVTest;
GO

IF (
    SELECT COUNT_BIG(*)
    FROM dbo.users
    WHERE role = 'ADMIN'
) > 1
BEGIN
    THROW 50001,
        'Existem múltiplos administradores. Corrija os dados antes da migração.',
        1;
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'UX_users_single_admin'
      AND object_id = OBJECT_ID('dbo.users')
)
BEGIN
    CREATE UNIQUE INDEX UX_users_single_admin
        ON dbo.users(role)
        WHERE role = 'ADMIN';
END;
GO
