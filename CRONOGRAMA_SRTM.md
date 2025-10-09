# CRONOGRAMA DE MIGRAÇÃO: ASTER → SRTM (OpenTopoData)

## Objetivo
Planejar e executar a substituição da fonte de elevação ASTER pelo SRTM (preferencialmente srtm30m) em todos os fluxos do pipeline KML_DXF.

---

## 1. Levantamento e Análise (Dia 1)
- Levantar todos os pontos do pipeline que usam o dataset 'aster30m'.
- Analisar diferenças técnicas entre ASTER e SRTM (cobertura, resolução, precisão, limitações).
- Identificar possíveis impactos em áreas fora de -60 a 60 graus latitude (limite do SRTM).

## 2. Atualização de Scripts e Configurações (Dia 2)
- Atualizar scripts, exemplos e documentação para usar 'srtm30m' como padrão (--dataset srtm30m).
- Garantir que todos os testes automatizados cubram o novo dataset.
- Atualizar caches e caminhos de saída para não misturar resultados ASTER/SRTM.

## 3. Testes Comparativos e Validação (Dias 3-4)
- Executar o pipeline em amostras reais (KMLs de diferentes regiões) usando ASTER e SRTM.
- Comparar estatísticas de elevação, cobertura e eventuais falhas (nulls, gaps).
- Validar se a troca não afeta negativamente a qualidade dos resultados.

## 4. Ajustes Finais e Documentação (Dia 5)
- Corrigir eventuais problemas detectados nos testes.
- Atualizar README, exemplos e instruções de uso para destacar o novo padrão.
- Comunicar a mudança aos usuários (changelog, README, aviso em PR/issue).

## 5. Monitoramento Pós-Migração (Dia 6+)
- Monitorar resultados e feedback dos usuários.
- Reverter ou ajustar rapidamente caso surjam problemas graves.

---

## Observações
- Para migrar basta trocar o parâmetro --dataset de 'aster30m' para 'srtm30m' na chamada da API.
- SRTM é mais confiável em áreas não montanhosas e menos sujeito a artefatos de nuvem.
- Para áreas polares ou fora de -60 a 60 graus, considerar fallback para ASTER ou outro dataset.
- Referência oficial: https://www.opentopodata.org/datasets/srtm/

---

**Checklist de migração:**
- [ ] Scripts e exemplos atualizados
- [ ] Testes automatizados cobrindo SRTM
- [ ] Resultados comparados e validados
- [ ] Documentação revisada
- [ ] Comunicação realizada
