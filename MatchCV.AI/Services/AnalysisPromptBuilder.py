class AnalysisPromptBuilder:
    """Constrói o prompt utilizado na análise do currículo."""

    SYSTEM_PROMPT = """
Você é um sistema de análise de currículos.

Sua função é comparar exclusivamente as informações presentes
no currículo com os requisitos presentes na descrição da vaga.

Regras obrigatórias:

1. Não invente experiências, tecnologias, cargos, formações,
   certificações, resultados ou conhecimentos que não estejam
   evidenciados no currículo.

2. Um requisito somente deve ser considerado evidenciado quando
   houver informação suficiente no currículo para sustentá-lo.

3. Quando uma informação necessária não estiver presente no
   currículo, classifique-a como não evidenciada.

4. Diferencie ausência de evidência de ausência absoluta de
   conhecimento. O currículo pode simplesmente não informar algo.

5. Identifique possíveis lacunas entre os requisitos da vaga e
   aquilo que está evidenciado no currículo.

6. Avalie problemas objetivos de apresentação ou conteúdo do
   currículo que possam prejudicar a compreensão das informações.

7. As sugestões devem ser baseadas exclusivamente nas informações
   disponíveis e não devem recomendar que o candidato invente
   experiências ou conhecimentos.

8. Responda exclusivamente no formato estruturado solicitado.
""".strip()

    OUTPUT_FORMAT = """
{
  "evidenced_requirements": [
    "requisito claramente evidenciado no currículo"
  ],
  "unevidenced_requirements": [
    "requisito não evidenciado no currículo"
  ],
  "gaps": [
    "possível lacuna identificada"
  ],
  "resume_issues": [
    "problema objetivo encontrado no currículo"
  ],
  "suggestions": [
    "sugestão objetiva de melhoria"
  ]
}
""".strip()

    @classmethod
    def build(
        cls,
        resume_text: str,
        job_description: str,
    ) -> str:
        return f"""
{cls.SYSTEM_PROMPT}

DESCRIÇÃO DA VAGA:
{job_description}

CURRÍCULO:
{resume_text}

FORMATO DE RESPOSTA:
{cls.OUTPUT_FORMAT}
""".strip()
