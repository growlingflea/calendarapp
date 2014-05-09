#!/usr/bin/env python

"""Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import argparse
import httplib2
import os
import sys
import logging
import curses
import datetime

from os import system
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/647865129103/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def get_param(prompt_string,screen):
	screen.clear()
	screen.border(0)
	screen.addstr(2, 2, prompt_string)
	screen.refresh()
	input = screen.getstr(10, 10, 60)
	return input

def execute_cmd(cmd_string):
	system("clear")
	a = system(cmd_string)
	print ""
	if a == 0:
		print "Command executed correctly"
	else:
		print "Command terminated with error"
	raw_input("Press enter")
	print ""


def main(argv):
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('sample.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Construct the service object for the interacting with the Calendar API.
  service = discovery.build('calendar', 'v3', http=http)

  try:
    pass
    #print ("Success! Now add code here.")

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")



  x = 0

  while x != ord('4'):
	  screen = curses.initscr()

	  screen.clear()
	  screen.border(0)
	  screen.addstr(2, 2, "CS419 Project")
	  screen.addstr(4, 3, "Please enter a number...")
	  screen.addstr(5, 4, "1 - List Contact's Calendars")
	  screen.addstr(6, 4, "2 - List Calendar Events")
	  screen.addstr(7, 4, "3 - Check Contact Availability")
	  screen.addstr(8, 4, "4 - Exit")
	  screen.addstr(9, 0, "")
	  screen.refresh()

	  x = screen.getch()

	  if x == ord('1'):
		  curses.endwin()
#		  execute_cmd("python sample.py")
		  system("clear")
		  list_calendars(service)
		  print ""
		  raw_input("Press enter")
		  print ""
	  if x == ord('2'):
		  curses.endwin()
		  system("clear")
		  list_events(service)
		  print ""
		  raw_input("Press enter")
		  print ""
	  if x == ord('3'):
		  username = get_param("Enter the username:",screen)
		  curses.endwin()
		  system("clear")
		  check_contact_availability(service,username,screen)
		  print ""
		  raw_input("Press enter")
		  print ""

  curses.endwin()


def list_calendars(service):
  # Returns entries on the user's calendar list.
  print ("List of calendars:")
  print
  page_token = None
  while True:
    calendar_list = service.calendarList().list(pageToken=page_token).execute()
    for calendar_list_entry in calendar_list['items']:
      print calendar_list_entry['summary']
    page_token = calendar_list.get('nextPageToken')
    if not page_token:
      break

def list_events(service):
  # Returns events on a specific calendar
  print ("List of events:")
  print
  page_token = None
  while True:
    events = service.events().list(calendarId='primary', pageToken=page_token).execute()
    for event in events['items']:
      print event['summary']
    page_token = events.get('nextPageToken')
    if not page_token:
      break

def check_contact_availability(service,username,screen):
  # Returns events on a specific calendar
  print ("List of events:")
  page_token = None
  while True:
    events = service.events().list(calendarId=username, pageToken=page_token, timeMax='2014-05-15T00:00:00+00:00', timeMin='2014-05-08T00:00:00+00:00').execute()
    for idx,event in enumerate(events['items']):
      print idx
      print "start time:", event['start']['dateTime']
      print "end   time:", event['end']['dateTime']
      #print event['kind']
    page_token = events.get('nextPageToken')
    if not page_token:
      break

# For more information on the Calendar API you can visit:
#
#   https://developers.google.com/google-apps/calendar/firstapp
#
# For more information on the Calendar API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
  main(sys.argv)
