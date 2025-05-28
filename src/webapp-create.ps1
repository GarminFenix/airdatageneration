$resourceGroup = "AirDataGeneration"
$appName = "AirDataGeneration"

az webapp create `
  --resource-group $resourceGroup `
  --name $appName `
  --runtime "PYTHON|3.13" `
  --plan "AppServicePlan"
