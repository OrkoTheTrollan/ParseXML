"""Simple parser for xml-files based on 'The ElementTree XML API'. Gets the data from a xml-File and prints it out as a GUI-table.
   GUI depends on pysimplegui (https://pysimplegui.readthedocs.io). So in Terminal or CMD run: 'pip3 install pysimplegui' before using the program."""

import ctypes
import platform
from tkinter import CENTER, LEFT
import xml.etree.ElementTree as ET
import PySimpleGUI as sg
import base64
import sqlite3

#Fix Bug on Windows when using multiple screens with different scaling
def make_dpi_aware():
    if platform.system() == 'Windows' and int(platform.release()) >= 8: 
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

#gets the xml file
def getXML():
  global mytree
  mytree = ET.parse('data/books.xml')
  global myroot
  myroot = mytree.getroot()
  return myroot, mytree

#Iterate through the root and the childs of the file
#Store tags in taglist for the columns of the table and values in valuelist for the rows
def parseXML():
  global listofvaluelists
  listofvaluelists = []
  i = 0

  for child in myroot:
    global taglist
    taglist = []
    valuelist = []
    def getdata():
      print(child.tag, child.attrib, child.text)
      if child.attrib == {}:
        valuelist.append (child.text)
        taglist.append (child.tag)
      else: 
        #Combine tag and attrib for column name
        for j in child.attrib :
          print(j, child.attrib[j])
          valuelist.append (child.attrib[j])
          taglist.append (child.tag + '_' + j)
    getdata()

    for child in myroot[i]:
      getdata()

      for child in child:
        getdata()

    i = i+1
    
    #Remove linebreaks and unnecessary spaces from valuelist
    temp = []
    for x in valuelist:
      temp.append(x.replace("\n", ""))
    valuelist = temp  
    temp = []
    for y in valuelist:
      temp.append(y.replace("  ", ""))
    valuelist = temp  
    listofvaluelists.append(valuelist)

  #Change doubles in taglist to avoid identical names in the table columns
  for k in range(len(taglist)):
    for l in range(k + 1, len(taglist)):
        if taglist[k] == taglist[l]:
          taglist[k] = taglist[k]+'_1'
          taglist[l] = taglist[l]+'_2'
          

  # Print lines for testing purposes
  print(taglist)
  print()
  print(valuelist)
  print()
  print(listofvaluelists)
  return taglist, valuelist, listofvaluelists

# Create SQL-database and inserts xml-values in a table; unfortunately no use of dynamic SQL, so table names and column names need to be static
def xmltosql():
  con = sqlite3.connect('data/xml.db')
  cur = con.cursor()
  
  # Delete and create table
  cur.execute('''DROP TABLE if exists books''')
  cur.execute('''CREATE TABLE books
               (book_id text, author text, title text, genre text, price real, publish_date text, description text)''')

  # Insert a row of data by iterating through listofvaluelists and nested lists
  for element in listofvaluelists:
    print(element)
    elementtuple = tuple(element)
    query = 'INSERT INTO books VALUES {};'.format(elementtuple)
    cur.execute(query)

  # Save (commit) the changes
  con.commit()

  # Close connection
  con.close()

    
# creates window with table 
def make_window(theme=None):
    make_dpi_aware()
    rows = len(listofvaluelists)
    sg.theme(theme)
    sg.set_global_icon(icon = 'settings/xml.ico') if platform.system() == 'Windows' else sg.set_global_icon(base64.b64encode(open('settings/xml.png', 'rb').read())) 
    layout = [[sg.Table(listofvaluelists, taglist, num_rows=rows, justification=LEFT, expand_x=True, expand_y=True)]]
    window = sg.Window('Table of XML-Input', layout, finalize=True, right_click_menu=sg.MENU_RIGHT_CLICK_EXIT, keep_on_top=True, resizable=True)

    return window

def main():
  getXML()
  parseXML()
  xmltosql()
  window = make_window()

  while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
  window.close()
  
main()  


