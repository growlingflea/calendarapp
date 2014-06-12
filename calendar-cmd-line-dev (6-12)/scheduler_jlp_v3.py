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
import mySQL

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
  

class DisplayPersons(npyscreen.Form):
	def afterEditing(self):
		self.parentApp.switchFormPrevious()

	def create(self):
		request = SERVICE.freebusy().query(body=freebusy_query).execute()
		theVals = []
		names = [] #Names from Google pull
		events = [] #combined list of google/db events
		names1 = [] #list of name
		results = [] #results to printout
		try:
			for name,value in request['calendars'].iteritems():
				if not value['busy']:
					theVals.append(name)
					names.append(str(name))
					#results.append(name)
			#dates = [[datetime, int], [day to search, day of week], ...]
			dates = mySQL.datesFormat(startWindow,endWindow)
			for x in nameList:
				temp = mySQL.getName(x)
				if temp is not None:
					#rawDBCourseInfo = [[string, int, int, int, int, int, int, int, timedelta, timedelta], [dept, course#, Mon, Tues, Wed, Thurs, Fri, Sat, start time, end time], ...]
					rawDBCourseInfo = mySQL.courseDBSearch(temp)
					#classTimes = [[datetime, datetime, string], [startDate, endDate, DB], ...]
					if rawDBCourseInfo is not None:
						classTimes = mySQL.dbResultsToDays(rawDBCourseInfo, dates, startWindow, endWindow, x)
						#combine with events...
						if classTimes is not None:
							for course in classTimes:
								temp1 = []
								temp1.append(x)
								for item in course:
									temp1.append(item)
								events.append(temp1)
				else:
					if results.count(x) == 0:
						if theVals.count(x) != 0:
							results.append(x)
					
			beginTime = datetime.datetime.strptime(startWindow[0:-6], "%Y-%m-%dT%H:%M:%S") #+ datetime.timedelta(hours=-7)
			endTime = datetime.datetime.strptime(endWindow[0:-6], "%Y-%m-%dT%H:%M:%S") #+ datetime.timedelta(hours=-7)
			
			try:
				startTimes = []
				for z in range(len(events)):
					if startTimes.count(events[z][1]) == 0:
						startTimes.append([events[z][1],events[z][2]])
				#end times vs start times
				sorted = []
				startValue = events[0][1] 
				endValue = events[0][2]
				for z in range(len(events)):
					if events[z][1] <= endValue and events[z][1] >= startValue:
						if events[z][2] >= endValue:
							endValue = events[z][2]
					elif events[z][1] > endValue:
						sorted.append([events[z][0], startValue, endValue, events[z][3]])
						startValue = events[z][1]
						endValue = events[z][2]
					if z == len(events)-1:
						sorted.append([events[z][0], startValue, endValue, events[z][3]])
						
				try:
					for x in range(len(sorted)):
						if results.count(sorted[x][0]) == 0:
							if theVals.count(sorted[x][0]) != 0:
								results.append(sorted[x][0])
				except:
					dummy = 0
			except:
				dummy = 0
		
		except:
			results.append("Error processing current request.  Please modify request and try again.")
			
		self.displayPersons = self.add(npyscreen.Pager, values = results, name='Display Persons')

