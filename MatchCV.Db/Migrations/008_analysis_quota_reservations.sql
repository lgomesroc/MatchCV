/*
    MatchCV - Migration 008
    Reservas da cota mensal de análises gratuitas.

    RESERVED ocupa uma vaga enquanto a análise está na fila/em processamento.
    COMPLETED mantém a vaga consumida no mês.
    RELEASED libera a vaga após falha técnica.
*/
IF OBJECT_ID(N'dbo.analysis_quota_reservations', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.analysis_quota_reservations
    (
        id UNIQUEIDENTIFIER NOT NULL,
        user_id UNIQUEIDENTIFIER NOT NULL,
        analysis_id UNIQUEIDENTIFIER NULL,
        month_start DATE NOT NULL,
        status NVARCHAR(20) NOT NULL
            CONSTRAINT DF_analysis_quota_reservations_status
            DEFAULT N'RESERVED',
        created_at DATETIME2(7) NOT NULL
            CONSTRAINT DF_analysis_quota_reservations_created_at
            DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2(7) NOT NULL
            CONSTRAINT DF_analysis_quota_reservations_updated_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_analysis_quota_reservations
            PRIMARY KEY (id),

        CONSTRAINT FK_analysis_quota_reservations_user
            FOREIGN KEY (user_id)
            REFERENCES dbo.users(id),

        CONSTRAINT FK_analysis_quota_reservations_analysis
            FOREIGN KEY (analysis_id)
            REFERENCES dbo.analyses(id),

        CONSTRAINT CK_analysis_quota_reservations_status
            CHECK (status IN (N'RESERVED', N'COMPLETED', N'RELEASED'))
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_analysis_quota_reservations_month_user_status'
      AND object_id = OBJECT_ID(N'dbo.analysis_quota_reservations')
)
BEGIN
    CREATE INDEX IX_analysis_quota_reservations_month_user_status
        ON dbo.analysis_quota_reservations(user_id, month_start, status);
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'UX_analysis_quota_reservations_analysis'
      AND object_id = OBJECT_ID(N'dbo.analysis_quota_reservations')
      AND is_unique = 1
)
BEGIN
    CREATE UNIQUE INDEX UX_analysis_quota_reservations_analysis
        ON dbo.analysis_quota_reservations(analysis_id)
        WHERE analysis_id IS NOT NULL;
END;
GO
