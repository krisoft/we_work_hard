#!/usr/bin/env python

import sys
import os
import sqlite3
import time
import pprint

DATABASE_FILE = "/Users/sly/Dropbox/weWorkHard/wwh.db"

conn = None
def open_database():
	global conn
	conn = sqlite3.connect(DATABASE_FILE)
	# create table if
	c = conn.cursor()
	c.execute("""
	CREATE TABLE IF NOT EXISTS wwh (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		entry_type TEXT NOT NULL,
		timestamp INT NOT NULL,
		note TEXT
	);
	""")
	conn.commit()
	c.close()

def register_entry(entry_type, timestamp, note):
	c = conn.cursor()
	c.execute("INSERT into wwh (entry_type, timestamp, note) VALUES (?,?,?)",(entry_type,timestamp,note))
	conn.commit()
	c.close()

def close_database():
	conn.commit()
	conn.close()

def is_working_hard():
	c = conn.cursor()
	c.execute("SELECT entry_type from wwh WHERE entry_type == 'stop' or entry_type == 'start' ORDER BY timestamp DESC LIMIT 1")
	row = c.fetchone()
	if row == None:
		return False
	result = row[0]
	return result == "start"

class Session(object):

	def __init__(self):
		self.starttime = None
		self.stoptime = None
		self.notes = []
	
	def addNote(self,note):
		note = note.strip()
		if len(note) > 0:
			self.notes.append(note)
	
	@staticmethod
	def timestamp_to_string(timestamp):
		from datetime import datetime
		dt = datetime.fromtimestamp(timestamp)
		return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
	
	def pprint(self):
		if self.starttime == None or self.stoptime == None:
			print "missing start or stoptime"
			print "====="
			return
		print("start:    " + Session.timestamp_to_string(self.starttime))
		print("stop:     " + Session.timestamp_to_string(self.stoptime))
		print("duration: " + str(self.stoptime - self.starttime)) + " sec"
		print("notes:    ")
		for note in self.notes:
			print("          " + note)
		print "====="

all_sessions = []

def export():
	global all_sessions
	c = conn.cursor()
	c.execute("SELECT * from wwh ORDER BY timestamp ASC")
	session = None
	for row in c:
		row_id = row[0]
		entry_type = row[1]
		timestamp = row[2]
		note = row[3]
		if entry_type == 'start':
			if session != None:
				all_sessions.append(session)
			session = Session()
			session.starttime = timestamp
			session.addNote(note)
		if entry_type == 'stop':
			session.stoptime = timestamp
			session.addNote(note)
		if entry_type == 'note':
			session.addNote(note)
	if session != None:
		all_sessions.append(session)
	c.close()

def show():
	global all_sessions
	print "===="
	for session in all_sessions:
		session.pprint()

class InvalidInput(Exception):
	pass

def main():
	try:
		
		try:
			action = sys.argv[1]
			note = ' '.join(sys.argv[2:])
			timestamp = int(time.time())
		except IndexError:
			raise InvalidInput()
		
		open_database()
		
		if action == 'start':
			if is_working_hard():
				register_entry('stop',timestamp-1,"")
			register_entry('start',timestamp,note)
		elif action == 'stop':
			register_entry('stop',timestamp,note)
		elif action == 'note':
			register_entry('note',timestamp,note)
		elif action == 'show':
			if is_working_hard():
				print("you are still working")
				return
			export()
			show()
		else:
			raise InvalidInput()
		
		close_database()
	
	except InvalidInput:
		print('Usage:')
		print(' wwh <start|note|stop> [optional note]')

if __name__ == "__main__":
	main()


