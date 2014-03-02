# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 14:55:00 2014

@author: Magdalena Furman s110848
"""

import pandas
from datetime import datetime
from datetime import timedelta
import csv
from matplotlib import pyplot as plt
from matplotlib.dates import date2num
from matplotlib.dates import DateFormatter
import numpy
import pylab as pl

DATE_FMT = "%d-%m-%y"
YLIM = [0, 1.1]

#def printoutSingleVal(name, value):
#    for row in data[name]:
#        print row
#    
#def printoutSingleSum(name, value):
#    return sum(data[name]==value)
#    
#def printoutSingleReport(name, value):
#    return sum(data[name]==value)
#    
#def printoutReport(val):
#    print "uuid" + " - " + str(printoutSingleSum("uuid", val))
#    print "name" + " - " + str(printoutSingleSum("name", str(val)))
#    print "timestamp" + " - " + str(printoutSingleSum("timestamp", val))
#    print "bt_mac" + " - " + str(printoutSingleSum("bt_mac", str(val)))
#    print "class" + " - " + str(printoutSingleSum("class", val))
#    print "user" + " - " + str(printoutSingleSum("user", val))
#    print "rssi" + " - " + str(printoutSingleSum("rssi", val))
#    print "sensible_token" + " - " + str(printoutSingleSum("sensible_token", val))
#    print "device_id" + " - " + str(printoutSingleSum("device_id", val))
    
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
    
def getQualityHour(user_id, time):
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
        grade = float((k + 1) / 12.0)
        if grade > 1.0:
            grade = 1.0
           
        tempDate = datetime(first_hour_dt.year, first_hour_dt.month, first_hour_dt.day, first_hour_dt.hour)
        counting_list.append((tempDate, grade))
        m = m + 1
    return counting_list

def getQualityDay(user_id, time):
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
            
        tempDate = datetime(first_hour_dt.year, first_hour_dt.month, first_hour_dt.day, 0)
        
        grade = (k + 1) / 288.0
        if grade > 1.0:
            grade = 1.0
        counting_list.append((tempDate, grade))
        m = m + 1
    return counting_list  
   
def commonPlotting(user_data, user_id, prefix, xlim=None):
    x = [date2num(date) for (date, value) in user_data]
    y = [value for (date, value) in user_data]
    colors = getBarColour(user_data)
    pl.figure()
    pl.subplot(111)
    pl.bar(x,y,color=colors)
    pl.title('Quality of all data, ' + user_id)
    pl.xticks(rotation=30)
    ax = pl.gca()
    ax.xaxis.set_major_formatter(DateFormatter(DATE_FMT))
    pl.xlim(xlim)
    pl.ylim([0, 1.1])
    plt.show()
    plt.savefig('pictures/' + prefix + user_id + '.png', bbox_inches='tight')
    plt.close()
    
def getBarColour(data):
    colors = []
    for value in data:
        if value[1] >= 1.0:
            colors.append('g')
        else:
            colors.append('r')
    return colors
    
def plotAllData(user_data, user_id):
    commonPlotting(user_data, user_id, 'all_')
    
def plotMonthData(user_data, user_id):
    [user_data, xlim] = getMonthData(user_data)
    commonPlotting(user_data, user_id, 'month_', xlim)
    
def plotWeekData(user_data, user_id):
    [user_data, xlim] = getWeekData(user_data)
    commonPlotting(user_data, user_id, 'week_', xlim)
    
def plotRandomDays(user_data, user_id):
    r = randint(0, len(getDaysList(user_data)))
    idx = []
    idx.append(r)
    idx.append(r * 3 % len(user_data))
    idx.append(r * 6 % len(user_data))
    
    for i in xrange(0, 3):
        [user_data1, xlim] = getDayData(user_data, idx[i])
        x = [date2num(date) for (date, value) in user_data1]
        y = [value for (date, value) in user_data1]
        
        colors = getBarColour(user_data1)
        pl.figure()
        pl.subplot(111)
        pl.bar(x,y,width=0.035, color=colors)
        pl.xlim(xlim)
        pl.title('Quality of data per hour, ' + user_id + " " + user_data1[0][0].strftime(DATE_FMT))
        pl.xticks(rotation=30)
        pl.ylim([0, 1.1])
        ax = pl.gca()
        ax.xaxis.set_major_formatter(DateFormatter("%H:%M")) 
        plt.show()
        plt.savefig('pictures/' + 'day_' + user_id + '_' + str(i) + '.png', bbox_inches='tight')
        plt.close()
    
def getDaysList(user_data):
    day_list = []
    temp_scan = user_data[0]
    for scan in user_data:
        if( not scan[0].year == temp_scan[0].year or scan[0].month == temp_scan[0].month or scan[0].day == temp_scan[0].day):
            day_list.append(scan)
            temp_scan = scan
    return day_list
        
def getDayData(user_data, idx):
    tempScan = user_data[idx]
    scan_list = []
    for scan in user_data:
        if scan[0].year == tempScan[0].year and scan[0].month == tempScan[0].month and scan[0].day == tempScan[0].day:           
            scan_list.append(scan)
            
    begin_date = datetime(tempScan[0].year, tempScan[0].month, tempScan[0].day, 0)
    end_date = datetime(tempScan[0].year, tempScan[0].month, tempScan[0].day, 0) + timedelta(days = 1)
    return [scan_list, [begin_date, end_date]]
    
def getWeekData(data):
    end_date = data[-1][0]
    begin_date = end_date - timedelta(days = 7)
    res = []
    for (key, val) in data:
        if key <= end_date and key > begin_date:
            res.append((key, val))
    return [res, [begin_date + timedelta(days = 1), end_date + timedelta(days = 1)]]
          
def getMonthData(data):
    end_date = data[-1][0] - timedelta(days = 7)
    begin_date = end_date - timedelta(days = 30)
    res = []
    for (key, val) in data:
        if key <= end_date and key > begin_date:
            res.append((key, val))
    return [res, [begin_date + timedelta(days = 1), end_date + timedelta(days = 1)]]
    
def calcStats(user_data):
    stats = []
    all_data = [data[1] for data in user_data]
    week_data = [data[1] for data in getWeekData(user_data)[0]] 
    month_data = [data[1] for data in getMonthData(user_data)[0]] 
    delta = user_data[-1][0] - user_data[0][0]
    stats.append(sum(all_data) / delta.days)
    stats.append(sum(month_data) / 30.0)
    stats.append(sum(week_data) / 7.0)
    return stats
    
USER_ID = "a6ad00ac113a19d953efb91820d878"
#DELTA = 300 # 5 mins
#single_user = getUserData(USER_ID)

users_list = getUsersList()

deltaDF = pandas.DataFrame()

i = 0
stats = []

for single_user in users_list:
    i = i + 1
    user_name = "user" + str(i)

#single_user = USER_ID
#    hours_data = getHourData(single_user)
#    with open(user_name + "_hour_data.csv", 'wb') as f:
#        writer = csv.writer(f)
#        writer.writerows(hours_data)
    qualityHour = getQualityHour(single_user, 1)
#    with open(user_name + "_qualityHour.csv", 'wb') as f:
#        writer = csv.writer(f)
#        writer.writerows(qualityHour)    
    
    qualityDay = getQualityDay(single_user, 1)
    
    #with open(single_user + "_qualityDay.csv", 'wb') as f:
    #    writer = csv.writer(f)
    #    writer.writerows(qualityDay)
    
    plotAllData(qualityDay, user_name)
    plotMonthData(qualityDay, user_name)
    plotWeekData(qualityDay, user_name)
#    
    plotRandomDays(qualityHour, user_name)
    stats.append([user_name, calcStats(qualityDay)])
    
#   single_user_data = getUserData(single_user)
#   single_user_timestamp = getTimestamp(single_user_data) 
#   delta_list = [single_user_timestamp[i] - single_user_timestamp[i + 1] for i in xrange(0, len(single_user_timestamp) - 1 )]
#   delta_list2 = [(single_user_timestamp[i], single_user_timestamp[i] - single_user_timestamp[i + 1]) for i in xrange(0, len(single_user_timestamp) - 1 )]
#   #deltaDF = pandas.DataFrame({single_user: delta_list})
#   #deltaDF.to_csv(single_user + ".csv")
#   with open(single_user + ".csv", 'wb') as f:
#       writer = csv.writer(f)
#       writer.writerows(delta_list2)  

with open("stats.csv", 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(stats)
    
    
    
    
    