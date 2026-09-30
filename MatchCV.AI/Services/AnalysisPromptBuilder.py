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

4. Ausência de evidência não significa necessariamente ausência
   de conhecimento ou experiência do candidato.

5. Identifique possíveis lacunas entre os requisitos da vaga e
   aquilo que está evidenciado no currículo.

6. Identifique problemas objetivos de conteúdo ou apresentação
   que possam prejudicar a compreensão do currículo.

7. As sugestões devem ser baseadas exclusivamente nas informações
   disponíveis.

8. Nunca sugira que o candidato invente experiência, formação,
   tecnologia, certificação ou resultado.

9. Responda exclusivamente no formato JSON solicitado.
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
        return (
            f"{cls.SYSTEM_PROMPT}\n\n"
            f"DESCRIÇÃO DA VAGA:\n"
            f"{job_description}\n\n"
            f"CURRÍCULO:\n"
            f"{resume_text}\n\n"
            f"FORMATO DE RESPOSTA:\n"
            f"{cls.OUTPUT_FORMAT}"
        )
