import boto3
import json
import urllib3

SUCCESS = "SUCCESS"
FAILED = "FAILED"
http = urllib3.PoolManager()

# Intended to the invoked by an AWS CloudFormation custom resource, this Lambda function invokes the AWS Connect API to create
# a Contact Flow in the designated AWS Connect instance.
def lambda_handler(event, context):
    responseObject = {}
    responseData = {}

    # Get event parameters passed from cfn custom resource
    try:
        connectInstanceArn = event["ResourceProperties"]["InstanceArn"]
        generateVanityNumberArn = event["ResourceProperties"]["LambdaFunctionArn"]
        deploymentEnvironment = event["ResourceProperties"]["Environment"]
    except KeyError as e:
        print("Missing required event paramters. Expected InstanceArn and LambdaFunctionArn")
        print(json.dumps(event))
        print(e)
        responseData["Data"] = "failure"
        sendCfnResponse(event, context, FAILED, responseData, context.function_name)
        raise SystemExit

    # Invoke Connect API to put contact flow with Lambda ARN inserted into specified Connect Instance
    try:
        connectClient = boto3.client("connect")
        connectClient.create_contact_flow(
            InstanceId = getInstanceIdFromArn(connectInstanceArn),
            Name = 'vf_main-inbound-{}'.format(deploymentEnvironment),
            Type = 'CONTACT_FLOW',
            Content = getFlowContent(generateVanityNumberArn)
        )
    except Exception as e:
        print("There has been an error creating your contact flow")
        print(json.dumps(event))
        print(e)
        responseData["Data"] = "failure"
        sendCfnResponse(event, context, FAILED, responseData, context.function_name)
        raise SystemExit
    
    responseData["Data"] = "success!"
    sendCfnResponse(event, context, SUCCESS, responseData, context.function_name)
    return responseObject

