
IF OBJECT_ID(N'dbo.analysis_queue', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.analysis_queue
    (
        id UNIQUEIDENTIFIER NOT NULL,
        analysis_id UNIQUEIDENTIFIER NOT NULL,
        payload_ciphertext VARBINARY(MAX) NOT NULL,
        status NVARCHAR(20) NOT NULL
            CONSTRAINT DF_analysis_queue_status
            DEFAULT N'PENDING',
        attempts INT NOT NULL
            CONSTRAINT DF_analysis_queue_attempts
            DEFAULT 0,
        created_at DATETIME2 NOT NULL
            CONSTRAINT DF_analysis_queue_created_at
            DEFAULT SYSUTCDATETIME(),
        started_at DATETIME2 NULL,
        finished_at DATETIME2 NULL,
        last_error NVARCHAR(1000) NULL,

        CONSTRAINT PK_analysis_queue
            PRIMARY KEY (id),

        CONSTRAINT UQ_analysis_queue_analysis
            UNIQUE (analysis_id),

        CONSTRAINT FK_analysis_queue_analysis
            FOREIGN KEY (analysis_id)
            REFERENCES dbo.analyses(id),

        CONSTRAINT CK_analysis_queue_status
            CHECK (
                status IN (
                    N'PENDING',
                    N'PROCESSING',
                    N'COMPLETED',
                    N'FAILED'
                )
            ),

        CONSTRAINT CK_analysis_queue_attempts
            CHECK (attempts >= 0)
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_analysis_queue_pending'
      AND object_id = OBJECT_ID(N'dbo.analysis_queue')
)
BEGIN
    CREATE INDEX IX_analysis_queue_pending
        ON dbo.analysis_queue(status, created_at);
END;
GO
