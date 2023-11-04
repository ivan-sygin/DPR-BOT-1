import json





def encode(name,data:dict):
    return str(name)+"|"+str(data)

def decode(string:str):
    string = string.replace("'", '"')

    return json.loads(string.split("|")[1])