class DisplayTimes(npyscreen.Form):
	def afterEditing(self):
		self.parentApp.switchFormPrevious()
		
	def create(self):
		request = SERVICE.freebusy().query(body=freebusy_query).execute()
		theVals = [] #Google pull
		names = [] #Names from Google pull
		events = [] #combined list of google/db events
		names1 = [] #list of name
		results = [] #results to printout
		try:
			for name,value in request['calendars'].iteritems():
				theVals.append(" ")
				theVals.append(name)
				names.append(str(name))
				for i in value['busy']:
					temp = []
					theVals.append("Start Time: " + i['start'])
					theVals.append("End Time: " + i['end'])
					time1 = str(i['start'])
					time2 = str(i['end'])
					time1 = datetime.datetime.strptime(time1[0:-1], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=-7)
					time2 = datetime.datetime.strptime(time2[0:-1], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=-7)
					temp = [str(name), time1, time2, 'G']
					events.append(temp)
					
			#dates = [[datetime, int], [day to search, day of week], ...]
			dates = mySQL.datesFormat(startWindow,endWindow)
			for x in nameList:
				temp = mySQL.getName(x)
				if temp is not None:
					#rawDBCourseInfo = [[string, int, int, int, int, int, int, int, timedelta, timedelta], [dept, course#, Mon, Tues, Wed, Thurs, Fri, Sat, start time, end time], ...]
					rawDBCourseInfo = mySQL.courseDBSearch(temp)
					#classTimes = [[datetime, datetime, string], [startDate, endDate, DB], ...]
					if rawDBCourseInfo is not None:
						classTimes = mySQL.dbResultsToDays(rawDBCourseInfo, dates, startWindow, endWindow, x)
						#combine with events...
						if classTimes is not None:
							for course in classTimes:
								temp1 = []
								temp1.append(x)
								for item in course:
									temp1.append(item)
								events.append(temp1)
							
			beginTime = datetime.datetime.strptime(startWindow[0:-6], "%Y-%m-%dT%H:%M:%S") #+ datetime.timedelta(hours=-7)
			endTime = datetime.datetime.strptime(endWindow[0:-6], "%Y-%m-%dT%H:%M:%S") #+ datetime.timedelta(hours=-7)
			results.append("Free Time on Calendar")
			
			#if len(events) > 0:
			try:
				events.sort(key=lambda x: x[1])
				#list of start times
				startTimes = []
				for z in range(len(events)):
					if startTimes.count(events[z][1]) == 0:
						startTimes.append([events[z][1],events[z][2]])
				#end times vs start times
				try:
					sorted = []
					startValue = events[0][1] 
					endValue = events[0][2]
					for z in range(len(events)):
						if events[z][1] <= endValue and events[z][1] >= startValue:
							if events[z][2] >= endValue:
								endValue = events[z][2]
						elif events[z][1] > endValue:
							sorted.append([events[z][0], startValue, endValue, events[z][3]])
							startValue = events[z][1]
							endValue = events[z][2]
						if z == len(events)-1:
							sorted.append([events[z][0], startValue, endValue, events[z][3]])
				except:
					dummy = 0
				#Flip to open times
				try:
					freeTime = []
					freeBegin = beginTime
					freeEnd = beginTime
					if len(sorted) > 0:
						for z in range(len(sorted)):
							if z == 0:
								if sorted[z][1] > beginTime:
									freeEnd = sorted[z][1]
									freeBegin = beginTime
								else:
									freeEnd = sorted[z+1][1]
									freeBegin = sorted[z][2]
							if z >  0:
								freeEnd = sorted[z][1]
								freeBegin = sorted[z-1][2]
							if freeTime.count(['free', freeBegin, freeEnd]) == 0:
								freeTime.append(['free', freeBegin, freeEnd])
						if sorted[len(sorted)-1][2] < endTime:
							freeTime.append(['free', sorted[len(sorted)-1][2], endTime])
						for y in range(len(freeTime)):
							#results.append("Start Time: " + rfc3339.rfc3339(freeTime[y][1]))
							#results.append("End Time: " + rfc3339.rfc3339(freeTime[y][2]))
							#results.append(rfc3339.rfc3339(freeTime[y][1]) + " to " + rfc3339.rfc3339(freeTime[y][2]))
							results.append((freeTime[y][1]).strftime("%A, %d. %B %Y %I:%M%p") + " to " + (freeTime[y][2]).strftime("%A, %d. %B %Y %I:%M%p"))
				except:
					dummy = 0
			except:
				dummy = 0
			if len(results) == 1:
				results.append(beginTime.strftime("%A, %d. %B %Y %I:%M%p") + " to " + endTime.strftime("%A, %d. %B %Y %I:%M%p"))
		except:
			results.append("Error processing current request.  Please modify request and try again.")			
		self.DisplayTimes = self.add(npyscreen.Pager, values = results, name='Display Times')

