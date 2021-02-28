import boto3
import json
import time
import os

# Intended to be invokved by a Lambda Proxy method in AWS API Gateway, this Lambda function returns the five newest records
# from the specified DynamoDB table.
def lambda_handler(event, context):
    # Create basic response object
    responseBody = {}
    responseObject = {}
    responseObject["statusCode"] = {}
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json"
    responseObject["headers"]["Access-Control-Allow-Methods"] = "GET"
    responseObject["headers"]["Access-Control-Allow-Origin"] = "*"
    responseObject["body"] = {}
    responseObject["isBase64Encoded"] = "false"

    # Get environment variables and create dynamodb resource
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['ddbTable'])
    except Exception as e:
        print("Error with Lambda function environment variable(s): {}".format(e))
        responseObject["statusCode"] = 500
        responseObject["body"] = json.dumps("There has been an unrecoverable error in processing your request. Please try again later")

    # Scan dynamodb and return the five most recent results
    try:
        # Scan DB to return callernumber, utctime, and vanitynumbers for each record
        response = table.scan(
            ProjectionExpression="callernumber, utctime, vanitynumbers"
        )

        # If any records are returned, take five most recent records
        if len(response["Items"]) > 0:
            # Sort all returned items by newest first
            response["Items"].sort(key=getUtcTime, reverse=True)

            # Create a new list of the first five (newest) items
            newestFiveResults = response["Items"][:5]

            # Add a record into our responseBody object for each item in our list of items. Epoch
            # timestamp is converted to human readable
            counter = 1
            for each in newestFiveResults:
                responseBody["result{}".format(counter)] = {}
                responseBody["result{}".format(counter)]["callerNumber"] = each["callernumber"]
                responseBody["result{}".format(counter)]["displayTime"] = formatEpoch(each["utctime"])
                responseBody["result{}".format(counter)]["vanitynumbers"] = each["vanitynumbers"]
                counter += 1
            
            # Add responseBody into responseObject
            responseObject["body"] = json.dumps(responseBody)
            responseObject["statusCode"] = 200
        else:
            responseObject["statusCode"] = 404
            responseObject["body"] = json.dumps("No records found")

    except Exception as e:
        print("Error reading DynamoDB and processing retrieved data: {}".format(e))
        responseObject["statusCode"] = 500
        responseObject["body"] = json.dumps("There has been an unrecoverable error in processing your request. Please try again later")

    # Return response object to API Gateway / browser
    return responseObject

# Takes an epoch timestamp (in seconds) and returns a human readable UTC timestamp in format YYYY-MM-DD HH:MM:SS
def formatEpoch(epochTimeStampInSecs):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epochTimeStampInSecs))

# Returns the value of key named utctime in the passed record object
def getUtcTime(record):
    return record.get("utctime")