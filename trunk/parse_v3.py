#!/usr/bin/python
# Download the links

# Based on code from http://josechristian.com/2012/09/16/downloading-html-source-code-python/ 

import urllib
import sys
import string
import os
import shutil

### FUNCTIONS ###

#Convert term and year command line arguments into format for sending to web address
def termConvert(term, year):
    if term == "Fall" or term == "fall":
        term_int = "01"
        year = int(year) + 1
        year = str(year)
    elif term == "Winter" or term == "winter":
        term_int = "02"
    elif term == "Spring" or term == "spring":
        term_int = "03"
    elif term == "Summer" or term == "summer":
        term_int = "04"
    else:
        sys.exit("Error - Invalid Term Entered")
    term1 = year + term_int
    return term1

#Convert term and year to schedule abreviation for parsing
def termSchedule(term, year):
    year = int(year) - 2000
    year = str(year)
    if term == "Fall" or term == "fall":
        term_abr = "F"
        year = int(year) + 1
        year = str(year)
    elif term == "Winter" or term == "winter":
        term_abr = "W"
    elif term == "Spring" or term == "spring":
        term_abr = "Sp"
    elif term == "Summer" or term == "summer":
        term_abr = "Su"
    else:
        sys.exit("Error - Invalid Term")
    termSch = term_abr + year
    return termSch

# files where info will be stored to
rawSrc="rawSrc.txt"
linkSrc="lnksSrc.txt"
departments="departments.txt"
scheduleFile="schedule.txt"
tempfile="tempfile.txt"
tempfile2="tempfile2.txt"

# this function will download the source code and save it as a txt file.
def dlSrc(locPage):
    # Open first file where source code will be saved
    wRawSrc=open(rawSrc,"w")
    # connect and donwnload
    webPage=urllib.urlopen(locPage)
    wPageSrc=webPage.read()
    webPage.close()
    # write to text file
    wRawSrc.write(wPageSrc)
    # close file
    wRawSrc.close()

    return None
 
# this function will extract all the links and save them on another txt file
def cleanFile(readfile, writefile, tempfile):
    # open file for reading
    rFile = open(readfile,"r")
    # open the stripped one for writing
    wFile = open(writefile,"w")
    # open temp file for other lines
    wTemp = open(tempfile, "w")
    # export only the lines that contain "a href"
    for line in rFile:
        if "a href" in line:
            wFile.write(line)
        else:
            wTemp.write(line)
    # close files
    rFile.close()
    wFile.close()

    return None
    
