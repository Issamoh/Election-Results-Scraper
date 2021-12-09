#The following library is made to make HTTP requests just as the browser can do
import requests

#pandas is a powerful library built in top of python for data science purposes, we use it to convert json into a csv file
import pandas as pd

#used to convert into epoch
from datetime import datetime
import time

def scrapeTheSite():

    #The following code simulates the request that the website does in order to get the data
    #url = "http://electionmaps.acgov.org/json/electionResults.json?_=1635065022771"
    url = "http://electionmaps.acgov.org/json/pastelections/2021-09-14-GubernatorialRecall.json?_=1639006954518"

    payload={}
    headers = {
      'Connection': 'keep-alive',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache',
      'Accept': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
      'X-Requested-With': 'XMLHttpRequest',
      'Referer': 'http://electionmaps.acgov.org/',
      'Accept-Language': 'en-GB,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,ar-DZ;q=0.6,ar;q=0.5,en-US;q=0.4'
    }

    #After the request is sent the object response will contain all the information (status code, the data...etc)
    response = requests.request("GET", url, headers=headers, data=payload)

    #response.json() method has a builtin JSON decoder that converts the data contained in the response into a json object
    data = response.json()

    #Now we can access to the fields of our json object
    if(data):

        #result is the variable that will contain our result
        result = []

        #the last update time is the same for all the records, we can get it like so :
        lastUpdate = data['lastUpdatedDateTime']
        lastUpdateString = lastUpdate

        #Converting date into epoch
        parts = lastUpdate.partition(" ")
        month = parts[0]
        datetime_object = datetime.strptime(month, "%B")
        month_number = datetime_object.month
        newDate = str(month_number)+" "+parts[2]

        pattern = '%m %d, %Y, %H:%MAM'
        epoch = int(time.mktime(time.strptime(newDate, pattern)))
        lastUpdate = epoch

        #races field contains the statistics that we want (precinct ID, Yes and No counter)
        races = data['races']['1']['precincts']

        #Now we loop over the races table to organize our result
        for precinct in races:
            #item represents one line in our wanted result
            item={}
            item['precinctID'] = precinct
            item['yes'] = races[precinct]['candidates']['47']['votes']
            item['no'] = races[precinct]['candidates']['48']['votes']
            item['total'] = item['yes'] + item['no']
            if (item['total']!=0):
                item['yesPercentage'] = format(item['yes'] * 100 / item['total'], ".1f")
                item['noPercentage'] = format(item['no'] * 100 / item['total'], ".1f")
            else:
                item['yesPercentage'] =0
                item['noPercentage']= 0
            item['lastUpdateEpoch'] = lastUpdate
            item['lastUpdate'] = lastUpdateString

                #we add the new item to our result list
            result.append(item)

        # Now we sort the list based on the precinct ID
        result = sorted(result, key=lambda i: i['precinctID'])

        #For the second file that contains each precinct and its neighbours:
        precinctsNeighbours = []

        precincts = data['registrationAndTurnout']
        for key in precincts:
            precinct={}
            precinct['precinctID'] = key
           # precinct['includedPrecincts'] = precincts[key]['homePrecincts']
            includedPrecincts = precincts[key]['homePrecincts']

            i = 1
            for neighbour in includedPrecincts:
                precinct['precinct'+str(i)] = neighbour
                i = i+1
            precinctsNeighbours.append(precinct)

        #Now we sort the list based on the precinct ID
        precinctsNeighbours = sorted(precinctsNeighbours, key=lambda i: i['precinctID'])

        return (result,precinctsNeighbours)

#the following function uses pandas library to convert json data into a csv file
def export_as_csv(data,fileName):
    if(data):
        dataFrame = pd.json_normalize(data)
        dataFrame.to_csv(fileName)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Scraping is in progress ...")
    (stats,consolidated) = scrapeTheSite()
    export_as_csv(stats,"statistics.csv")
    export_as_csv(consolidated,"consolidated.csv")
    print("Done")


