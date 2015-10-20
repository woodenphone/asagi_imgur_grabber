npIn=open('named pastes.txt',mode='r')
npSet=set()
npLine=npIn.readline()
while npLine:
    npLine=npLine[0].capitalize()+npLine[1:]
    npSet.add(npLine)
    npLine=npIn.readline()

npList=list(npSet)
npList.sort()
npOut=open('named pastes.txt',mode='w')
for i in range(len(npList)):
    npOut.write(npList[i])
    

    
npIn=open('pastebins sorted by writefag.txt',mode='r')
npSet=set()
npLine=npIn.readline()
while npLine:
    npLine=npLine[0].capitalize()+npLine[1:]
    npSet.add(npLine)
    npLine=npIn.readline()

npList=list(npSet)
npList.sort()
npOut=open('pastebins sorted by writefag.txt',mode='w')
for i in range(len(npList)):
    npOut.write(npList[i])


    
npIn=open('writefags.txt',mode='r')
npSet=set()
npLine=npIn.readline()
while npLine:
    npLine=npLine[:22]+npLine[22].capitalize()+npLine[23:]
    npSet.add(npLine)
    npLine=npIn.readline()

npList=list(npSet)
npList.sort()
npOut=open('writefags.txt',mode='w')
for i in range(len(npList)):
    npOut.write(npList[i])