# after original HTML code is split and extra items that are not needed (from original html code) are removed
def removeHTMLTags(filename, splitValue):
    # open raw HTML source for reading
    rRawSrc=open(filename,"r")
    data = rRawSrc.readlines()
    sections = []
    for lines in data:
        temp = lines.split(splitValue)
        sections.extend(temp)
    for x in range(len(sections)):
        temp = sections[x]
        temp = str(temp).strip(' ')
        sections[x] = temp
    items = [ '\r\n', '</font', '</h1', '</td', '\t</tr', '</h5', '<br /', '<tr', '<\t<tr', '</a', '<font size="2"', '</form', '</table', '<strong', '--Z--</strong', '\t\t<td', '&nbsp;&nbsp;\r\n', '&nbsp;\r\n',
                  '&nbsp;</td', '"/',  '\t\r\n', '\t\t\r\n', '\t\t\t\t\r\n',  '\t\t\t\t\t\t<td align="right"', '\t\t\t\t\t\t<td nowrap="nowrap" valign="middle"', '\t\t\t\t\t\t<td valign="top"',  '\t\t\t\t\t\t<th scope="col"',
                  '\t\t\t\t\t</tr',  '\t\t\t\t\t<tr', '\t\t\t\t\t<tr align="center"',  '\t\t\t\t</table', '\t\t\t\t\t<tr align="center"',  '\t\t\t\t<td style="vertical-align: top; height: 43px; width: 41px; white-space: nowrap"',
                  '\t\t\t</div','\t\t\t<area shape="rect" coords="0',  '\t\t\t<td',  '\t\t</map', '\t\t</table', '\t\t</tr', '</body', '</br', '</div', '</head', '</html', '</script', '</span', '</strong', '-</strong', '</th', 
                  '</title', '</tr', '<b', '<body', '<div', '<div class="legendDiv"', '<h1 style="font-family:Verdana', '<h3', '<h5', '<head', '<html xmlns="http://www.w3.org/1999/xhtml"', '<meta content="All" name="Robots" /',
                  '<meta content="General" name="Rating" /', '<meta content="Information about Oregon State University" name="Description" /', '<meta content="Oregon State University" name="Author" /',
                  '<meta content="Oregon State University" name="Copyright" /', '<meta http-equiv="Keywords" content="Oregon State University', '<script type="text/javascript"',
                  '<script type="text/javascript"src="scripts/jquery-1.3.2.min.js"', '<script type="text/javascript"src="scripts/legendtoggle/legendtoggle.js"', '<span class="homelink"', '<span class="legendtoggler"',
                  '<span id="ctl00_ContentPlaceHolder1_SOCColumnFilterUC1_cblColumns"', '<span id="ctl00_lblRevisedDate"', '<table id="ctl00_ContentPlaceHolder1_dlCourses" cellspacing="0"',
                  '<table id="ctl00_Table4" border="0" cellpadding="0" cellspacing="0"', '<table id="ctl00_tblFooter" cellspacing="0" cellpadding="0" width="98%"',
                  '<table id="ctl00_tblHeader" style="width: 98%;border: none;" cellpadding="0" cellspacing="0"', '<table id="ctl00_tblQuickJump" cellpadding="0" cellspacing="0" border="0"',
                  '<table id="Table1" cellspacing="0" cellpadding="0" width="650" border="0"', '<table id="Table1" cellspacing="0" cellpadding="0" width="98%" border="0"',
                  '<table id="Table3" cellspacing="1" cellpadding="1" width="380" border="0" align="center"', '<td', '<td align="right" valign="top" nowrap="nowrap"', '<td nowrap="nowrap"', '<td nowrap="nowrap" align="right"',
                  '<td style="white-space: nowrap"', '<td style="width: 15px" valign="top"', '<td style="width: 635px" valign="top"', '<td valign="top" style="width: 15px"', '<td valign="top" style="width: 635px"',
                  '<th scope="col"', '<th scope="col" nowrap="nowrap"', '<title', '<tr align="center" valign="top"', '<tr align="center" valign="top" bgcolor="WhiteSmoke"', '/b', '<BR /', '<br /', '/font', '\n',
                  '\t\t\t\t', '/font\n', '/a\n', '/b\n', 'BR /\n', '', 'br /\n']
    for x in items:
        number = sections.count(x)
        for y in range(number):
            sections.remove(x)
    return sections

#parse rawSrc.txt for department name and tla
def departmentParse():
    sections = []
    sections = removeHTMLTags(linkSrc, '>')

    # open raw HTML source for reading
    rLinkSrc=open(linkSrc,"r")
    # open temp for writing
    wTemp = open(tempfile, "w")

    #print sections


    for x in range(3):
        sections.pop(0)
    for x in range(7):
        sections.pop()

    #print sections

    for x in range(len(sections)):
        if sections[x].find('(Studio)') != -1:
            sections[x] = "Music Studio (MUP) </a"

    #print sections
    
    # save to temp file
    for x in sections:
        print>>wTemp, x

    #close files
    rLinkSrc.close()
    wTemp.close()

    #clean the file temp file back into the linkSrc file
    cleanFile(tempfile, linkSrc, tempfile2)

    # in linkSrc is a list of links to follow for parsing schedules for each department -- note:  line 1 needs removed
    # all links in linkSrc require http://catalog.oregonstate.edu/ before the reference link
    # in tempfile2 is a list of departments to parse w/ TLAs -- note:  line 1 needs removed
    #parse tempfile2 into departments
    #open tempfile2 for reading
    rTemp2 = open (tempfile2, "r")
    #open departments file for writing
    wDepartments = open (departments, "w")

    #reset sections to empty
    sections = []
    for line in rTemp2:
        line = line[:-6]
        temp = line.split('(')
        sections.extend(temp)
               
    sections.pop()
    sections.pop(0)
    for x in sections:
        print>>wDepartments, x
    
    #print sections
    # departments.txt now contains list of department name (TLA) for each department

    #close files
    rTemp2.close()
    wDepartments.close()

    #parse linkSrc into just html addresses

    #copy linkSrc to tempfile
    shutil.copy(linkSrc, tempfile)

    #open files to read (tempfile) / write (linkSrc)
    rTemp = open(tempfile, "r")
    wLinkSrc = open(linkSrc, "w")

    for line in rTemp:
        text = line
        text = text[:-2]
        text = text[9:]
        intro = "http://catalog.oregonstate.edu/"
        # ending allows for only the columns with term, section, instructor, and day/time/date to be shown in HTML code
        ending = "&columns=agjk"
        text = intro + text
        text = text + ending
        wLinkSrc.write(text)
        wLinkSrc.write("\n")
        
    #close files
    rTemp.close()
    wLinkSrc.close()

    return None

