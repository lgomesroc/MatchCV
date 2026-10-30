USE MatchCVTest;
GO

/*
    MatchCV - Migration 009 (test database)
    Mantém o schema de teste compatível com descrições de até 15000 caracteres.
*/
IF OBJECT_ID(N'dbo.job_descriptions', N'U') IS NOT NULL
BEGIN
    ALTER TABLE dbo.job_descriptions
        ALTER COLUMN content NVARCHAR(MAX) NOT NULL;
END;
GO
