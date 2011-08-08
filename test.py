import unittest
import os
import sqlite3

import work

def deleteFileIfExists(fileName):
	try:
		os.unlink(fileName)
	except OSError:
		pass

def getEmptyTestModel(testDb):
	deleteFileIfExists(testDb)
	model = work.Model(testDb)
	return model

def closeTestModel(model):
	model.close()
	deleteFileIfExists(testDbPath)

def generateEventList(listOfTuplles):
	return map(lambda x,y: work.Event(x[0],y,x[1]),listOfTuplles,range(0,len(listOfTuplles)))



testDbPath = "/tmp/test2.db"
testProjectName = "testProjectName"

class WorkHardModelTest(unittest.TestCase):
	
	def testOpenDatabaseEnsureTables(self):
		testDbPath = "/tmp/test.db"
		model = getEmptyTestModel(testDbPath)
		model.close()
		conn = sqlite3.connect(testDbPath)
		c = conn.cursor()
		try:
			c.execute("select * from events")
			c.execute("select * from projects")
			c.execute("select * from current_project")
		except sqlite3.OperationalError, e:
			self.fail(e)
		c.close()
		conn.close()
		deleteFileIfExists(testDbPath)
	
	def testCreateProject(self):
		model = getEmptyTestModel(testDbPath)

		model.createProjectIfNotExists(testProjectName)
		self.assertTrue(model.projectExists(testProjectName))

		closeTestModel(model)

	
	def testSwitchToExistingProject(self):

		model = getEmptyTestModel(testDbPath)
		model.createProjectIfNotExists(testProjectName)		
		model.switchToProject(testProjectName)
		
		self.assertEquals(model.getCurrentProject(),testProjectName)

		closeTestModel(model)
	
	def testCreateProjectSwitchesToProject(self):
		self.skipTest("Command should switch to project")
		model = getEmptyTestModel(testDbPath)
		model.createProjectIfNotExists(testProjectName)
		self.assertEquals(testProjectName,model.getCurrentProject())
		closeTestModel(model)
	
	def testSwitchToNonExistingProjectRaisesNoSuchProject(self):
		model = getEmptyTestModel(testDbPath)
		
		with self.assertRaises(work.NoSuchProject):
			model.switchToProject(testProjectName)
		
		closeTestModel(model)

	def testGetCurrentProjectRaisesNoCurrentProject(self):
		model = getEmptyTestModel(testDbPath)

		with self.assertRaises(work.NoProjectSelected):
			model.getCurrentProject()
		
		closeTestModel(model)

	def testInsertEventWithoutSelectedProjectRaisesNoCurrentProject(self):
		model = getEmptyTestModel(testDbPath)

		with self.assertRaises(work.NoProjectSelected):
			model.insertEvent(work.Event("a",1,"message"))

		closeTestModel(model)
	
	def testInsertEventInsertsEvent(self):
		model = getEmptyTestModel(testDbPath)
		
		model.createProjectIfNotExists(testProjectName)
		model.switchToProject(testProjectName)

		testEvent = work.Event("a",1,"message")
		model.insertEvent(testEvent)
		events = model.getEventsForProject(testProjectName)
		self.assertEquals(len(events),1)
		self.assertEquals(events[0],testEvent)

		closeTestModel(model)

	def testEventEqualsItself(self):
		testEvent = work.Event("a",1,"message")
		self.assertEquals(testEvent,testEvent)

	def testEventNonEquality(self):
		self.assertNotEquals(work.Event('a',123324,'message'), work.Event('b',3223432,'dgdfgdg'))
		self.assertNotEquals(work.Event('a',123324,'message'), work.Event('a',3223432,'dgdfgdg'))
		self.assertNotEquals(work.Event('a',123324,'message'), work.Event('b',123324,'message'))
	
	def testEventEquality(self):
		self.assertEquals(work.Event('a',123324,'message'), work.Event('a',123324,'message'))
		self.assertEquals(work.Event('a',3223432,'dgdfgdg'), work.Event('a',3223432,'dgdfgdg'))
	
	def testGetEventsForProjectFiltersForProject(self):
		model = getEmptyTestModel(testDbPath)
		
		project1 = "pr1"
		project2 = "pr2"

		model.createProjectIfNotExists(project1)
		model.switchToProject(project1)
		testEvent1 = work.Event("a",1,"message")
		model.insertEvent(testEvent1)

		model.createProjectIfNotExists(project2)
		model.switchToProject(project2)
		testEvent2 = work.Event("b",2,"message2")
		testEvent3 = work.Event("c",3,"message4")
		model.insertEvent(testEvent2)
		model.insertEvent(testEvent3)

		events1 = model.getEventsForProject(project1)
		events2 = model.getEventsForProject(project2)
		self.assertEquals(len(events1),1)
		self.assertEquals(len(events2),2)
		self.assertEquals(events1[0],testEvent1)

		# test that multiple Events are in timestamp ascending order
		self.assertEquals(events2[0],testEvent2)
		self.assertEquals(events2[1],testEvent3)
	
	def testGenerateNoSessionsFromNoEvents(self):
		result = work.Session.sessionListFromEventList([])
		self.assertEquals(len(result),0)

