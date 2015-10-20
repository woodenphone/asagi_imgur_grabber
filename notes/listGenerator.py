'''
Created on 09.04.2015

@author: DER RUETTLER
'''
import copy
from datetime import datetime
from os.path import os
import re
import sys

from bs4 import BeautifulSoup
from pip._vendor.distlib.compat import raw_input
import requests



'''
First we need the current year and month so the script knows when to stop
'''
currentYear=datetime.now().year
currentMonth=datetime.now().month

'''
Next we need four variables to generate a Timeframe from which to extract pastebin links.
The Timeframe is formatted like this: From 01-month-year to 01-month2-year2 (day-month-year)
This Timeframe will be changed (by one month) and reused until the present is reached.
The variables will be determined by the following input:
'''

print('[u]pdate the list (last two months), extract [a]ll links, exract from a [s]pecific month or [p]rocess unprocessed links?')
mode=raw_input('>>')

'''
[a]ll links:
This mode will scan the entirety of https://archive.moe/mlp/ for pastebin links.
'''

if mode=='a':
    year=2012
    month=2
    year2=2012
    month2=3
    
    '''
    [u]pdate:
    This mode will scan just the last two months for links.
    '''    
    
elif mode=='u':
    if currentMonth>1:
        year=currentYear
        month=currentMonth-1
    else:
        year=currentYear-1
        month=12
    year2=currentYear
    month2=currentMonth    
    
    '''
    [s]pecific month:
    This mode will ask the user to specify a year and a month and then extract links from that month.
    To make this work we also have to lower the treshold of when the program is supposed to stop.
    '''
elif mode=='s':
    year=int(raw_input('Year:'))
    month=int(raw_input('Month:'))
    if month==12:
        year2=year+1
        month2=1
    else:
        month2=month+1
        year2=year
    currentYear=year
    currentMonth=month
    
    '''
    Next we initialize some variables that we'll need later.
    This is my first Python project, so my code is a little inconsistent in terms of structure.
    I'll only explain the important stuff.
    pasteListSet: Set of non-user pastebin links
    newPastes: Set of new links that have been found while running this script.
    pasteSet: Set that contains all links ever found with this script.
    writefagSet: Set that contains all user pastebin links
    processedPastes: List that contains data to be used algorithmically by other programs.
    wfSortList: List that contains triples of writefag, story title and link processed.
    
    The last two are lists instead of sets, because I'm being inconsistent.
    Sets are generally the better choice because they rule out duplicates.
    
    errorID: Integer to be used later in case some special snowflake put in chinese characters or something in the paste title.
             Unfortunately I forgot to save this variable after exiting the program, so all erroneous pastes are named "UnicodeEncodeError0".
             Oops.
             
    pastebinRequests: Integer that counts the requests sent to Pastebin.com.
                      Useful for estimating how long it will take until your IP gets temporarily blocked due to "unnatural browsing behaviour".
                      
    pasteCount: Integer that counts the amount of links scanned.
                Probably obsolete and isn't even used in every case, but I'm too lazy to go over the script again and change it.
    
    '''
    
pastebinLink=str('--')
pasteListSet = set()
newPastes = set()
duplicates=0
pasteSet = set()
namedPasteList=[]
writefagSet = set()
processedPastes=[]
wfSortList=[]
errorID = 0;
pastebinRequests=0

pasteCount=0

'''
Ok, next we need to retrieve the current lists, or else you'd have to run the whole script every time you want to make an update.
'''


print('Retrieving already scanned pastebin links...')
if not os.path.exists('resources'):
    os.makedirs('resources')
try:    
    pasteSetInput=open('resources/pasteSet.txt',mode='r')
    
except Exception:
    open('resources/pasteSet.txt',mode='w')
    pasteSetInput=open('resources/pasteSet.txt',mode='r')

inputLine = pasteSetInput.readline()

while inputLine:
    inputLine=inputLine[:-1]
    pasteSet.add(inputLine)
    if inputLine.startswith('http://pastebin.com/u/'):
        writefagSet.add(inputLine)
    else:
        pasteListSet.add(inputLine)
    inputLine=pasteSetInput.readline()
    pasteCount=pasteCount+1

   
try: 
    procInput=open('resources/processed.txt',mode='r')
except Exception:
    open('resources/processed.txt',mode='w')
    procInput=open('resources/processed.txt',mode='r')
procLine=procInput.readline()
while procLine:
    procLine=procLine[:-1]
    processedPastes.append(procLine)
    procLine=procInput.readline()


try: 
    namedInput=open('named pastes.txt',mode='r')
except Exception:
    open('named pastes.txt',mode='w')
    namedInput=open('named pastes.txt',mode='r')
namedLine=namedInput.readline()
while namedLine:
    namedLine=namedLine[:-1]
    namedPasteList.append(namedLine)
    namedLine=namedInput.readline()


try: 
    wfSortInput=open('pastebins sorted by writefag.txt',mode='r')
