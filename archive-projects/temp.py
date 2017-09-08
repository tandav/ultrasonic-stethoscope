data = range(10)


f = open('data.txt','w')

for item in data:
  f.write("%s " % item)

f.write("\n")

data = range(10, 20)
for item in data:
  f.write("%s " % item)
# f.write(data) # python will convert \n to os.linesep
f.close() # close the file
