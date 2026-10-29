# Timeout de análise no frontend

O polling do status da análise possui um limite total de cinco minutos, contado a partir do início do acompanhamento após a API aceitar a análise.

Se a análise continuar pendente ou em processamento após esse limite, o frontend encerra o acompanhamento e apresenta uma mensagem orientando a pessoa usuária. Isso não cancela o processamento no servidor e não cria nem envia automaticamente outra análise. Uma nova tentativa só ocorre por ação explícita da pessoa usuária.

A cobertura unitária de `AnalysisService` verifica a conclusão normal, o limite de espera e a mensagem apresentada no timeout. Os testes usam HTTP simulado e não dependem de API real.