except Exception:
    open('pastebins sorted by writefag.txt',mode='w')
    wfSortInput=open('pastebins sorted by writefag.txt',mode='r')
wfSortLine=wfSortInput.readline()
while wfSortLine:
    wfSortLine=wfSortLine[:-1]
    wfSortList.append(wfSortLine)
    wfSortLine=wfSortInput.readline()

'''
If our goal is to [u]pdate, retrieve [a]ll links, or to scan a [s]pecific month, then the following part is executed.
The while loop is executed as long as the total amount of months since 0 A.D. is not larger than the treshold set earlier.
The maximum number of pages scanned for each month is 200, but it's usually around 75.

The first step in scanning a month worth of pages is to construct the URL (see below).
The URL is dependant on the variable i, that's representing the current page that's being scanned.
i is increased by 1 in every loop of that particular month, so all pages are being scanned.

Next we get the page's source code via Requests, and transform it into a tree of objects using Beautiful Soup.
We use BS's find method to look for any instances of "<h4 class="alert-heading">Error!</h4>".
The only case in which that object is displayed, is if archive.moe has run out of search results for the specified conditions (in this case posts containing "http:pastebin.com/" posted in a certain timeframe)
Therefore we break the for loop since we won't get any additional results from scanning more pages of this timeframe.

Now that we've assured that there are actual results on the page, we use BS to get all links leading to "http://pastebin.com" 
If the links found are not included in the Set of links that were already found at some point, they are added to the Set of already found links as well as to the Set of new links

Afterwards, we're done with that particular month, so we increase month, year, month2 and year2 by 1.
'''


if mode=='u' or mode=='a' or mode=='s':
    print(pasteCount,' links found.')
    print('Extraction started')
#This loop is executed as long as month and year are below a certain treshold
    while year*12+month <= currentYear*12+currentMonth:
        print()
        print('Timeframe: ',month,year,' - ',month2,year2)
        #200=maximum number of pages returned by archive.moe
        for i in range(200):
            print('Extracting from page '+str(i+1))
            #constructing the URL:
            url = "https://archive.moe/mlp/search/text/http%3A%2F%2Fpastebin.com%2F/start/"+str(year)+"-"+str(month)+"-1/end/"+str(year2)+"-"+str(month2)+"-1/page/"+str(i+1)+"/#"
            #getting the source code:
            r=requests.get(url)
            data=r.text
            #transforming the source code into a tree of objects:
            soup = BeautifulSoup(data)
            
            #check whether archive.moe still returns results:
            abort = str(soup.find('h4'))
            if abort=='<h4 class="alert-heading">Error!</h4>':
                break
            
            #find pastebin links and add them to their respective sets:
            for link in soup.find_all(href=re.compile('http://pastebin.com')):
                pastebinLink = link.get('href')
                if not pastebinLink in pasteSet:
                    newPastes.add(pastebinLink)
                    pasteSet.add(pastebinLink)
        month=month+1
        month2=month2+1
        if month==13:
            month=1
            year=year+1
        if month2==13:
            month2=1
            year2=year2+1
    
    print('Extraction finished')
    print('Found',len(pasteSet)-duplicates,'unique links in total,',len(newPastes),'of which are new.')

    '''
    Alternatively, if you already have a list of unprocessed links, you can skip right to processing.
    The next few lines of code aren't particularly interesting; as before it's simple retrieving of strings from a text file. 
    '''
    
elif mode=='p':
    
    try:    
        unprocessed=open('resources/unprocessed.txt',mode='r')
    
    except Exception:
        open('resources/unprocessed.txt',mode='w')
        unprocessed=open('resources/unprocessed.txt',mode='r')
    upLine = unprocessed.readline()
    while upLine:
        newPastes.add(upLine[:-1])
        upLine=unprocessed.readline()
    setCopy=copy.copy(newPastes)
print('Found',len(newPastes),'unprocessed links.')


