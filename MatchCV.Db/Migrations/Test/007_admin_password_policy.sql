USE MatchCVTest;
GO


/*
    MatchCV - Migration 007
    Controle de troca e recuperação da senha administrativa.

    Regras previstas:
    - Troca normal: intervalo mínimo de 30 dias.
    - Aos 90 dias, a troca normal passa a ser obrigatória.
    - Recuperação: até 3 utilizações consecutivas.
    - Após a terceira recuperação, bloqueio por 15 dias.
    - Após o bloqueio, o contador poderá ser reiniciado pelo script.

    Esta migration cria somente a estrutura de controle.
    Ela não altera a senha nem implementa os scripts.
*/

IF OBJECT_ID(N'dbo.admin_password_policy', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.admin_password_policy
    (
        id INT NOT NULL,
        admin_user_id UNIQUEIDENTIFIER NOT NULL,

        last_normal_change_at DATETIME2(7) NULL,

        last_reset_at DATETIME2(7) NULL,
        reset_count INT NOT NULL
            CONSTRAINT DF_admin_password_policy_reset_count
            DEFAULT (0),

        reset_blocked_until DATETIME2(7) NULL,

        created_at DATETIME2(7) NOT NULL
            CONSTRAINT DF_admin_password_policy_created_at
            DEFAULT SYSUTCDATETIME(),

        updated_at DATETIME2(7) NOT NULL
            CONSTRAINT DF_admin_password_policy_updated_at
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_admin_password_policy
            PRIMARY KEY (id),

        CONSTRAINT CK_admin_password_policy_singleton
            CHECK (id = 1),

        CONSTRAINT CK_admin_password_policy_reset_count
            CHECK (reset_count BETWEEN 0 AND 3),

        CONSTRAINT FK_admin_password_policy_admin
            FOREIGN KEY (admin_user_id)
            REFERENCES dbo.users(id),

        CONSTRAINT UQ_admin_password_policy_admin
            UNIQUE (admin_user_id)
    );
END;
GO
