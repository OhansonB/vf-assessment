@echo off
set directory=%CD%
echo %directory%
cd aws-resources/frontend

rem Set variables from command line arguments
rem e.g. ./deploy_backend.bat {region} {environment(dev/test/prod)}
set region=%1
set clientName=vf1
set environment=%2

rem Package and deploy cloudfront-deployment.yml then tidy up
aws cloudformation package ^
--region %region% ^
--template-file cloudfront-deployment.yml ^
--s3-bucket s3-%clientName%-vannums-%environment%-%region%-deployment ^
--output-template-file deploy-cloudfront-deployment.yml

aws cloudformation deploy ^
--region %region% ^
--template-file deploy-cloudfront-deployment.yml ^
--stack-name cfn-voicefoundry-connect-%environment%-cloudFront ^
--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM ^
--parameter-overrides ^
    pClientLowerCase=%clientName% ^
    pEnvironmentLowerCase=%environment%

rem Wouldn't /normally/ do this. Might prefer to use Code Pipeline or some such other service to run tests on the repo of the web app
rem before putting it into S3. Hardcoded here for the sake of brevity in deployment (you may need to invalidate the files in CloudFront)
aws s3 cp ./../../src/web s3://s3-vf-vannums-ENV_HERE-REGION_HERE-webapp --recursive

del deploy-cloudfront-deployment.yml
cd %directory%