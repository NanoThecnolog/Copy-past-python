# instalação de lib:
### reportlab - gerar pdf

# Modificações no algorítmo:

## Lista de arquivos
### Agora o script aceita vários arquivos de vídeo.

## Pasta separada com os resultados
### Os vídeos convertidos são salvos em pastas individuais com os respectivos relatórios de conversão.

## Novas métricas

### WMAF - analisa a qualidade percebida do vídeo
### MS-SSIM - analisa a qualidade em multiplas escalas de forma mais detalhada

### Frame Difference - cálculo da diferença entre os quadros originais e os convertidos.

### Histograma de cor - Comparação da distribuição de cores entre o original e o convertido (cor e luminosidade).

### Frame drop - Verificação de perda de quadros durante conversão.

### Análise no tempo de conversão e uso de recurso - Medição de tempo total de conversão e uso de CPU e GPU.

## Novos relatórios

### com o reportlab, os relatórios com as métricas são salvos em PDF.