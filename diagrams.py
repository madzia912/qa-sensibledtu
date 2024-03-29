# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 14:55:00 2014

@author: Magdalena Furman s110848
"""

from datetime import datetime
from datetime import timedelta
from matplotlib import pyplot as plt
from matplotlib.dates import date2num
from matplotlib.dates import DateFormatter
import MySQLdb
from random import randrange

# Diagram layout settings
DAY_FMT = "%H:%M"
DATE_FMT = "%d-%m-%y"
YLIM = [0, 1.1]

# Quality settings
HOUR_EXP = 12.0
DAY_EXP = 288.0
MAX_GRADE = 1.0

# Db connection settings
USER = 'magda'
PWD = 'lokus1?'
HOST = 'localhost'

DB_CONN = {'edu_mit_media_funf_probe_builtin_BluetoothProbe' : 'bluetooth',
           'edu_mit_media_funf_probe_builtin_LocationProbe'  : 'location',
           'edu_mit_media_funf_probe_builtin_WifiProbe'      : 'wifi'}
           
TB_QUALITY_DAILY = 'data_quality_daily'
TB_QUALITY_HOURLY = 'data_quality_hourly'
TB_LAST_SCANS = 'user_last_scans'

DB_QUALITY = 'data_quality'

PICTURE_FOLDER = 'pic/'

def get_first_last_timestamp(db, user_id, column, table_name):
    cur = db.cursor()
    query = 'SELECT start_timestamp, %s FROM %s WHERE user = %%s ORDER BY start_timestamp DESC' % (column + '_quality', table_name)
    cur.execute(query, (user_id))
    fetched_data = cur.fetchall()
    cur.close()
    return (fetched_data[-1][0], fetched_data[0][0])
    
def get_users_list(db):
    cur = db.cursor()
    cur.execute('SELECT DISTINCT(user) FROM user_last_scans')
    result = cur.fetchall()
    cur.close()
    return result

def common_plotting(user_data, user_id, subfolder, prefix, date_fmt=None, wid=None, xlim=None):
    x_val = [date2num(row[0]) for row in user_data]
    y_val = [row[1] for row in user_data]
    colors = get_bar_colour(y_val)
    plt.figure()
    plt.subplot(111)

    plt.gca().xaxis.set_major_formatter(DateFormatter(date_fmt))
    #plt.gca().xaxis.set_major_locator(DayLocator())

    if wid != None:
        plt.bar(x_val, y_val, width = wid, color = colors)
    else:
        plt.bar(x_val, y_val, color = colors)
        
    plt.title('Quality of data for ' + user_id)
    plt.xticks(rotation = 30)
    
    #current_axis = pl.gca()
    #current_axis.xaxis.set_major_formatter(DateFormatter(DATE_FMT))
    
    plt.xlim(xlim)
    plt.gcf().autofmt_xdate()
    plt.show()
    plt.savefig(PICTURE_FOLDER + subfolder + '/' + prefix + user_id + '.png', bbox_inches = 'tight')
    plt.close()

def get_bar_colour(data):
    colors = []
    for value in data:
        if value >= 1.0:
            colors.append('g')
        else:
            colors.append('r')
    return colors

def plot_week_data(db, user_id, column, table_name, wid):
    (first_timestamp, last_timestamp) = get_first_last_timestamp(db, user_id, column, table_name)
    cur = db.cursor()
    query = 'SELECT start_timestamp, %s FROM %s WHERE user = %%s AND start_timestamp > DATE_SUB(%%s, INTERVAL 7 DAY)' % (column + '_quality', table_name)
    cur.execute(query, (user_id, last_timestamp))    
    fetched_data = cur.fetchall()
    cur.close()
    common_plotting(fetched_data, user_id, column, 'week_', DATE_FMT, wid, [last_timestamp - timedelta(days = 7), last_timestamp + timedelta(days = 1)])

def plot_month_data(db, user_id, column, table_name):
    (first_timestamp, last_timestamp) = get_first_last_timestamp(db, user_id, column, table_name)
    cur = db.cursor()
    query = 'SELECT start_timestamp, %s FROM %s WHERE user = %%s AND start_timestamp > DATE_SUB(%%s, INTERVAL 37 DAY) AND start_timestamp <= DATE_SUB(%%s, INTERVAL 7 DAY)' % (column + '_quality', table_name)
    cur.execute(query, (user_id, last_timestamp, last_timestamp))    
    fetched_data = cur.fetchall()
    cur.close()
    common_plotting(fetched_data, user_id, column, 'month_', DATE_FMT, None, [last_timestamp - timedelta(days = 37), last_timestamp - timedelta(days = 6)])

def plot_all_data(db, user_id, column, table_name):
    cur = db.cursor()
    query = 'SELECT start_timestamp, %s FROM %s WHERE user = %%s' % (column + '_quality', table_name)
    cur.execute(query, (user_id))
    fetched_data = cur.fetchall()
    cur.close()
    common_plotting(fetched_data, user_id, column, 'all_', DATE_FMT)

def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

def plot_random_days(db, user_id, column, table_name, wid, count):
    (first_timestamp, last_timestamp) = get_first_last_timestamp(db, user_id, column, table_name)
    i = 0
    while i < count:
        date = random_date(first_timestamp, last_timestamp)
        print date
        start_date = datetime(date.year, date.month, date.day, 0, 0)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59)
        cur = db.cursor()
        query = 'SELECT start_timestamp, %s FROM %s WHERE user = %%s AND start_timestamp > %%s AND start_timestamp < %%s ORDER BY start_timestamp DESC' % (column + '_quality', table_name)
        cur.execute(query, (user_id, start_date, end_date))
        fetched_data = cur.fetchall()
        cur.close()
        values = [row[1] for row in fetched_data]
        print any(v > 0 for v in values)
        if any(v > 0 for v in values):
            common_plotting(fetched_data, user_id, column, 'day_', DAY_FMT, wid, [start_date, end_date])
            i = i + 1
        else:
            print 'Day empty, taking another day.'

try:
    db_quality = MySQLdb.connect(host = HOST, user = USER, passwd = PWD, db = DB_QUALITY)
    print 'Connected to database: ', DB_QUALITY
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])

USERS_LIST = get_users_list(db_quality)
USER_IDX = 0

for connection in DB_CONN.keys():
    for single_user in USERS_LIST:
        USER_IDX = USER_IDX + 1
        user_name = "user" + str(USER_IDX)
        
        print "Processing: ", user_name
        plot_week_data(db_quality, single_user[0], DB_CONN[connection], TB_QUALITY_DAILY, 0.3)
        plot_month_data(db_quality, single_user[0], DB_CONN[connection], TB_QUALITY_DAILY)
        plot_all_data(db_quality, single_user[0], DB_CONN[connection], TB_QUALITY_DAILY)
        plot_random_days(db_quality, single_user[0], DB_CONN[connection], TB_QUALITY_HOURLY, 0.035, 3)
        
        if USER_IDX > 4:
            USER_IDX = 0
db_quality.close()


