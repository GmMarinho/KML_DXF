# Exemplo de execução do pipeline KML → DXF
# Execute este script no PowerShell com o ambiente virtual ativado

$input = "../examples/sample.kml"
$output = "../examples/dxf/out.dxf"
$cache = "../examples/cache/elev_cache_sample.json"
$metrics = "../examples/metrics/metrics_sample.json"

python ../main.py --input $input --output $output --dataset etopo --batch-size 100 --enable-cache --cache-file $cache --log-json --log-json-file $metrics

Write-Host "DXF gerado em $output"
