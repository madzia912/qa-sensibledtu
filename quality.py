# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 14:55:00 2014

@author: Magdalena Furman s110848
"""

import pandas
from datetime import datetime
from datetime import timedelta
from matplotlib import pyplot as plt
from matplotlib.dates import date2num
import numpy
import pylab as pl
import collections
import csv

def printoutSingleVal(name, value):
    for row in data[name]:
        print row
    
def printoutSingleSum(name, value):
    return sum(data[name]==value)
    
def printoutSingleReport(name, value):
    return sum(data[name]==value)
    
def printoutReport(val):
    print "uuid" + " - " + str(printoutSingleSum("uuid", val))
    print "name" + " - " + str(printoutSingleSum("name", str(val)))
    print "timestamp" + " - " + str(printoutSingleSum("timestamp", val))
    print "bt_mac" + " - " + str(printoutSingleSum("bt_mac", str(val)))
    print "class" + " - " + str(printoutSingleSum("class", val))
    print "user" + " - " + str(printoutSingleSum("user", val))
    print "rssi" + " - " + str(printoutSingleSum("rssi", val))
    print "sensible_token" + " - " + str(printoutSingleSum("sensible_token", val))
    print "device_id" + " - " + str(printoutSingleSum("device_id", val))
    
def getUserData(user_id):
    return data[data["user"] == user_id]
    
data = pandas.read_csv('Dump3_Good.csv',delimiter=';');

def getUsersList():
    user_list = [i for i in data["user"]]
    return list(set(user_list))
    
def getTimestamp(single_user_data):
    timestamp_list = [i for i in single_user_data["timestamp"]]
    timestamp_list = list(set(timestamp_list))
    timestamp_list.sort()
    return timestamp_list
    
def getHourData(user_id):
    single_user_data = getUserData(user_id)
    single_user_timestamp = getTimestamp(single_user_data)    
    tab = []
    for i in single_user_timestamp:
        tab.append((datetime.fromtimestamp(i), " "))
    return tab
    

    
def getQualityHour2(user_id):
    single_user_data = getUserData(user_id)
    single_user_timestamp = getTimestamp(single_user_data)
    first_hour = single_user_timestamp[0]
    
    first_hour_dt = datetime.fromtimestamp(first_hour)
   
    counting_list = []
    j = 1
    m = 0
    while j < len(single_user_timestamp):
        k = 0
        first_hour_dt = datetime.fromtimestamp(single_user_timestamp[j])
        for i in xrange(j, len(single_user_timestamp)):
            temp_timestamp = datetime.fromtimestamp(single_user_timestamp[i])
            j = j + 1            
            if(first_hour_dt.day == temp_timestamp.day and 
                first_hour_dt.month == temp_timestamp.month and
                first_hour_dt.year == temp_timestamp.year and
                first_hour_dt.hour == temp_timestamp.hour):
                    k = k + 1
            else:
                break
        tempdate = datetime(first_hour_dt.year, first_hour_dt.month, first_hour_dt.day, first_hour_dt.hour, 0, 0)
                
        counting_list.append((tempdate, float((k + 1) / 12.0)))
        m = m + 1
    return counting_list

def getQualityDay(user_id):
    single_user_data = getUserData(user_id)
    single_user_timestamp = getTimestamp(single_user_data)
    first_hour = single_user_timestamp[0]
    first_hour_dt = datetime.fromtimestamp(first_hour)
    last_hour = single_user_timestamp[-1]
    last_hour_dt = datetime.fromtimestamp(last_hour)
    
    i = 0
    resDict = {}
    while first_hour_dt < last_hour_dt and i < len(single_user_timestamp): 
        temp_timestamp = datetime.fromtimestamp(single_user_timestamp[i])
        if temp_timestamp >= first_hour_dt and temp_timestamp < first_hour_dt + timedelta(minutes = 5):
            if resDict.has_key(first_hour_dt):
                resDict[first_hour_dt] = resDict[first_hour_dt] + 1
                i = i + 1
            else:
                resDict[first_hour_dt] = 1
                i = i + 1
        elif temp_timestamp < first_hour_dt:
            i = i + 1
        elif temp_timestamp >= first_hour_dt + timedelta(minutes = 5):
            first_hour_dt = first_hour_dt + timedelta(minutes = 5) 
            if not resDict.has_key(first_hour_dt):
                resDict[first_hour_dt] = 0
        else:
            i = i + 1
            first_hour_dt = first_hour_dt + timedelta(minutes = 5)
        #tempdate = datetime(first_hour_dt.year, first_hour_dt.month, first_hour_dt.day, first_hour_dt.hour, 0, 0)
        #counting_list.append((tempdate, float((k + 1) / 12.0)))                
    return collections.OrderedDict(sorted(resDict.items()))
    
def getQualityDay1(user_id):
    single_user_data = getUserData(user_id)
    single_user_timestamp = getTimestamp(single_user_data)
    first_hour = single_user_timestamp[0]
    
    first_hour_dt = datetime.fromtimestamp(first_hour)
   
    counting_list = []
    j = 0
    m = 0
    while j < len(single_user_timestamp):
        k = 0
        first_hour_dt = datetime.fromtimestamp(single_user_timestamp[j])
        for i in xrange(j, len(single_user_timestamp)):
            temp_timestamp = datetime.fromtimestamp(single_user_timestamp[i])
            j = j + 1            
            if(first_hour_dt.day == temp_timestamp.day and 
                first_hour_dt.month == temp_timestamp.month and
                first_hour_dt.year == temp_timestamp.year):
                    k = k + 1
            else:
                break
            
        tempdate = datetime(first_hour_dt.year, first_hour_dt.month, first_hour_dt.day, 12, 0, 0)
        value = (k + 1) / 288.0
        #print "K" + str(k) + "val" + str(value)
        counting_list.append((tempdate, value))
        m = m + 1
    return counting_list  
   
def plotAllData(user_data, user_id):
    x = [date2num(date) for date in user_data.keys()]
    y = [value for value in user_data.values()]
    yy = numpy.zeros(len(user_data))
    
    pl.figure()
    pl.subplot(111)
    pl.plot_date(x,y,'r')
    pl.title('Quality of all data, ' + user_id)
    pl.xticks(rotation=30)
    pl.plot(x, yy, 'g')
    plt.show()
    plt.savefig('Diagrams/all_' + user_id + '.png', bbox_inches='tight')
    plt.close()
    
def plotMonthData(user_data, user_id):
    #user_data = user_data[-37:-7] # take last 30 elements
    x = [date2num(date) for date in user_data.keys()]
    y = [value for value in user_data.values()]
    yy = numpy.ones(len(user_data))
    
    pl.figure()
    pl.subplot(111)
    pl.plot_date(x,y,'r-o')
    pl.title('Quality of data last month, ' + user_id)
    pl.xticks(rotation=30)
    pl.plot(x, yy, 'g')
    plt.show()
    plt.savefig('Diagrams/month_' + user_id + '.png', bbox_inches='tight')
    plt.close()
    
def plotWeekData(user_data, user_id):
    #user_data = user_data[-7:] # take last 7 elements
    x = [date2num(date) for (date, value) in user_data]
    y = [value for (date, value) in user_data]
    yy = numpy.ones(len(user_data))
    
    pl.figure()
    pl.subplot(111)
    pl.plot_date(x,y,'r-o')
    pl.title('Quality of data last week, ' + user_id)
    pl.xticks(rotation=30)
    pl.plot(x, yy, 'g')
    plt.show()
    plt.savefig('Diagrams/week_' + user_id + '.png', bbox_inches='tight') 
    plt.close()
    
def getWeekData(data):
    end_date = data[-1][0]
    begin_date = end_date - timedelta(days = 7)
#    print end_date
#    print begin_date
    res = []
    for (key, val) in data:
        if key <= end_date and key > begin_date:
            res.append((key, val))
    return res
          
def getMonthData(data):
    end_date = data[-1][0] - timedelta(days = 7)
    begin_date = end_date - timedelta(days = 37)
#    print end_date
#    print begin_date
    res = []
    for (key, val) in data:
        if key <= end_date and key > begin_date:
            res.append((key, val))
    return res
    
USER_ID = "a6ad00ac113a19d953efb91820d878"
#DELTA = 300 # 5 mins
#single_user = getUserData(USER_ID)

users_list = getUsersList()

deltaDF = pandas.DataFrame()

i = 0
for single_user in users_list:
    i = i + 1
    user_name = "user" + str(i)
    
    #single_user = USER_ID
#    hours_data = getHourData(single_user)
#    with open("Quality/" + user_name + "_hour_data.csv", 'wb') as f:
#        writer = csv.writer(f)
#        writer.writerows(hours_data)
#        
#    qualityHour = getQualityHour(single_user)
#    with open("Quality/" + user_name + "_qualityHour.csv", 'wb') as f:
#        writer = csv.writer(f)
#        writer.writerows(qualityHour)    
    
    qualityDay = getQualityDay(single_user)
    #print qualityDay[:100]
    with open("Quality1/" + user_name + "_qualityDay.csv", 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(qualityDay.items())
    
    #monthData = getMonthData(qualityDay)
    #weekData = getWeekData(qualityDay)
    
    plotAllData(qualityDay, user_name)
    #plotMonthData(monthData, user_name)
    #plotWeekData(weekData, user_name)
    
#   single_user_data = getUserData(single_user)
#   single_user_timestamp = getTimestamp(single_user_data) 
#   delta_list = [single_user_timestamp[i] - single_user_timestamp[i + 1] for i in xrange(0, len(single_user_timestamp) - 1 )]
#   delta_list2 = [(single_user_timestamp[i], single_user_timestamp[i] - single_user_timestamp[i + 1]) for i in xrange(0, len(single_user_timestamp) - 1 )]
#   #deltaDF = pandas.DataFrame({single_user: delta_list})
#   #deltaDF.to_csv(single_user + ".csv")
#   with open(single_user + ".csv", 'wb') as f:
#       writer = csv.writer(f)
#       writer.writerows(delta_list2)
   
    
    
    
    
    
    
    
    