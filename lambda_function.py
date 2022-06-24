import json
import redis
import boto3
from phpserialize import *

print('Loading function v: 1.0.5')
host_string = 'funcof.4yuhei.0001.usw2.cache.amazonaws.com'
#host_string ='beauty.4yuhei.0001.usw2.cache.amazonaws.com'

def lambda_handler(event, context):

    operation = event.get('httpMethod',None)
    data = {}
    print("Session lambda")    
    print(event)  
        
    
    #RESPONSE SETUP
    response = {}
    response['statusCode'] = 200
    response['headers'] = {}
    response['headers']['Content-Type'] = 'application/json'    
    #RESPONSE SETUP
    
    environment = event.get('environment',None)
    if environment == "dev":
        host_string = 'funcof.4yuhei.0001.usw2.cache.amazonaws.com'
    elif environment == "main":
        host_string = 'beauty.4yuhei.0001.usw2.cache.amazonaws.com'
    else:
        print("no environment info provided")
        data["success"] = False
        data["message"] = "no environment provided"
        response['body'] = data
        return  response

    
    data={}
    #data['event'] = str(event)
    execution_id = None
    queryStringParameters = event.get("queryStringParameters",None)
    #if queryStringParameters:
    #    print("queryStringParameters:" + str(queryStringParameters)+"  type:"+str(type(queryStringParameters) ))
    #    execution_id = queryStringParameters.get('execution_id',None)
    #    print("execution_id:" + str(execution_id)  )
    
    #if not execution_id:
    #    data["Error"] = "execution_id is a required parameter"

    if operation:
        print("Metodo: "+str(operation))
        
        #headers = str(event.get('headers',None))
        #print("headers: "+ str(headers))

        if  str(operation) == 'GET':
            print(" Get item")
            sessionId = event.get("sessionId", None)
            if not sessionId:
                print("no session info provided")
                data["success"] = False
                data["message"] = "no session provided"
                response['body'] = data
                return  response
            print(sessionId)

            # connect to redis
            r = redis.Redis(
                host=host_string,
                port=6379
            )
            print("*********GET*******")
            key = 'PHPREDIS_SESSION:' + str(sessionId)
            print('get redis key: ' + key)
            # Retrieve data from redis
            try:
                value = r.get(key)
            except (RedisError, OSError) as e:
                error_code = REDIS_EXCEPTION_ERROR_CODE
                print(error_code)
                value = None
            if(value):
                # Unserialize data stored in redis
                data = loads(value, object_hook=phpobject,decode_strings=True)
            else:
                data = {}
                data["success"] = False
                data["message"] = "result not value"

            response['body'] = data
            return  response
            
        elif  str(operation) == 'PUT':
            print(" Create item")
            print("setting up client metadata")
            country = None
            sessionId = event.get("sessionId", None)
            if not sessionId:
                print("no session info provided")
                data["success"] = False
                data["message"] = "no session provided"
                response['body'] = data
                return  response
            print(sessionId)
           
            key = 'PHPREDIS_SESSION:' + str(sessionId)
            print('PUT redis key: ' + key)
            
            # Retrieve data from redis
            data = dumps(queryStringParameters, object_hook=phpobject)
            #data = queryStringParameters
            # connect to redis
            r = redis.Redis(
                host=host_string,
                port=6379
            )
            print("*********PUT*******")
            # Set the session entry in redis
            error_code = None
            try:
                r.set(key,data)
            except (RedisError, OSError) as e:
                error_code = REDIS_EXCEPTION_ERROR_CODE
                print(error_code)
            #return updated item                
            if error_code:
                response['body'] = {"error_code":error_code} | queryStringParameters
            else:
                response['body'] = queryStringParameters
            return response
        elif  str(operation) == 'POST': #update
            print(" Add objects to item")
            
            sessionId = event.get("sessionId", None)
            if not sessionId:
                print("no session info provided")
                data["success"] = False
                data["message"] = "no session provided"
                response['body'] = data
                return  response
            print(sessionId)
           
            key = 'PHPREDIS_SESSION:' + str(sessionId)
            print('UPDATE redis key: ' + key)
            
            # connect to redis
            r = redis.Redis(
                host=host_string,
                port=6379
            )
            print("*********UPDATE*******")
            
            # get the current item
            try:
                value = r.get(key)
            except (RedisError, OSError) as e:
                error_code = REDIS_EXCEPTION_ERROR_CODE
                print(error_code)
                value = None
            if(value):
                # Unserialize data stored in redis
                loaddata = loads(value, object_hook=phpobject,decode_strings=True)
            else:
                loaddata = {}


            UpdateParameters = loaddata
            # update item
            UpdateParameters.update(queryStringParameters)
            # save object
            data = dumps(UpdateParameters, object_hook=phpobject)                
            error_code = None
            try:
                r.set(key,data)
            except (RedisError, OSError) as e:
                error_code = REDIS_EXCEPTION_ERROR_CODE
                print(error_code)
            if error_code:
                response['body'] = {"error_code":error_code} | queryStringParameters
            else:
                #return updated item
                response['body'] = UpdateParameters
            return response

        elif  str(operation) == 'DELETE':
            print(" Delete item")
            sessionId = queryStringParameters.get("sessionId", None)
            if not sessionId:
                print("no session info provided")
                data["success"] = False
                data["message"] = "no session provided"
                response['body'] = data
                return  response
            print(sessionId)
           
            key = 'PHPREDIS_SESSION:' + str(sessionId)
            print('DELETE redis key: ' + key)
            
            # connect to redis
            r = redis.Redis(
                host=host_string,
                port=6379
            )
            print("*********DELETE*******")
            # Set the session entry in redis
            error_code = None
            try:
                r.delete(key)
            except (RedisError, OSError) as e:
                error_code = REDIS_EXCEPTION_ERROR_CODE
                print(error_code)

            if error_code:
                response['body'] = {"error_code":error_code}
                data["success"] = False
                data["message"] = "Error_code: "+str(error_code)
            else:
                data["success"] = True
                data["message"] = "Sessiond deleted"                

            #return updated item
            response['body'] = data
            return response

    else:
        #event['key1']
        data["msg"] = "no acction selected"

    response['body'] = json.dumps(data)
    return  response
    #raise Exception('Something went wrong')