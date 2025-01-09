import json
file = 'data.json'
with open(file, 'r') as obj:
    data = json.load(obj)

print(data)
print(type(data))