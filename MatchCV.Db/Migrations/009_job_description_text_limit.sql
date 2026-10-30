/*
    MatchCV - Migration 009
    Aumenta o tamanho persistido da descrição da vaga para suportar 15000 caracteres.

    SQL Server limita NVARCHAR(n) a 4000 unidades; NVARCHAR(MAX) é necessário
    para armazenar descrições de até 15000 caracteres.
*/
IF OBJECT_ID(N'dbo.job_descriptions', N'U') IS NOT NULL
BEGIN
    ALTER TABLE dbo.job_descriptions
        ALTER COLUMN content NVARCHAR(MAX) NOT NULL;
END;
GO
