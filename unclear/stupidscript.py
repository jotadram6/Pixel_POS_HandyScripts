import sys
printstring = []
listtomask = sys.argv[1].split(',')
print listtomask
for i in range(80):
    for j in listtomask:
       if i is int(j):
          printstring.append('0')
       else:
          printstring.append('1')
print  ''.join(printstring)
