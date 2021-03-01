@echo off
set directory=%CD%
echo %directory%
cd aws-resources/api-gateway/cloudformation

rem Set variables from command line arguments
rem e.g. ./deploy_backend.bat {region} {environment(dev/test/prod)}
set region=%1
set clientName=vf1
set environment=%2

rem Package and deploy apigateway-deployment.yml then tidy up
aws cloudformation package ^
--region %region% ^
--template-file apigateway-deployment.yml ^
--s3-bucket s3-%clientName%-vannums-%environment%-%region%-deployment ^
--output-template-file deploy-apigateway-deployment.yml

aws cloudformation deploy ^
--region %region% ^
--template-file deploy-apigateway-deployment.yml ^
--stack-name cfn-voicefoundry-connect-%environment%-apiGateway ^
--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM ^
--parameter-overrides ^
    pClientLowerCase=%clientName% ^
    pEnvironmentLowerCase=%environment%

del deploy-apigateway-deployment.yml
cd %directory%