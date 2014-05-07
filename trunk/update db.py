#!/usr/bin/python

import MySQLdb
import urllib
import sys
import string
import os
import shutil

#Open database connection
db = MySQLdb.connect("mysql.cs.orst.edu", "cs419_group1", "yuPMS8mTxvbPRn6U", "cs419_group1")

#open file for departments

departments="departments.txt"
schedule="schedule.txt"
rFileDept = open(departments,"r")

term = "Sp14"

#Prepare a cursor object using cursor() method
cursor = db.cursor()

#Drop table if it already exists using execute() method
cursor.execute("DROP TABLE IF EXISTS Departments_Sp14")

#Create table for testing
deptSetup = """CREATE TABLE `Departments_Sp14` (
	id int(11) NOT NULL AUTO_INCREMENT,
	department varchar(40) NOT NULL,
	department_tla varchar(4) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY (department_tla)
	) ENGINE = InnoDB;"""

cursor.execute(deptSetup)

#Populate Table
values = []
data = rFileDept.readlines()
for lines in data:
    #print lines
    temp = lines.split('(')
    values.extend(temp)
#print values
for x in range(len(values)):
    temp = values[x]
    temp = str(temp).strip('\n')
    temp = str(temp).strip(')')
    temp = str(temp).rstrip(' ')
    values[x] = temp
for x in range(0, len(values), 2):
    name = values[x]
    tla = values[x+1]
    deptValues = {
        'department': name,
        'department_tla': tla,
    }
    #print name
    #print tla
    addDept = """INSERT IGNORE INTO `Departments_Sp14` (
            department, department_tla)
            VALUES (%(department)s, %(department_tla)s);"""
    cursor.execute(addDept, deptValues)
db.commit()

print "Departments Added to DB."

rFileDept.close()

rFileSchedule = open(schedule,"r")

cursor.execute("DROP TABLE IF EXISTS Schedule_Sp14")

scheduleSetup = """CREATE TABLE `Schedule_Sp14` (
	id int(11) NOT NULL AUTO_INCREMENT,
	department varchar(4) NOT NULL,
	course_id varchar(4) NOT NULL,
	section_id int(11) NOT NULL,
	instructor varchar(40) NOT NULL,
	Monday boolean default 0,
	Tuesday boolean default 0,
	Wednesday boolean default 0,
	Thursday boolean default 0,
	Friday boolean default 0,
	TBA boolean default 0,
	start_time time default '00:00:00',
	end_time time default '00:00:00',
	PRIMARY KEY (id),
	UNIQUE KEY (department, course_id, section_id)
        ) ENGINE = InnoDB;"""
cursor.execute(scheduleSetup)

values = []
data = rFileSchedule.readlines()
for lines in data:
    values.append(lines)
for x in range(len(values)):
    temp = values[x]
    temp = str(temp).strip('\n')
    values[x] = temp
#print values[0:100]
for x in range(0, len(values), 4):
    course = values[x]
    section = values[x+1]
    instructor = values[x+2]
    dates = values[x+3]
    course_id = course[-4:]
    course_id = str(course_id).strip(' ')
    dept_id = course[:-4]
    dept_id = str(dept_id).strip(' ')
    end_time = None
    start_time = None
    days = None
    mon = 0
    tues = 0
    wed = 0
    thurs = 0
    fri = 0
    tba = 0
    if dates != 'TBA':
        end_time = dates[-4:]
        end_time = end_time[:2] + ':' + end_time[2:] + ':00'
        start_time = dates[-9:-5]
        start_time = start_time[:2] + ':' + start_time[2:] + ':00'
        days = dates[:-10]
        if days.find('M') != -1:
            mon = 1
        if days.find('T') != -1:
            tues = 1
        if days.find('W') != -1:
            wed = 1
        if days.find('R') != -1:
            thurs = 1
        if days.find('F') != -1:
            fri = 1
    else:
        tba = 1
        end_time = '00:00:00'
        start_time = '00:00:00'
    scheduleValues = {
        'department': dept_id,
        'course_id': course_id,
        'section_id': section,
        'instructor': instructor,
        'Monday': mon,
        'Tuesday': tues,
    	'Wednesday': wed,
    	'Thursday': thurs,
    	'Friday': fri,
    	'TBA': tba,
        'start_time':  start_time,
        'end_time': end_time,
    }
    addSection = """INSERT IGNORE INTO `Schedule_Sp14` (
        department, course_id, section_id, instructor, Monday, Tuesday, Wednesday, Thursday, Friday, TBA, start_time, end_time)
        VALUES (%(department)s, %(course_id)s, %(section_id)s, %(instructor)s, %(Monday)s, %(Tuesday)s, %(Wednesday)s, %(Thursday)s, %(Friday)s, %(TBA)s, %(start_time)s, %(end_time)s);"""
    cursor.execute(addSection, scheduleValues)
    db.commit()


    #if 4500 < x < 5000:
    #    print dept_id
    #    print course_id
    #    print instructor
    #    print end_time
    #    print start_time
    #    print days
    


rFileSchedule.close()

#disconnect
cursor.close()
db.close()


