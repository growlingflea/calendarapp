#!/usr/bin/env python

import npyscreen
import argparse
import httplib2
import os
import json
import datetime
import curses
import time
import MySQLdb
import urllib
import string
import shutil

from rfc3339 import rfc3339
from apiclient import discovery
from oauth2client import file
from oauth2client import tools
from oauth2client import client
from os import system

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))

flags = None

storage = file.Storage('sample.dat')
CREDENTIALS = storage.get()
if CREDENTIALS is None or CREDENTIALS.invalid:
  CREDENTIALS = tools.run_flow(FLOW, storage, flags)

http = httplib2.Http()
http = CREDENTIALS.authorize(http)

SERVICE = discovery.build('calendar', 'v3', http=http)


freebusy_query = None

class SQL(npyscreen.Form):
  def afterEditing(self):
    self.parentApp.switchFormPrevious()
  
  def getName(username):
    db = MySQLdb.connect("mysql.cs.orst.edu", "cs419_group1", "yuPMS8mTxvbPRn6U", "cs419_group1")
    cursor = db.cursor()
    instructorSearch = """SELECT first_initial, last_name FROM Staff_Sp14 WHERE email=%s;"""
    try:
      cursor.execute(instructorSearch,(username))
      staffSQL = cursor.fetchall()
      #print staffSQL
      staffSQL = list(staffSQL)
      #print staffSQL
    except:
      staffSQL = []
      name = None

    cursor.close()
    db.close()

    if len(staffSQL) > 0:
          name = staffSQL[0][1] + ', ' + staffSQL[0][0] + '.'
    else:
          name = None
    #This line is for troubleshooting only and needs removed from final code
    name = 'Rooker, T.'

    return name

  def scheduleDayOfWeek(classes, dates, x, y):
    temp = []
    start = str(classes[y][8])
    start = start.split(':')
    startHour = int(start[0])
    startMin = int(start[1])
    end = str(classes[y][9])
    end = end.split(':')
    endHour = int(end[0])
    endMin = int(end[1])
    #start = (dates[x][0]).datetime()
    start = dates[x][0]
    #end = (dates[x][0]).datetime()
    end = dates[x][0]
    #print start
    #print end
    start = start.replace(hour=startHour, minute=startMin, second=0)
    end = end.replace(hour=endHour, minute=endMin, second=0)
    ts = rfc3339(start)
    te = rfc3339(end)
    temp = [ts, ts]
    return temp

  def checkDates(event,startWindow,endWindow):
    start = datetime.datetime.strptime(event[0][0:-6], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=-7)
    end = datetime.datetime.strptime(event[1][0:-6], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=-7)

    #print start
    #print end

    #if start is before startWindow and end is before startWindow
    if start < startWindow and end <= startWindow:
      return -1
    if start < startWindow and end > startWindow:
      start = rfc(startWindow)
      event[0] = start
      return event
    if start >= startWindow and end <= endWindow:
      return event
    if start >= startWindow and start < endWindow and end > endWindow:
      end = rfc(endWindow)
      event[1] = end
      return event
    if start >= startWindow and start >=endWindow and end >=endWindow:
      return -1

  def checkSQLCourseSchedule(username,startWindow,endWindow):

    instructorName = getName(username)

    if instructorName == None:
          return None
    
    #print ("List of classes:")
    classes = []
    db = MySQLdb.connect("mysql.cs.orst.edu", "cs419_group1", "yuPMS8mTxvbPRn6U", "cs419_group1")
    cursor = db.cursor()
    
    #Assumes M-S pull all classes.
    scheduleSearch = """SELECT department, course_id, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, start_time, end_time FROM Schedule_Sp14 WHERE instructor=%s;"""
    cursor.execute(scheduleSearch,(instructorName))
    classSQL = cursor.fetchall()
    #print classSQL
    cursor.close()
    db.close()
    temp = list(classSQL)

    for x in temp:
        classes.append(list(x))

    temp = []
    dates = []

    startWindow = datetime.datetime.strptime(startWindow[0:-6], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=-7)
    endWindow = datetime.datetime.strptime(endWindow[0:-6], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=-7)

    dayOfWeek = startWindow
    temp = [dayOfWeek, startWindow.weekday()]
    dates.append(temp)
    while dayOfWeek < endWindow:
      dayOfWeek = dayOfWeek + datetime.timedelta(days=1)
      temp = [dayOfWeek, dayOfWeek.weekday()]
      dates.append(temp)

    #print dates
    temp = []

    for x in range(len(dates)):
      for y in range(len(classes)):
        #print classes[y]
        #Monday
        if dates[x][1] == 0 and classes[y][2] == 1:
          values = scheduleDayOfWeek(classes, dates, x, y)
          check = checkDates(values, startWindow, endWindow)
          if check != -1:
            temp.append(values)
        #Tuesday
        if dates[x][1] == 1 and classes[y][3] == 1:
          values = scheduleDayOfWeek(classes, dates, x, y)
          check = checkDates(values, startWindow, endWindow)
          if check != -1:
            temp.append(values)
        #Wednesday
        if dates[x][1] == 2 and classes[y][4] == 1:
          values = scheduleDayOfWeek(classes, dates, x, y)
          check = checkDates(values, startWindow, endWindow)
          if check != -1:
            temp.append(values)
        #Thursday
        if dates[x][1] == 3 and classes[y][5] == 1:
          values = scheduleDayOfWeek(classes, dates, x, y)
          check = checkDates(values, startWindow, endWindow)
          if check != -1:
            temp.append(values)
        #Friday
        if dates[x][1] == 4 and classes[y][6] == 1:
          values = scheduleDayOfWeek(classes, dates, x, y)
          check = checkDates(values, startWindow, endWindow)
          if check != -1:
            temp.append(values)
        #Saturday
        if dates[x][1] == 5 and classes[y][7] == 1:
          values = scheduleDayOfWeek(classes, dates, x, y)
          check = checkDates(values, startWindow, endWindow)
          if check != -1:
            temp.append(values)

    #print temp
    return temp


  def checkStaff(people, startWindow, endWindow):
    days = []
    dayOfWeek = startWindow
    days.append(dayOfWeek.weekday())
    while dayOfWeek < endWindow:
      dayOfWeek = dayOfWeek + datetime.timedelta(days=1)
      days.append(dayOfWeek.weekday())

    staff = []
    remove = []
    for i in people:
        classes = check_course_schedule_availability(i, startWindow, endWindow)
        if len(classes > 0):
          check = checkDates(classes,startWindow,endWindow)
          if (check != -1):
            remove.append(i)
          else:
            staff.append(i)
    return staff 