class DisplayTimesbyPerson(npyscreen.Form):
	def afterEditing(self):
		self.parentApp.switchFormPrevious()
		
	def create(self):
		request = SERVICE.freebusy().query(body=freebusy_query).execute()
		theVals = [] #Google pull
		names = [] #Names from Google pull
		events = [] #combined list of google/db events
		names1 = [] #list of name
		results = [] #results to printout
		try:
			for name,value in request['calendars'].iteritems():
				theVals.append(" ")
				theVals.append(name)
				names.append(str(name))
				for i in value['busy']:
					temp = []
					theVals.append("Start Time: " + i['start'])
					theVals.append("End Time: " + i['end'])
					time1 = str(i['start'])
					time2 = str(i['end'])
					time1 = datetime.datetime.strptime(time1[0:-1], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=-7)
					time2 = datetime.datetime.strptime(time2[0:-1], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=-7)
					temp = [str(name), time1, time2, 'G']
					events.append(temp)
					
			#dates = [[datetime, int], [day to search, day of week], ...]
			dates = mySQL.datesFormat(startWindow,endWindow)
			for x in nameList:
				temp = mySQL.getName(x)
				if temp is not None:
					#rawDBCourseInfo = [[string, int, int, int, int, int, int, int, timedelta, timedelta], [dept, course#, Mon, Tues, Wed, Thurs, Fri, Sat, start time, end time], ...]
					rawDBCourseInfo = mySQL.courseDBSearch(temp)
					#classTimes = [[datetime, datetime, string], [startDate, endDate, DB], ...]
					classTimes = mySQL.dbResultsToDays(rawDBCourseInfo, dates, startWindow, endWindow, x)
					#combine with events...
					for course in classTimes:
						temp1 = []
						temp1.append(x)
						for item in course:
							temp1.append(item)
						events.append(temp1)
						
			beginTime = datetime.datetime.strptime(startWindow[0:-6], "%Y-%m-%dT%H:%M:%S") #+ datetime.timedelta(hours=-7)
			endTime = datetime.datetime.strptime(endWindow[0:-6], "%Y-%m-%dT%H:%M:%S") #+ datetime.timedelta(hours=-7)
			results.append("Free Time on Calendar")
			
			#if len(events) > 0:			
			try:
				
				#sort the events by each person
				events.sort(key=lambda x: x[0])

				#get list of names
				for x in range(len(events)):
					if names1.count(events[x][0]) == 0:
						names1.append(events[x][0])
								
				for x in range(len(names1)):
					temp = []

					#list by person
					for y in range(len(events)):
						if events[y][0] == names1[x]:
							temp.append(events[y])
					#sort by start time
					temp.sort(key=lambda x: x[1])
					
					#list of start times
					startTimes = []
					for z in range(len(temp)):
						if startTimes.count(temp[z][1]) == 0:
							startTimes.append([temp[z][1],temp[z][2]])

					try:
						#end times vs start times
						sorted = []
						startValue = temp[x][1]
						endValue = temp[x][2]
						for z in range(len(temp)):
							if temp[z][1] <= endValue and temp[z][1] >= startValue:
								if temp[z][2] >= endValue:
									endValue = temp[z][2]
							elif temp[z][1] > endValue:
								sorted.append([temp[x][0], startValue, endValue, temp[z][3]])
								startValue = temp[z][1]
								endValue = temp[z][2]	
					except:
						dummy = 0
						

					try:
						#Flip to open
						freeTime = []
						freeBegin = beginTime
						freeEnd = beginTime
						for z in range(len(sorted)):
							if z == 0:
								if sorted[z][1] > beginTime:
									freeEnd = sorted[z][1]
									freeBegin = beginTime
								else:
									freeEnd = sorted[z+1][1]
									freeBegin = sorted[z][2]
							if z >  0:
								freeEnd = sorted[z][1]
								freeBegin = sorted[z-1][2]
							if freeTime.count(['free', freeBegin, freeEnd]) == 0:
								freeTime.append(['free', freeBegin, freeEnd])
						if sorted[len(sorted)-1][2] < endTime:
							freeTime.append(['free', sorted[len(sorted)-1][2], endTime])
						results.append(temp[x][0])				
						for y in range(len(freeTime)):
							#results.append("Start Time: " + rfc3339.rfc3339(freeTime[y][1]))
							#results.append("End Time: " + rfc3339.rfc3339(freeTime[y][2]))
							#results.append(rfc3339.rfc3339(freeTime[y][1]) + " to " + rfc3339.rfc3339(freeTime[y][2]))
							results.append((freeTime[y][1]).strftime("%A, %d. %B %Y %I:%M%p") + " to " + (freeTime[y][2]).strftime("%A, %d. %B %Y %I:%M%p"))
					except:
						dummy = 0
			#else:
			except:
				for x in nameList:
					results.append(x)
					results.append(beginTime.strftime("%A, %d. %B %Y %I:%M%p") + " to " + endTime.strftime("%A, %d. %B %Y %I:%M%p"))
		except:	
			results.append("Error processing current request.  Please modify request and try again.")
		self.DisplayTimesbyPerson = self.add(npyscreen.Pager, values = results, name='Display Times by Person')

			

class MainForm(npyscreen.ActionFormWithMenus):
	def on_ok(self):
		global startWindow
		global endWindow
		global nameList
		global uname
		global unames
		nameList = []
		uname = self.username.value.split(",")
		unames = []
		for idx,i in enumerate(uname):
			unames.append({"id": uname[idx].strip()})
			nameList.append(uname[idx].strip())
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
		elif self.selectDisplay.value[0] == 2:
			self.parentApp.setNextForm('DISPLAY3')
			
	def create(self):
		self.username = self.add(npyscreen.TitleText, name='Username(s)')
		self.startDate = self.add(npyscreen.TitleDateCombo, name='Start Date')
		self.startHour = self.add(npyscreen.TitleSlider, out_of=23, name = "Start Hour")
		self.startMinute = self.add(npyscreen.TitleSlider, out_of=59, name = "Start Minute")
		self.endDate = self.add(npyscreen.TitleDateCombo, name='End Date')
		self.endHour = self.add(npyscreen.TitleSlider, out_of=23, name = "End Hour")
		self.endMinute = self.add(npyscreen.TitleSlider, out_of=59, name = "End Minute")
		self.selectDisplay = self.add(npyscreen.TitleSelectOne, scroll_exit=True, max_height=3, name='Choose Display', values = ['Free Meeting Time(s)', 'Person(s) Available', 'Person(s) Schedule'])
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
		self.addFormClass('DISPLAY3', DisplayTimesbyPerson, name='Display Times by Person')

if __name__ == '__main__':
	App = Scheduler().run()

