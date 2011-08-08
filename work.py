from model import *

class Command():
	pass

class HelpCommand(Command):
	pass

class SwitchCommand(Command):
	pass

def parseArguments(argv):
	if len(argv) == 1:
		return HelpCommand()
	if argv[1] == "help":
		return HelpCommand()
	if argv[1] == "on":
		return SwitchCommand()
	raise InvalidInput()
	
if __name__=='__main__':
	pass