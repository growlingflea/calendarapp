#!/usr/bin/python

import MySQLdb

#Open database connection
db = MySQLdb.connect("mysql.cs.orst.edu", "cs419_group1", "yuPMS8mTxvbPRn6U", "cs419_group1")

#Prepare a cursor object using cursor() method
cursor = db.cursor()

#Drop table if it already exists using execute() method
cursor.execute("DROP TABLE IF EXISTS TEST1")

#Create table for testing
sql = """CREATE TABLE TEST1 (id int(11) NOT NULL AUTO_INCREMENT, instructor VARCHAR(45) NOT NULL, department VARCHAR(10) NOT NULL, PRIMARY KEY (id), UNIQUE KEY(instructor, department)) ENGINE = InnoDB"""


cursor.execute(sql)

#disconnect
db.close()
