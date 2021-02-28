@echo off
set directory=%CD%
echo %directory%
cd aws-resources/backend

rem Set variables from command line arguments
rem e.g. ./deploy_backend.bat {region} {environment(dev/test/prod)} {connectInstanceArn}
set region=%1
set clientName=vf
set environment=%2
set connectInstanceArn=%3

rem Deploy deployment-bucket.yml cfn template to create the S3 bucket that holds the rest of the deployment
aws cloudformation deploy ^
--region %region% ^
--template-file deployment-bucket.yml ^
--stack-name cfn-voicefoundry-connect-%environment%-deploymentBucket ^
--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM ^
--parameter-overrides ^
    pClientLowerCase=%clientName% ^
    pEnvironmentLowerCase=%environment%

rem Package and deploy backend-deployment.yml then tidy up
aws cloudformation package ^
--region %region% ^
--template-file backend-deployment.yml ^
--s3-bucket s3-%clientName%-vannums-%environment%-%region%-deployment ^
--output-template-file deploy-backend-deployment.yml

aws cloudformation deploy ^
--region %region% ^
--template-file deploy-backend-deployment.yml ^
--stack-name cfn-voicefoundry-connect-%environment%-vanityNumbers ^
--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM ^
--parameter-overrides ^
    pConnectInstanceArn=%connectInstanceArn% ^
    pClientLowerCase=%clientName% ^
    pEnvironmentLowerCase=%environment%

del deploy-backend-deployment.yml
cd %directory%