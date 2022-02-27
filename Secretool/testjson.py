#!/usr/bin/python
import json

data = [ { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 } ]

data2 = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
with open('txt.json', 'w') as f:
    f.write(data2)
print(data2)