class DisplayPersons(npyscreen.Form):
    def afterEditing(self):
      self.parentApp.switchFormPrevious()

    def create(self):
      request = SERVICE.freebusy().query(body=freebusy_query).execute()
      theVals = []
      for name,value in request['calendars'].iteritems():
        if not value['busy']:
          theVals.append(name)
      #INSERT MYSQL REQUEST HERE
      staff = SQL.checkStaff(theVals, startWindow, endWindow)
      #print staff 
      #MERGE Done by the MYSQL check, need to 
      self.displayPersons = self.add(npyscreen.Pager, values = theVals, name='Display Persons')
      #self.displayPersons = self.add(npyscreen.Pager, values = staff, name='Display Persons')


class DisplayTimes(npyscreen.Form):
     def afterEditing(self):
       self.parentApp.switchFormPrevious()

     def create(self):
      request = SERVICE.freebusy().query(body=freebusy_query).execute()
      theVals = []
      events = []
      names = []
      for name,value in request['calendars'].iteritems():
        theVals.append(" ")
        theVals.append(name)
        names.append(str(name))
        for i in value['busy']:
          temp = []
          theVals.append("Start Time: " + i['start'])
          theVals.append("End Time: " + i['end'])
          #create list of events
          temp = [i['start'], i['end']]
          events.append(temp)
      #INSERT MYSQL REQUEST HERE
      startWindow = freebusy_query['timeMin']
      endWindow = freebusy_query['timeMax']
      courses = []
      for i in range(len(names)):
        courses[i] = SQL.checkSQLCourseSchedule(names[i],startWindow,endWindow)
        #print courses
      #INSERT MERGE HERE                  
      self.displayTimes = self.add(npyscreen.Pager, values = theVals, name='Display Times')
      

class MainForm(npyscreen.ActionFormWithMenus):
    def on_ok(self):
      uname = self.username.value.split(",")
      unames = []      
      for idx,i in enumerate(uname):
        unames.append({"id": uname[idx].strip()})
      if not self.startDate.value or not self.endDate.value:
        startWindow = datetime.date.today()
        endWindow = startWindow + datetime.timedelta(weeks = 1)
        startWindow = rfc3339.rfc3339(datetime.datetime.combine(startWindow, datetime.time(8, 0)))
        endWindow = rfc3339.rfc3339(datetime.datetime.combine(endWindow, datetime.time(18, 0)))
      else:
        startWindow = rfc3339.rfc3339(datetime.datetime.combine(self.startDate.value, datetime.time(int(self.startHour.value), int(self.startMinute.value))))
        endWindow = rfc3339.rfc3339(datetime.datetime.combine(self.endDate.value, datetime.time(int(self.endHour.value), int(self.endMinute.value))))
      global freebusy_query
      freebusy_query = {"timeMin" : startWindow, "timeMax" : endWindow, "items" : unames}
      if self.selectDisplay.value[0] == 0:
        self.parentApp.setNextForm('DISPLAY1')
      elif self.selectDisplay.value[0] == 1:
        self.parentApp.setNextForm('DISPLAY2')

    def create(self):
      self.username = self.add(npyscreen.TitleText, name='Username(s)')
      self.startDate = self.add(npyscreen.TitleDateCombo, name='Start Date')
      self.startHour = self.add(npyscreen.TitleSlider, out_of=23, name = "Start Hour")
      self.startMinute = self.add(npyscreen.TitleSlider, out_of=59, name = "Start Minute")
      self.endDate = self.add(npyscreen.TitleDateCombo, name='End Date')
      self.endHour = self.add(npyscreen.TitleSlider, out_of=23, name = "End Hour")
      self.endMinute = self.add(npyscreen.TitleSlider, out_of=59, name = "End Minute")
      self.selectDisplay = self.add(npyscreen.TitleSelectOne, scroll_exit=True, max_height=2, name='Choose Display', values = ['Free Meeting Time(s)', 'Person(s) Available'])
      self.m1 = self.add_menu(name="Help", shortcut="h")
      self.m1.addItem(text = "This is the help and usage")
      self.m1.addItem(text = "description.")
      self.m2 = self.add_menu(name="About", shortcut="a")
      self.m2.addItem(text = "This is the about description.")

    def on_cancel(self):
        self.parentApp.setNextForm(None)

class Scheduler(npyscreen.NPSAppManaged):
    def onStart(self):
      npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
      self.addForm('MAIN', MainForm, name='CS419 Project')
      self.addFormClass('DISPLAY1', DisplayTimes, name='Display Times')
      self.addFormClass('DISPLAY2', DisplayPersons, name='Display Available Persons')
      self.addFormClass(None, SQL, name='CS419 Project')

if __name__ == '__main__':
   App = Scheduler().run()

