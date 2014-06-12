#!/usr/bin/env python

import npyscreen
import argparse
import httplib2
import os
import json
import datetime

from rfc3339 import rfc3339
from apiclient import discovery
from oauth2client import file
from oauth2client import tools
from oauth2client import client

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

class DisplayPersons(npyscreen.Form):
    def afterEditing(self):
      self.parentApp.switchFormPrevious()

    def create(self):
      request = SERVICE.freebusy().query(body=freebusy_query).execute()
      theVals = []
      for name,value in request['calendars'].iteritems():
        if not value['busy']:
          theVals.append(name)
      self.displayPersons = self.add(npyscreen.Pager, values = theVals, name='Display Persons')

class DisplayTimes(npyscreen.Form):
    def afterEditing(self):
      self.parentApp.switchFormPrevious()

    def create(self):
      request = SERVICE.freebusy().query(body=freebusy_query).execute()
      theVals = []
      for name,value in request['calendars'].iteritems():
        theVals.append(" ")
        theVals.append(name)
        for i in value['busy']:
          theVals.append("Start Time: " + i['start'])
          theVals.append("End Time: " + i['end'])
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

if __name__ == '__main__':
   App = Scheduler().run()