print()
'''
Processing:
During this part of the script we gather the paste's relevant metadata (author and title) from pastebin.com.
Processing is only executed if there are any new pastes to begin with, and even then the user is questioned whether he wants to process the links he found.
If the answer to that question is not [n]o, the processing loop is initiated.
The first thing we do is set the default author to "Anonymous". This is only changed if we later find another author, so all pastes submitted by a guest are
attributed to Anonymous. We also set option='n' (the n standing for normal), which will later become relevant for handling pastebin.com's ip block.

The first step of processing is to check whether the link we got is a user link. If that's the case we don't have to send any requests to pastebin.com,
and can just add that link to the writefag list. If the link is a non-user link we instead add it to the non-user paste set and gather it's metadata.
We set problems=False by default, indicating that the current loop went without any problems so far. Next we get the BS object tree as we did with archive.moe.
The first thing we need is the title. If it equals "<title>Pastebin.com - Access Denied Warning</title>", pastebin has detected the script and the ip has been 
blocked temporarily. To handle this, user action is required. The user can either [r]etry, which will work if either the ip address is reset, 
or if he waits for an hour or so. Another option would be to break the loop and [s]ave the current process or to just [a]bort. Getting an ip block will set problems to True.

If we encountered no problems so far with accessing the paste, we can now check whether the link actually leads to a paste. If it does, we continue.
First thing we do is cut "<title>" and " - Pastebin.com</title>" from the title. Then we try to print the title in the console, and if an exception occurs,
that's usually because there's some weird character in the title. In that case we simply rename it to UnicodeEncodeError.

As soon as we have the title, we add an entry to namedPasteList.
Next we get the first link starting with "/u/", since that link will always lead to the author's pastebin. With that we can generate all the other listes.

Finally, before ending the loop we check the value of option. If it equals 'n', we get another entry from pasteSet and reiterate the loop.
If option='a', the program simply exits. If option='s', the loop is broken and we go on to saving.
Any other value for option (like [r]etry) is causing a repeat of the loop with the same input.
'''
if len(newPastes):
    print('Continue with processing?(y,n)')
    proc=raw_input('>>')
    url2='url2'
    if proc=='n':
        contWithProc=False
    else:
        print('Processing started')
        contWithProc=True
        url2=newPastes.pop()
        url2=str(url2)
    while url2 and contWithProc:
        
        writefag='Anonymous'
        option='n'
        if url2.startswith('http://pastebin.com/u/'):
            writefagSet.add(url2)
            print('Writefag found:',url2[22:])
        else:
            pasteListSet.add(url2)
            problems=False
            print(url2)
            try:
                r2=requests.get(url2)
            except Exception:
                print('Something went wrong while trying to get access to',url2)
            
            pastebinRequests=pastebinRequests+1
            print('Requests to pastebin.com:',pastebinRequests)
            data2=r2.text
            data2=str(data2)
            data2=data2.replace('\n', '')
            soup2=BeautifulSoup(data2)
            title=soup2.find('title')
            title=str(title)
            if title=='<title>Pastebin.com - Access Denied Warning</title>':
                problems=True
                print('The Access to Pastebin.com has been denied due to "unnatural browsing behaviour"')
                print('Reset your IP-Address to [r]etry or either [s]ave or [a]bort')
                option=raw_input('>>')
            if not problems:        
                if title=='<title>Pastebin.com Unknown Paste ID</title>':
                    print(url2,'has not been found.')
                else:
                    title=title[7:-23]
                    try:
                        print(title)
                    except :
                        print('Could not process',url2,'due to an UnicodeEncodeError.')
                        title='UnicodeEncodeError'+str(errorID)
                        
                    namedPasteList.append(title+' '+url2)
                    
                    
                    link2=soup2.find(href=re.compile('/u/'))
                    if link2:
                        writefag=link2.get('href')
                        wfLink ='http://pastebin.com'+writefag
                        writefagSet.add(wfLink)
                        writefag=writefag[3:]
                        print('Writefag:',writefag)
                    processedPastes.append(writefag+'>>><>>'+title+'>>><>>'+url2)
                    writefag=writefag+(25-len(writefag))*' '
                    if len(title)>70:
                        title=title[:70]
                    title=title+(80-len(title))*' '
                    wfSortList.append(writefag+title+url2)
            
        if option=='n':
            pasteSet.add(url2)    
            try:
                url2=newPastes.pop()
            except Exception:
                url2=str()
            print()
        elif option=='a':
            sys.exit('Program aborted');
        elif option=='s':
            newPastes.add(url2)
            break

    print('Processing finished.')

'''
Nothing too interesting happening here, just standard string storage.
'''

print(len(pasteSet),len(newPastes))
pasteSet=pasteSet-newPastes
pasteSetOutput = open('resources/pasteSet.txt',mode='w')
while pasteSet:
    pasteSetOutput.write(pasteSet.pop()+'\n')
unprocessedOutput=open('resources/unprocessed.txt',mode='w')
while newPastes:
    unprocessedOutput.write(newPastes.pop()+'\n')


processedPastes.sort()
processed=open('resources/processed.txt',mode='w')
for i in range(len(processedPastes)):
    processed.write(processedPastes[i]+'\n')

writefagList=list(writefagSet) 
writefagList.sort() 
writefagOutput=open('writefags.txt',mode='w')  
for i in range(len(writefagList)):
    writefagOutput.write(writefagList[i]+'\n')

pasteList=list(pasteListSet)
pasteList.sort()
pasteOutput=open('pastes.txt',mode='w')    
for i in range(len(pasteList)):
    pasteOutput.write(pasteList[i]+'\n')
    
namedPasteList.sort()
namedPasteOutput=open('named pastes.txt',mode='w')    
for i in range(len(namedPasteList)):
    namedPasteOutput.write(namedPasteList[i]+'\n')
    
wfSortList.sort()
wfSortOutput=open('pastebins sorted by writefag.txt',mode='w')
for i in range(len(wfSortList)):
    wfSortOutput.write(wfSortList[i]+'\n')
print('-End of Script-')