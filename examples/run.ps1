# Exemplo de execução do pipeline KML → DXF
# Execute este script no PowerShell com o ambiente virtual ativado

$input = "../examples/sample.kml"
$output = "../examples/out.dxf"

python ../main.py --input $input --output $output --dataset etopo --batch-size 100 --formats dxf

Write-Host "DXF gerado em $output"
