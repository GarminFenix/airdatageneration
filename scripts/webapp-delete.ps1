$resourceGroup = "AirDataGeneration"
$appName = "AirDataGeneration"

# Delete the web app
az webapp delete --name $appName --resource-group $resourceGroup
