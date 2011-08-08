import sqlite3

class InvalidInput(Exception):
	pass

class NoSuchProject(Exception):
	pass

class NoProjectSelected(Exception):
	pass

class InconsistentEventList(Exception):
	pass

class Session():

	def __init__(self):
		self.startEvent = None
		self.stopEvent = None
		self.events = []

	def __repr__(self):
		return "<Session %s %s>" % (self.startEvent, self.stopEvent)	
	
	@staticmethod
	def sessionListFromEventList(events):
		sessions = []
		session = None
		for event in events:
			if event.eventType == "start":
				if session != None:
					raise InconsistentEventList
				session = Session()
				session.startEvent = event
				session.events.append(event)

			elif event.eventType == "stop":
				if session == None:
					raise InconsistentEventList
				session.stopEvent = event
				session.events.append(event)
				sessions.append( session )
				session = None
			else:
				if session != None:
					session.events.append(event)
				else:
					raise InconsistentEventList

		if session != None:
			session.endEvent = None
			sessions.append( session )
		return sessions

class Event():
	def __init__(self,eventType,timestamp,note):
		self.eventType = eventType
		self.timestamp = timestamp
		self.note = note

	def __eq__(self,other):
		if self.eventType != other.eventType:
			return False
		if self.timestamp != other.timestamp:
			return False
		if self.note != other.note:
			return False
		return True
		
	def __ne__(self, other):
		return not self.__eq__(other)

	def __repr__(self):
		return self.__unicode__()

	def __str__(self):
		return self.__unicode__()
	
	def __unicode__(self):
		return "<event %s %d %s>" % (self.eventType, self.timestamp, self.note)

class Model():

	def __init__(self,dbPath):
		self.conn = sqlite3.connect(dbPath)
		c = self.conn.cursor()
		c.execute("""
			CREATE TABLE IF NOT EXISTS events (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				project TEXT NOT NULL,
				event_type TEXT NOT NULL,
				timestamp INT NOT NULL,
				note TEXT
			);
			""")
		c.execute("""
			CREATE TABLE IF NOT EXISTS projects (
				name TEXT PRIMARY KEY NOT NULL
			);
			""")
		c.execute("""
			CREATE TABLE IF NOT EXISTS current_project (
				project_name TEXT PRIMARY KEY NOT NULL
			);
			""")

		self.conn.commit()
		c.close()
	
	def createProjectIfNotExists(self,projectName):
		c = self.conn.cursor()
		c.execute("INSERT INTO projects (name) VALUES (?)",(projectName,))
		self.conn.commit()
		c.close()
	
	def projectExists(self,projectName):
		c = self.conn.cursor()
		c.execute("select * from projects where name=?",(projectName,))
		row = c.fetchone()
		return row != None

	def switchToProject(self, projectName):
		if not self.projectExists(projectName):
			raise NoSuchProject()
		c = self.conn.cursor()
		c.execute("DELETE from current_project")
		c.execute("INSERT into current_project VALUES (?)",(projectName,))
		self.conn.commit()
		c.close()
	
	def getCurrentProject(self):
		c = self.conn.cursor()
		c.execute("select project_name from current_project")
		row = c.fetchone()
		c.close();
		if row != None:
			return row[0]
		else:
			raise NoProjectSelected()
	
	def insertEvent(self, event):
		current_project = self.getCurrentProject()
		c = self.conn.cursor()
		c.execute("insert into events (project,event_type,timestamp,note) VALUES (?,?,?,?)",(
			current_project,
			event.eventType,
			event.timestamp,
			event.note,
		))
		self.conn.commit()
		c.close();


	def getEventsForProject(self, project):
		def row2event(row):
			return Event(row[1],row[2],row[3])
		c = self.conn.cursor()
		c.execute("""
			SELECT project,event_type,timestamp,note
			FROM events
			WHERE project = ?
			ORDER BY timestamp ASC
			""",(project,))
		events = []
		for row in c.fetchall():
			events.append(row2event(row))
		c.close()
		return events
	
	def getSessionsForProject(self,project):
		pass
	
	def close(self):
		self.conn.close()
