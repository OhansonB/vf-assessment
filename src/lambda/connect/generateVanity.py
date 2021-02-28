import boto3
import json
import os
import time
import random

# Intended to be invoked wtihin AWS Connect, this function generates five words based on the callers telephone number and puts
# them into a DynamoDB table. Three of the five results are returned to AWS Connect to be played back the caller.
def lambda_handler(event, context):
    responseObject = {}

    # Sample event for Lambda function
    # {
    #     "Details": {
    #         "ContactData": {
    #             "ContactId": "4a573372-1f28-4e26-b97b-XXXXXXXXXXX",
    #             "CustomerEndpoint": {
    #                 "Address": "+447772707934"
    #             }
    #         }
    #     }
    # }

    # Get parameters from Lambda environment variables and event object from Connect.
    try:
        callerNumber = event["Details"]["ContactData"]["CustomerEndpoint"]["Address"]
        contactId = event["Details"]["ContactData"]["ContactId"]

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['ddbTable'])

        if callerNumber == "anonymous":
            responseObject["status"] = "error"
            print("Caller number is anonymous, exiting")
            return responseObject

    except KeyError as e:
        print("Missing event parameters")
        print(json.dumps(event))
        print(e)
        responseObject["status"] = "error"
        return responseObject

   # Take the last six digits of the callers number; convert those six digits into all possible permutations of characters 
   # according to telephone number pad; select a random five of those permutations and log into dynamodb; return three of the
   # five to Connect to playback to customer.
    try:
        # Identify prefix of callers number (i.e. all but the last six digits, and insert "-"" on the end)
        callerPrefix = callerNumber[:-6] + "-"

        # Create a list of vanity numbers based on the last six digits on the callers number
        callerVanityNumberList = getWordsFromNumber(callerNumber[-6:])

        # Add the callers number prefix to the vanity numbers generate
        for each in range(len(callerVanityNumberList)):
            callerVanityNumberList[each] = callerPrefix + callerVanityNumberList[each]
        
        # Add contact Id, current time, callers original number, and list of vanity numbers into DynamoDB
        table.update_item(
            Key = {
                "contactid": contactId
            },
            UpdateExpression = "set utctime=:time, callernumber=:callerNumber, vanitynumbers=:vanityNumbers",
            ExpressionAttributeValues = {
                ":time": int(time.time()),
                ":callerNumber": callerNumber,
                ":vanityNumbers": json.dumps(callerVanityNumberList)
            }
        )

        # Generate a response object to pass to connect, containing the first three of the five numbers generated
        for each in range(3):
            responseObject["vanity{}".format(each)] = callerVanityNumberList[each]
        
        responseObject["status"] = "success"

    except Exception as e:
        print("There has been an error processing the telephone number")
        print(json.dumps(event))
        print(e)
        responseObject["status"] = "error"
        return responseObject

    return responseObject

# Takes a vanity number and replaces 0 and 1 with o and i respectively
def formatVanityNumber(word):
    connectString = ""
    
    counter = 0
    for each in word:
        if (each == "0"):
            word[counter] = "o"
        elif (each == "1"):
            word[counter] = "i"
        counter += 1
        
    connectString = ''.join(word)
    return connectString

# Defines the map of telephone number digits and the corresponding possible letters; generates all possible combinations of letters
# based on the telephone number provided; and then returns a random selection of five of those combinations
def getWordsFromNumber(numberString):
    # Define a dictionary of lists representing each digit on a telephone keypad and the corresponding letters
    numberLetterMap = {}
    numberLetterMap["0"] = ["0"]
    numberLetterMap["1"] = ["1"]
    numberLetterMap["2"] = ["a", "b", "c"]
    numberLetterMap["3"] = ["d", "e", "f"]
    numberLetterMap["4"] = ["g", "h", "i"]
    numberLetterMap["5"] = ["j", "k", "l"]
    numberLetterMap["6"] = ["m", "n", "o"]
    numberLetterMap["7"] = ["p", "q", "r", "s"]
    numberLetterMap["8"] = ["t", "u", "v"]
    numberLetterMap["9"] = ["w", "x", "y", "z"]

    # Create a list containing the possible letters for each digit in the parameter passed to the function
    letterCombinations = []
    for each in numberString:
        letterCombinations.append(numberLetterMap[each])

    # Create a list of lists containing all possible combinations of the characters in the letterCombinations list
    # https://stackoverflow.com/questions/798854/all-combinations-of-a-list-of-lists
    outlist =[]; templist =[[]]

    for sublist in letterCombinations:
        outlist = templist; templist = [[]]
        for sitem in sublist:
            for oitem in outlist:
                newitem = [oitem]
                if newitem == [[]]: newitem = [sitem]
                else: newitem = [newitem[0], sitem]
                templist.append(flatten(newitem))

    outlist = list(filter(lambda x: len(x)==len(letterCombinations), templist))
    
    # Create a new list containing a random five of the letter combinations
    vanityWordList = []
    for each in range(5):
        vanityWordList.append(formatVanityNumber(outlist[random.randint(0, (len(outlist)-1))]))

    return vanityWordList

def flatten(B):
    A = []
    for i in B:
        if type(i) == list: A.extend(i)
        else: A.append(i)
    return A