class WorkHardSwitchProjectCommandTest(unittest.TestCase):

	# Adatbazisban levo projectek: 0db                  1db+               
	# on <semmi>                   Uzenet+Help          Listaz         
	# on <nem letezo project>      Uzenet+Help          Hibauzenet+Listaz     
	# on <letezo project>          -                    Switch

	def testOnInputReturnsSwitchCommand(self):
		c = work.parseArguments(["work","on"])
		self.assertEqual(c.__class__,work.SwitchCommand)

	def testSwitchCommand(self):

class WorkHardTest(unittest.TestCase):

	def testInvalidInputThrowInvalidInputException(self):
		with self.assertRaises(work.InvalidInput):
			work.parseArguments(["work","cafff"])
	
	def testEmptyInputReturnsHelpCommand(self):
		c = work.parseArguments(["work"])
		self.assertEqual(c.__class__,work.HelpCommand)

	def testHelpInputReturnsHelpCommand(self):
		c = work.parseArguments(["work","help"])
		self.assertEqual(c.__class__,work.HelpCommand)
	
	def testGenerateOneSessionsFromTwoEvents(self):
		eventList = generateEventList([
			("start",""),
			("stop",""),
		])

		result = work.Session.sessionListFromEventList(eventList)
		
		self.assertEquals(len(result),1)
		self.assertEquals(result[0].startEvent,eventList[0])
		self.assertEquals(result[0].stopEvent,eventList[1])
	
	def testGenerateTwoSessionsFromOneAndAHalf(self):
		eventList = generateEventList([
			("start",""),
			("stop",""),
			("start",""),
		])

		result = work.Session.sessionListFromEventList(eventList)

		self.assertEquals(len(result),2)
		self.assertEquals(result[0].startEvent,eventList[0])
		self.assertEquals(result[0].stopEvent,eventList[1])
		self.assertEquals(result[1].startEvent,eventList[2])
		self.assertIsNone(result[1].stopEvent)

	def testGenerateTwoSessions(self):
		eventList = generateEventList([
			("start",""),
			("stop",""),
			("start",""),
			("stop",""),
		])

		result = work.Session.sessionListFromEventList(eventList)

		self.assertEquals(len(result),2)
		self.assertEquals(result[0].startEvent,eventList[0])
		self.assertEquals(result[0].stopEvent,eventList[1])
		self.assertEquals(result[1].startEvent,eventList[2])
		self.assertEquals(result[1].stopEvent,eventList[3])

	def testGenerateTwoSessions(self):
		eventList = generateEventList([
			("start",""),
			("note","testNote"),
			("stop",""),
		])

		result = work.Session.sessionListFromEventList(eventList)

		self.assertEquals(len(result),1)
		self.assertEquals(result[0].startEvent,eventList[0])
		self.assertEquals(result[0].stopEvent,eventList[2])
		self.assertEquals(len(result[0].events),3)
	
	def testSessionGenerationInsonsistency(self):
		with self.assertRaises(work.InconsistentEventList):
			eventList = generateEventList([
				("stop",""),
			])
			result = work.Session.sessionListFromEventList(eventList)

		with self.assertRaises(work.InconsistentEventList):
			eventList = generateEventList([
				("start",""),
				("stop",""),
				("stop",""),
			])
			result = work.Session.sessionListFromEventList(eventList)
		
		with self.assertRaises(work.InconsistentEventList):
			eventList = generateEventList([
				("start",""),
				("start",""),
				("stop",""),
			])
			result = work.Session.sessionListFromEventList(eventList)

		with self.assertRaises(work.InconsistentEventList):
			eventList = generateEventList([
				("start",""),
				("stop",""),
				("note",""),
			])
			result = work.Session.sessionListFromEventList(eventList)
		

if __name__ == '__main__':
	unittest.main()