def scheduleParse(term, year):
    #open link list
    rlinkSrc = open(linkSrc, "r")
    aSchedule = open(scheduleFile, 'a')
    sections = []

    #COMMENT OUT FOR LOOP TO MANUALLY TEST W/ SINGLE PAGE
    for line in rlinkSrc:
        page = line
        #print page
        dlSrc(page)
        sections = htmlParseCourse(rawSrc, term, year)
        #print sections
        for x in range(len(sections)):
            for y in range(4):
                aSchedule.write(sections[x][y])
                aSchedule.write("\n")
            #print>>aSchedule, schedule[x][y]
        

    #run function to get sourse HTML code from each page
    #dlSrc("http://catalog.oregonstate.edu/SOCList.aspx?subjectcode=JPN&termcode=201403&campus=corvallis&columns=agjk")
    #htmlParseCourse(rawSrc, term, year)

    
    rlinkSrc.close()
    aSchedule.close()
    return None

def htmlParseCourse(filename, term, year):
    sections = []
    sections = removeHTMLTags(filename, '>')
    #print sections

    for x in range(185):
        sections.pop(0)
    for x in range(55):
        sections.pop()

    #print sections

    #save to temp file and re-split
    wTemp = open (tempfile, "w")
    for x in sections:
        print>>wTemp, x
    wTemp.close()

    sections = removeHTMLTags(tempfile, '<')
    for x in range(len(sections)):
        temp = sections[x]
        temp = str(temp).strip('\n')
        temp = str(temp).strip('\r')
        sections[x] = temp
    
    #print sections

    termSch = termSchedule(term, year)
    #print termSch

    courses = []
    count = []
    for x in range(len(sections)):
        if sections[x].find('href') != -1:
            temp = sections[x]
            subject = temp[38:42]
            subject = subject.strip('&c')
            courseNum = temp[-5:-1]
            courseNum = courseNum.lstrip('=')
            courseID = subject + ' ' + courseNum
            courses.append(courseID)
            count.append(x)

    schedule = []
    for y in range(len(sections)):
        if sections[y].find(termSch) != -1:
            courseSection = sections[y+1]
            instructor = sections[y+2]
            dates = sections[y+3]
            for x in range(len(count)):
                if count[x] < y:
                    courseID = courses[x]
            temp = []
            temp = [courseID, courseSection, instructor, dates]
            schedule.append(temp)
    
            
    #print count
    #print courses
    #print schedule
    #print schedule[10][0]
    #print len(schedule)
    #print len(count)
    
    return schedule
   

### MAIN PROGRAM ###

# sys will be for command line use of program, format required will be Fall/Winter/Spring/Summer YYYY
try:
    term = os.system('"' + sys.argv[1] + '"')
    year = os.system('"' + sys.argv[2] + '"')
    term1 = termConvert(term, year)
# exception for if command line arguments are not entered, request user input
except:
    #term_input = raw_input("Please enter term (Fall, Winter, Spring, or Summer):\n")
    #year_input = raw_input("Please enter year (Example:  2014):\n")
    #term1 = termConvert(term_input, year_input)
# test if return is correct
#print term1

    term2 = "201403"

# Create name for website to pull from
page = "http://catalog.oregonstate.edu/SOC.aspx?level=all&campus=corvallis&term="
homepage = page + term2

# Run the functions
#currently manually set for current term, needs above code turned on to allow for user input of term
dlSrc(homepage)
cleanFile(rawSrc, linkSrc, tempfile)
departmentParse()
term = "Spring"
year = 2014
scheduleParse(term, year)


os.remove(tempfile)
os.remove(tempfile2)


