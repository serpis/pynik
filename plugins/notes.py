# -*- coding: utf-8 -*-

# Plugin created by Merola

import re
import utility
from commands import Command

class Notebook(Command):
	notebook = {}
	usage = "Usage: .notes show | .notes add <text> | .notes remove <number> | .notes clear"
	
	def __init__(self):
		pass

	def on_load(self):
		self.notebook = utility.load_data('notes', {})

	def set_notes(self, nick, text):
		self.notebook[nick] = text
		utility.save_data('notes', self.notebook)
		
	def get_notes(self, nick):
		return self.notebook.get(nick, [])
		
	def trig_notes(self, bot, source, target, trigger, argument):
		"""A personal notebook (one for each IRC nick). Use it to save small (non-secret) notes."""
		
		argument = argument.strip()
		args = argument.split(' ', 1)
		
		# Show usage
		if not args[0]:
			return "Your personal (but not so private) notebook! " + self.usage
				
		# Show notes
		elif args[0].lower() == 'show':
			notes = self.get_notes(source)
			
			if not notes:
				return "You have no saved notes :/"
			else:
				# Let's use some ugly code!
				index = 1
				numbered_notes = []
				
				for note in notes:
					numbered_notes.append("#" + str(index) + " " + note)
					index = index + 1
				
				return "[ " + " ][ ".join(numbered_notes) + " ]"
		
		# Add note
		elif args[0].lower() == 'add':
			if len(args) < 2:
				return "You cannot add empty notes!"
			
			notes = self.get_notes(source)
			if notes:
				maxlen = 390 - len(" ][ 99: ".join(notes)) - len("[ " + " ]")
			else:
				maxlen = 390
			
			if maxlen <= 0:
				return "No space left for more notes :("
			elif maxlen < len(args[1]):
				notes.append(args[1][:maxlen])
				self.set_notes(source, notes)
				return "Note added (but truncated): " + args[1][:maxlen]
			else:
				notes.append(args[1])
				self.set_notes(source, notes)
				return "Note successfully added: " + args[1]
		
		# Remove note
		elif args[0].lower() == 'remove':
			if len(args) < 2:
				return "You have to specify a note number!"
			elif not args[1].isdigit():
				return "That is not a number :("
			
			notes = self.get_notes(source)
			numnotes = len(notes)
			index = int(args[1])
			
			if not notes:
				return "You have no saved notes!"
			elif index > numnotes:
				return "You only have %s notes!" % numnotes
			elif index == 0:
				return "1 is the first number!"
			
			note = notes.pop(index - 1)
			self.set_notes(source, notes)
			return "Note removed: " + note
		
		# Clear all notes
		elif args[0].lower() == 'clear':
			self.set_notes(source, [])
			return "All your notes have been removed."
		
		# Unknown subcommand
		else:
			return "Unknown subcommand! " + self.usage

