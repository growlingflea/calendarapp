#!/usr/bin/env python


import httplib2
import os
import datetime
import curses
import time
import MySQLdb
import urllib
import string
import shutil
from rfc3339 import rfc3339


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
		
def courseDBSearch(username):
	classes = []
	db = MySQLdb.connect("mysql.cs.orst.edu", "cs419_group1", "yuPMS8mTxvbPRn6U", "cs419_group1")
	cursor = db.cursor()
	#Assumes M-S pull all classes.
	scheduleSearch = """SELECT department, course_id, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, start_time, end_time FROM Schedule_Sp14 WHERE instructor=%s;"""
	cursor.execute(scheduleSearch,(username))
	classSQL = cursor.fetchall()
	#print classSQL
	cursor.close()
	db.close()
	temp = list(classSQL)
	for x in temp:
		classes.append(list(x))
	return classes
	
def datesFormat(startWindow, endWindow):
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
	return dates
	
def formatCourseTimes(startDate, startTime, endTime, startWindow, endWindow, username):
	endDate = startDate
	startDate = startDate.replace(hour=0, minute=0, second=0)
	endDate = endDate.replace(hour=0, minute=0, second=0)
	startDate = startDate + startTime
	endDate = endDate + endTime
	
	#check dates within range

	#if start is before startWindow and end is before startWindow
	
	startWindow = datetime.datetime.strptime(startWindow[0:-6], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=-7)
	endWindow = datetime.datetime.strptime(endWindow[0:-6], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=-7)
	if startDate < startWindow:
		startDate = startWindow
	if endDate < startWindow:
		return -1
	if endDate > endWindow:
		endDate = endWindow
	if startDate > endWindow:
		return -1
	if startDate == endDate:
		return -1
		
	
		
	return [startDate, endDate, 'DB']
	#return temp
	
	
def removeDuplicates(list):
	#incoming list = [[datetime, datetime, string], [startDate, endDate, DB], ...]
	remove = []
	length1 = len(list)
	for x in range(list):
		for y in range(x+1, list):
			if list[x][0] == list[y][0]:
				if list[x][1] == list[y][1]:
					remove.append(x)
	#if len(remove) > 0:
	#	remove = list(set(remove))
	#	remove.reverse()
	#	for x in range(len(remove)):
	#		result.pop(remove[x])
	
	if len(remove) > 0:
		return remove
	
	return -1
	
def dbResultsToDays(classes, dates, startWindow, endWindow, username):
	#dates = [[datetime, int], [day to search, day of week], ...]
	#rawDBCourseInfo = [[string, int, int, int, int, int, int, int, timedelta, timedelta], [dept, course#, Mon, Tues, Wed, Thurs, Fri, Sat, start time, end time], ...]
	searchWindow = []
	scheduleInfo = []
	result = []
	format_error = -1
	for searchDay in dates: #datesFormat
		temp = []
		for item in searchDay:
			temp.append(item)
		searchWindow.append(temp)
	for course in classes: #rawDBCourseInfo
		temp = []
		for item in course:
			temp.append(item)
		scheduleInfo.append(temp)
	for x in range(len(searchWindow)): #dates / times
		for y in range(len(scheduleInfo)): #classes / events
			#Monday
			if searchWindow[x][1] == 0:
				if scheduleInfo[y][2] == 1:
					#result.append('Course: Monday')
					#create list = [date, start time, end time]
					#temp = [searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9]]
					temp1 = formatCourseTimes(searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9], startWindow, endWindow, username)
					#result.append(temp)
					if temp1 != -1:
						result.append(temp1)
			#Tuesday
			if searchWindow[x][1] == 1:
				if scheduleInfo[y][3] == 1:
					#result.append('Course: Tuesday')
					#create list = [date, start time, end time]
					#temp = [searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9]]
					temp1 = formatCourseTimes(searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9], startWindow, endWindow, username)
					#result.append(temp)
					if temp1 != -1:
						result.append(temp1)
			#Wednesday
			if searchWindow[x][1] == 2:
				if scheduleInfo[y][4] == 1:
					#result.append('Course: Wednesday')
					#create list = [date, start time, end time]
					#temp = [searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9]]
					temp1 = formatCourseTimes(searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9], startWindow, endWindow, username)
					#result.append(temp)
					if temp1 != -1:
						result.append(temp1)
			#Thursday
			if searchWindow[x][1] == 3:
				if scheduleInfo[y][5] == 1:
					#result.append('Course: Thursday')
					#create list = [date, start time, end time]
					#temp = [searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9]]
					temp1 = formatCourseTimes(searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9], startWindow, endWindow, username)
					#result.append(temp)
					if temp1 != -1:
						result.append(temp1)
			#Friday
			if searchWindow[x][1] == 4:
				if scheduleInfo[y][6] == 1:
					#result.append('Course: Friday')
					#create list = [date, start time, end time]
					#temp = [searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9]]
					temp1 = formatCourseTimes(searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9], startWindow, endWindow, username)
					#result.append(temp)
					if temp1 != -1:
						result.append(temp1)
			#Saturday
			if searchWindow[x][1] == 5:
				if scheduleInfo[y][7] == 1:
					#result.append('Course: Saturday')
					#create list = [date, start time, end time]
					#temp = [searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9]]
					temp1 = formatCourseTimes(searchWindow[x][0], scheduleInfo[y][8], scheduleInfo[y][9], startWindow, endWindow, username)
					#result.append(temp)
					if temp1 != -1:
						result.append(temp1)
			#Sunday - No Classes on Sundays

	if len(result) > 0:
		#remove duplicates
		remove = []
		for x in range(len(result)):
			for y in range(x+1, len(result)):
				if result[x][0] == result[y][0]:
					if result[x][1] == result[y][1]:
						remove.append(x)
		
		if len(remove)> 0:
			remove = list(set(remove))
			remove.reverse()
			for x in range(len(remove)):
				result.pop(remove[x])
	
		return result

	return format_error



	

def checkSQLCourseSchedule(username,startWindow,endWindow):
	#instructorName = getName(username)
	#if instructorName == None:
	#      return None
	instructorName = username
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
	
	
def sortResults(events):
	#events = [string, datetime, datetime, string] = [username, startDateTime, endDateTime, dbSource]
	users = []
	for x in range(len(events)):
		value = events[x][0]
		if users.count[value] == 0:
			users.append(value)
	return None
	
	
	
	
	
	