## Deploy the Azure Function

TODO

## Configure Event Grid Trigger

TODO

## Register Model
```
az ml model register -n ncd-sklearn-model -p ./sklearn_regression_model.pkl --model-framework ScikitLearn --model-framework-version 0.0.1 --cc 1 --gb 0.5 --tag ncd=true --tag stage=production -g andyxu_test_rg -w ax-cicd-canary
```