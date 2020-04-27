import json
import boto3
from flask_lambda import FlaskLambda
from flask import jsonify
from flask import request
from flask import Response
from boto3.dynamodb.conditions import Key
# import requests

app = FlaskLambda(__name__)
ddb = boto3.resource("dynamodb")
table = ddb.Table('restaurants')
logintable = ddb.Table('logintable')

@app.route('/')
def index():

    data = {
        "message": "Welcome to Restaurant Automation"
    }
    return json.dumps(data)


@app.route('/restaurants', methods=['GET','POST'])
def put_or_list_restuarants():
    if(request.method == 'GET'):
        res = table.scan()['Items']
        return(
            json.dumps(res),
            200,
            {'Content-Type': "application/json"}
        )
    else:
        table.put_item(Item=request.json)
        return(
            json.dumps({"message": "entry made"}),
            200,
            {'Content-Type': "application/json"}
        )



@app.route('/restaurants/seating/<string:resid>', methods=['GET'])
def getseatingchart(resid):
    response = table.query(IndexName="seatingGSI",KeyConditionExpression=Key("Resid").eq(resid))
    if(response['Items'][0]["Seating"]==[]):
        return(json.dumps("Seating Chart not updated"),200,{'Content-Type': "application/json"})
    else:
        return(jsonify(response['Items'][0]['Seating']),200, {'Content-Type': "application/json"})



@app.route('/restaurants/menu/<string:resid>', methods=['GET','POST'])
def menu(resid):
    if(request.method == 'GET'):
        res = table.scan()['Items']
        for restaurants in res:
            if(restaurants['Resid']==resid):
                menu=restaurants['Menu']
                return(
                    json.dumps(menu),
                    200,
                    {'Content-Type': "application/json"}
                )
            else:
                return(json.dumps("Restaurant doesnt exist"),200,{'Content-Type': "application/json"})

# {"Resname":"Pizza hut","Resaddr":"Banashkari,98/4","Resnum":"23316745","Resid":"1","Username":"PizHut","Password":"1234"}
@app.route('/restaurants/signup', methods=['POST'])
def signup():
    req=request.get_json()
    uname=req["Username"]
    pwd=req["Password"]
    resid=req["Resid"]

    name=req["Resname"]
    num=req["Resnum"]
    addr=req["Resaddr"]
    
    req1=jsonify({"Resid":resid,"Username":uname,"Password":pwd})
    req2=jsonify({"Resid":resid,"Menu":[],"Offers":[],"Seating":[],"Resname":name,"Resnum":num,"Resaddr":addr})

    logintable.put_item(Item={"Resid":resid,"Username":uname,"Password":pwd})
    table.put_item(Item={"Resid":resid,"Menu":[],"Offers":[],"Seating":[],"Resname":name,"Resnum":num,"Resaddr":addr})
    return(
        json.dumps({"message": "entry made"}),
        200,
        {'Content-Type': "application/json"}
    )
    
#{"Resid":"1","Username":"PizHut","Password":"1234"}
@app.route('/restaurants/login', methods=['POST'])
def login():
    req=request.get_json()
    resid=req["Resid"]
    uname=req["Username"]
    pwd=req["Password"]
    
    res = logintable.scan()['Items']
    for restaurants in res:
        if(restaurants['Username']==uname):
            chk=1
            if restaurants['Password']==pwd:
                return(
                    json.dumps({"message": "login successful"}),
                    200,
                    {'Content-Type': "application/json"}
                )        
    return(
        json.dumps({"message": "Invalid credentials!"}),
        200,
        {'Content-Type': "application/json"}
    )