# Places Lambda function Arn into the JSON definition of the AWS Connect contact flow to be created
def getFlowContent(lambdaArn):
    # There HAS to be a better way of doing this!?
    # I have done the good old fashioned 'string' + variable + 'string' to get the Lambda Arn into the flow content
    contactFlowJson = '{\"Version\":\"2019-10-30\",\"StartAction\":\"c911899c-32a8-42d0-9156-77544b240563\",\"Metadata\":{\"entryPointPosition\":{\"x\":15,\"y\":15},\"snapToGrid\":false,\"ActionMetadata\":{\"c911899c-32a8-42d0-9156-77544b240563\":{\"position\":{\"x\":179,\"y\":56}},\"d2ece386-7d6b-4621-9df8-2051ebcfaedb\":{\"position\":{\"x\":447,\"y\":126}},\"f8802bed-2238-4399-ab5b-639b9e2a712a\":{\"position\":{\"x\":705,\"y\":194},\"useDynamic\":false},\"1f7dc0c9-e7bf-459d-ab32-4f1f22779fb8\":{\"position\":{\"x\":1271,\"y\":774},\"dynamicMetadata\":{},\"useDynamic\":false},\"38c550a5-4820-43a8-8065-f780a663d512\":{\"position\":{\"x\":1571,\"y\":350},\"useDynamic\":false},\"a918430b-9b14-4e27-9a5b-e53bfa80b642\":{\"position\":{\"x\":1844,\"y\":604},\"useDynamic\":false},\"f26d915e-b841-4620-aee4-9e9eb6bb193d\":{\"position\":{\"x\":1847,\"y\":307},\"useDynamic\":false},\"4485cb67-94e5-464d-a35b-6fbff977935f\":{\"position\":{\"x\":973,\"y\":241},\"conditionMetadata\":[{\"id\":\"b5ccd1b0-5236-47b6-b0c9-5b8efc336c5e\",\"operator\":{\"name\":\"Equals\",\"value\":\"Equals\",\"shortDisplay\":\"=\"},\"value\":\"anonymous\"}]},\"1a7af335-726e-40fb-9004-8e6cecdc250c\":{\"position\":{\"x\":1282,\"y\":269},\"useDynamic\":false,\"useDynamicForEncryptionKeys\":true,\"useDynamicForTerminatorDigits\":false,\"countryCodePrefix\":\"+44\"},\"e05e8c2e-f5fb-41ae-a3c6-bee781aef668\":{\"position\":{\"x\":2164,\"y\":849}},\"6aba3ab4-29f4-47e6-a977-39520b4cfee8\":{\"position\":{\"x\":1547,\"y\":840},\"conditionMetadata\":[{\"id\":\"79d785da-e2a7-43db-b23b-22f56cff3dba\",\"operator\":{\"name\":\"Equals\",\"value\":\"Equals\",\"shortDisplay\":\"=\"},\"value\":\"success\"}]},\"774fd058-a646-4af2-b561-83d688de215e\":{\"position\":{\"x\":1854,\"y\":906},\"useDynamic\":false}}},\"Actions\":[{\"Identifier\":\"c911899c-32a8-42d0-9156-77544b240563\",\"Parameters\":{\"FlowLoggingBehavior\":\"Enabled\"},\"Transitions\":{\"NextAction\":\"d2ece386-7d6b-4621-9df8-2051ebcfaedb\",\"Errors\":[],\"Conditions\":[]},\"Type\":\"UpdateFlowLoggingBehavior\"},{\"Identifier\":\"d2ece386-7d6b-4621-9df8-2051ebcfaedb\",\"Parameters\":{\"RecordingBehavior\":{\"RecordedParticipants\":[]}},\"Transitions\":{\"NextAction\":\"f8802bed-2238-4399-ab5b-639b9e2a712a\",\"Errors\":[],\"Conditions\":[]},\"Type\":\"UpdateContactRecordingBehavior\"},{\"Identifier\":\"f8802bed-2238-4399-ab5b-639b9e2a712a\",\"Parameters\":{\"SSML\":\"<speak>Thank you for calling Oliver Hanson-Bragg\'s Voice Foundry vanity number generator.</speak>\"},\"Transitions\":{\"NextAction\":\"4485cb67-94e5-464d-a35b-6fbff977935f\",\"Errors\":[],\"Conditions\":[]},\"Type\":\"MessageParticipant\"},{\"Identifier\":\"1f7dc0c9-e7bf-459d-ab32-4f1f22779fb8\",\"Parameters\":{\"LambdaFunctionARN\":\"' + lambdaArn + '\",\"InvocationTimeLimitSeconds\":\"3\"},\"Transitions\":{\"NextAction\":\"6aba3ab4-29f4-47e6-a977-39520b4cfee8\",\"Errors\":[{\"NextAction\":\"6aba3ab4-29f4-47e6-a977-39520b4cfee8\",\"ErrorType\":\"NoMatchingError\"}],\"Conditions\":[]},\"Type\":\"InvokeLambdaFunction\"},{\"Identifier\":\"38c550a5-4820-43a8-8065-f780a663d512\",\"Parameters\":{\"LoopCount\":\"3\"},\"Transitions\":{\"NextAction\":\"a918430b-9b14-4e27-9a5b-e53bfa80b642\",\"Errors\":[],\"Conditions\":[{\"NextAction\":\"a918430b-9b14-4e27-9a5b-e53bfa80b642\",\"Condition\":{\"Operator\":\"Equals\",\"Operands\":[\"DoneLooping\"]}},{\"NextAction\":\"f26d915e-b841-4620-aee4-9e9eb6bb193d\",\"Condition\":{\"Operator\":\"Equals\",\"Operands\":[\"ContinueLooping\"]}}]},\"Type\":\"Loop\"},{\"Identifier\":\"a918430b-9b14-4e27-9a5b-e53bfa80b642\",\"Parameters\":{\"SSML\":\"<speak>There has been an error and we are unable to process your call. Please try again later.</speak>\"},\"Transitions\":{\"NextAction\":\"e05e8c2e-f5fb-41ae-a3c6-bee781aef668\",\"Errors\":[],\"Conditions\":[]},\"Type\":\"MessageParticipant\"},{\"Identifier\":\"f26d915e-b841-4620-aee4-9e9eb6bb193d\",\"Parameters\":{\"SSML\":\"<speak>I\'m sorry, that\'s not a valid number. Please try again.</speak>\"},\"Transitions\":{\"NextAction\":\"1a7af335-726e-40fb-9004-8e6cecdc250c\",\"Errors\":[],\"Conditions\":[]},\"Type\":\"MessageParticipant\"},{\"Identifier\":\"4485cb67-94e5-464d-a35b-6fbff977935f\",\"Parameters\":{\"ComparisonValue\":\"$.CustomerEndpoint.Address\"},\"Transitions\":{\"NextAction\":\"1f7dc0c9-e7bf-459d-ab32-4f1f22779fb8\",\"Errors\":[{\"NextAction\":\"1f7dc0c9-e7bf-459d-ab32-4f1f22779fb8\",\"ErrorType\":\"NoMatchingCondition\"}],\"Conditions\":[{\"NextAction\":\"1a7af335-726e-40fb-9004-8e6cecdc250c\",\"Condition\":{\"Operator\":\"Equals\",\"Operands\":[\"anonymous\"]}}]},\"Type\":\"Compare\"},{\"Identifier\":\"1a7af335-726e-40fb-9004-8e6cecdc250c\",\"Parameters\":{\"SSML\":\"<speak>The number that you are calling from is withheld. To use this service, please enter a valid UK telephone number.</speak>\",\"StoreInput\":\"True\",\"InputTimeLimitSeconds\":\"5\",\"InputValidation\":{\"PhoneNumberValidation\":{\"NumberFormat\":\"Local\",\"CountryCode\":\"GB\"}}},\"Transitions\":{\"NextAction\":\"1f7dc0c9-e7bf-459d-ab32-4f1f22779fb8\",\"Errors\":[{\"NextAction\":\"a918430b-9b14-4e27-9a5b-e53bfa80b642\",\"ErrorType\":\"NoMatchingError\"},{\"NextAction\":\"38c550a5-4820-43a8-8065-f780a663d512\",\"ErrorType\":\"InvalidPhoneNumber\"}],\"Conditions\":[]},\"Type\":\"GetParticipantInput\"},{\"Identifier\":\"e05e8c2e-f5fb-41ae-a3c6-bee781aef668\",\"Type\":\"DisconnectParticipant\",\"Parameters\":{},\"Transitions\":{}},{\"Identifier\":\"6aba3ab4-29f4-47e6-a977-39520b4cfee8\",\"Parameters\":{\"ComparisonValue\":\"$.External.status\"},\"Transitions\":{\"NextAction\":\"a918430b-9b14-4e27-9a5b-e53bfa80b642\",\"Errors\":[{\"NextAction\":\"a918430b-9b14-4e27-9a5b-e53bfa80b642\",\"ErrorType\":\"NoMatchingCondition\"}],\"Conditions\":[{\"NextAction\":\"774fd058-a646-4af2-b561-83d688de215e\",\"Condition\":{\"Operator\":\"Equals\",\"Operands\":[\"success\"]}}]},\"Type\":\"Compare\"},{\"Identifier\":\"774fd058-a646-4af2-b561-83d688de215e\",\"Parameters\":{\"SSML\":\"<speak>\\nYour three vanity numbers are <break time=\\\"200ms\\\"/>\\n$.External.vanity0 <break time=\\\"100ms\\\"/>\\n$.External.vanity1<break time=\\\"100ms\\\"/>\\nand finally <break time=\\\"100ms\\\"/>\\n$.External.vanity2\\n</speak>\"},\"Transitions\":{\"NextAction\":\"e05e8c2e-f5fb-41ae-a3c6-bee781aef668\",\"Errors\":[],\"Conditions\":[]},\"Type\":\"MessageParticipant\"}]}'
    return contactFlowJson

# Takes an AWS Connect Instance ARN and returns only the Instance Id
def getInstanceIdFromArn(connectArn):
    instanceId = connectArn.rstrip("instance/")
    instanceId = connectArn.split("/")
    return instanceId[len(instanceId)-1]

# Send a response back to CloudFormation. 
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html
def sendCfnResponse(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False, reason=None):
    responseUrl = event['ResponseURL']

    print(responseUrl)

    responseBody = {
        'Status' : responseStatus,
        'Reason' : reason or "See the details in CloudWatch Log Stream: {}".format(context.log_stream_name),
        'PhysicalResourceId' : physicalResourceId or context.log_stream_name,
        'StackId' : event['StackId'],
        'RequestId' : event['RequestId'],
        'LogicalResourceId' : event['LogicalResourceId'],
        'NoEcho' : noEcho,
        'Data' : responseData
    }

    json_responseBody = json.dumps(responseBody)

    print("Response body:")
    print(json_responseBody)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }

    try:
        response = http.request('PUT', responseUrl, headers=headers, body=json_responseBody)
        print("Status code:", response.status)


    except Exception as e:

        print("send(..) failed executing http.request(..):", e)