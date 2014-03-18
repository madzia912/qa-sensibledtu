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
import pylab as pl
import MySQLdb
from random import randrange

# Diagram layout settings
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

TB_QUALITY_DAILY = 'data_quality_daily'
TB_QUALITY_HOURLY = 'data_quality_hourly'
TB_LAST_SCANS = 'user_last_scans'

DB_QUALITY = 'data_quality'

def get_users_list(db):
    cur = db.cursor()
    cur.execute('SELECT DISTINCT(user) FROM user_last_scans')
    result = cur.fetchall()
    cur.close()
    return result

def common_plotting(user_data, user_id, prefix, xlim=None):
    x_val = [date2num(row[0]) for row in user_data]
    y_val = [row[1] for row in user_data]
    colors = get_bar_colour(y_val)
    pl.figure()
    pl.subplot(111)
    pl.bar(x_val, y_val, color = colors)
    pl.title('Quality of data for ' + user_id)
    pl.xticks(rotation = 30)
    current_axis = pl.gca()
    current_axis.xaxis.set_major_formatter(DateFormatter(DATE_FMT))
    pl.xlim(xlim)
    plt.show()
    plt.savefig('pictures/' + prefix + user_id + '.png', bbox_inches = 'tight')
    plt.close()

def get_bar_colour(data):
    colors = []
    for value in data:
        if value >= 1.0:
            colors.append('g')
        else:
            colors.append('r')
    return colors

def plot_week_data(db, user_id):
    cur = db.cursor()
    cur.execute('SELECT start_timestamp, bluetooth_quality FROM data_quality_daily WHERE user = %s ORDER BY start_timestamp DESC', (user_id))
    fetched_data = cur.fetchall()
    cur.close()
    last_timestamp = fetched_data[0][0]
    cur = db.cursor()
    cur.execute('SELECT start_timestamp, bluetooth_quality FROM data_quality_daily WHERE user = %s AND start_timestamp > DATE_SUB(%s, INTERVAL 7 DAY)', (user_id, last_timestamp))
    fetched_data = cur.fetchall()
    cur.close()
    common_plotting(fetched_data, user_id, 'week_')

def plot_month_data(db, user_id):
    cur = db.cursor()
    cur.execute('SELECT start_timestamp, bluetooth_quality FROM data_quality_daily WHERE user = %s ORDER BY start_timestamp DESC', (user_id))
    fetched_data = cur.fetchall()
    cur.close()
    last_timestamp = fetched_data[0][0]
    cur = db.cursor()
    cur.execute('SELECT start_timestamp, bluetooth_quality FROM data_quality_daily WHERE user = %s AND start_timestamp > DATE_SUB(%s, INTERVAL 37 DAY) AND start_timestamp <= DATE_SUB(%s, INTERVAL 7 DAY)', (user_id, last_timestamp, last_timestamp))
    fetched_data = cur.fetchall()
    cur.close()
    common_plotting(fetched_data, user_id, 'month_')

def plot_all_data(db, user_id):
    cur = db.cursor()
    cur.execute('SELECT start_timestamp, bluetooth_quality FROM data_quality_daily WHERE user = %s', (user_id))
    fetched_data = cur.fetchall()
    cur.close()
    common_plotting(fetched_data, user_id, 'all_')

def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

def plot_random_days(db, user_id, user_name):
    cur = db.cursor()
    cur.execute('SELECT start_timestamp FROM data_quality_hourly WHERE user = %s ORDER BY start_timestamp DESC', (user_id))
    fetched_data = cur.fetchall()
    last_timestamp = fetched_data[0][0]
    first_timestamp = fetched_data[-1][0]
    cur.close()

    for i in xrange(0, 3):
        date = random_date(first_timestamp, last_timestamp)
        start_date = datetime(date.year, date.month, date.day, 0, 0)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59)

        cur = db.cursor()
        cur.execute('SELECT start_timestamp, bluetooth_quality FROM data_quality_hourly WHERE user = %s AND start_timestamp > %s AND start_timestamp < %s ORDER BY start_timestamp DESC', (user_id, start_date, end_date))
        fetched_data = cur.fetchall()
        cur.close()

        x_val = [date2num(row[0]) for row in fetched_data]
        y_val = [row[1] for row in fetched_data]

        colors = get_bar_colour(fetched_data)
        pl.figure()
        pl.subplot(111)
        pl.bar(x_val, y_val, width = 0.035, color = colors)
        pl.xlim([start_date, end_date])
        pl.title('Quality of data per hour, ' + user_name + " " + date.strftime(DATE_FMT))
        pl.xticks(rotation = 30)
        current_axis = pl.gca()
        current_axis.xaxis.set_major_formatter(DateFormatter("%H:%M"))
        plt.show()
        plt.savefig('pictures/' + 'day_' + user_name + '_' + str(i) + '.png', bbox_inches='tight')
        plt.close()

try:
    db_quality = MySQLdb.connect(host = HOST, user = USER, passwd = PWD, db = DB_QUALITY)
    print 'Connected to database: ', DB_QUALITY
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])

USERS_LIST = get_users_list(db_quality)
USER_IDX = 0

for single_user in USERS_LIST:
    USER_IDX = USER_IDX + 1
    user_name = "user" + str(USER_IDX)
    print "Processing: ", user_name
    plot_week_data(db_quality, single_user[0])
    plot_month_data(db_quality, single_user[0])
    plot_all_data(db_quality, single_user[0])
    plot_random_days(db_quality, single_user[0], single_user[0])

db_quality.close()


