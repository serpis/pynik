# coding: iso-8859-1
import re
import utility
import string
import os
import pickle
import htmllib
from datetime import datetime
from commands import Command

class Restaurant():
	next = None
	restaurants = []
	url = ""

	def __init__(self):
		pass

	def setNext(self, restaurant):
		self.next = restaurant
		return self.next

	def getFood(self, restaurant, day=None):
		if restaurant.lower() in [w.lower() for w in self.restaurants]:
			return self.fetchFood(restaurant, day)
		else:
			if self.next:
				return self.next.getFood(restaurant, day)
			else:
				return "I'm sorry Dave I don't recognize that restaurant."

	def getAllRestaurants(self):
		if self.next:
			return self.restaurants + self.next.getAllRestaurants()
		else:
			return self.restaurants

	def getAllUrls(self):
		if self.next:
			if self.url == "":
				return self.next.getAllUrls()
			else:
				return [self.url] + self.next.getAllUrls()
		else:
			return [self.url]

	def fetchFood(self, restaurant, day=None):
		return "I'm sorry Dave I don't recognize that restaurant. Hmm, should not reach this."

class Preston(Restaurant):
	restaurants = ["Husman", "Chili", "Golfinn", "Collegium", "Vallfarten"]
	url = "http://www.preston.se/dagens.html"

	def fetchFood(self, restaurant, day=None):
		if day == "today":
			return "Wiseass aren't you?"		
		elif day != None:
			return "I'm sorry Dave Preston can only handle 'today'."
		

		response = utility.read_url(self.url)
		data = response["data"]

		day = None
		week = None
		found_restaurant = None
		lunches = []
		ofset = 0

		# find week and day
		search = re.search('<h2><span class="[^"]*">([^<]*)</span>  <span class="[^"]*">vecka ([^<]*)</span></h2>', data)
		if search:
			day = search.group(1)
			week = search.group(2)

		# find lunch at restaurant
		search = re.search('id="(' + restaurant + ')"', data, re.IGNORECASE)
		end = 0
		if search:
			found_restaurant = search.group(1)
			ofset += search.end()
			
			search = re.search('</div>', data[ofset:])
			if search:
				end = ofset + search.start()

				for cnt in range(1,20):
					search = re.search("<li>([^<]*)</li>", data[ofset:])
					if search and ofset+search.end() < end:
						lunch = search.group(1).replace("&amp; ", "")
						lunches.append(lunch)
						ofset += search.end()
					else:
						break

		# create result
		result = ""
		cnt = 1
		if day != None and week != None and found_restaurant != None:
			result = "Lunch " + found_restaurant + " " + day + " v" + week + " "
			
		for lunch in lunches:
			result += str(cnt) + ": " + lunch + " "
			cnt += 1

		if result[-1:] == " ":
			result = result[:-1]

		if len(result) == 0 or len(lunches) == 0:
			return "No lunch available at %s ):" % restaurant
		else:
			return result



class Blaumesen(Restaurant):
	restaurants = ["Blåmesen"]
	url = "http://www.blamesen.se/Lunch.html"

	def fetchFood(self, restaurant, today=None):
		response = utility.read_url(self.url)
		data = response["data"]

		day = None
		week = None
		found_restaurant = "Blåmesen"
		lunches = []
		ofset = 0

		days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
		if not today:
			today = days[datetime.now().isoweekday()-1]

		data = data.replace("\r", "")
		data = re.sub("<[^>]*>", "", data)
		data = data.replace("&nbsp;", "")

		# find week
		search = re.search('Vecka ([0-9]+)', data)
		if search:
			week = search.group(1)

		# find day
		start = data.lower().find(today.lower())
		search = re.search("[^\s]*", data[start:])
		if search:
			day = data[start:start+search.end()]
		else:
			day = today

		def findFood(pattern, data):
			""" Finds food in data """
			search = re.search(pattern, data)
			if search:
				sdata = data[search.end():]
				search = re.search("\n\s*\n", sdata)
				if search:
					sdata = sdata[0:search.start()]
					sdata = re.sub("\n *", "", sdata)
					return sdata

		patterns = ["Dagens\s*rätt:\s*L?\s*", "Dagens\s*pasta:\s*L?\s*", 
			    "Dagens\s*vegetariska:\s*L?\s*",
			    "A\s*la\s*carte:\s*L?\s*", "Dagens\s*soppa:\s*L?\s*"]

		for pattern in patterns:
			food = findFood(pattern, data[start:])
			if food:
				lunches.append(food)

		# create result
		result = ""
		cnt = 1
		if day != None and week != None and found_restaurant != None:
			result = "Lunch " + found_restaurant + " " + day + " v" + week + " "
			
		for lunch in lunches:
			result += str(cnt) + ": " + lunch + " "
			cnt += 1

		if result[-1:] == " ":
			result = result[:-1]

		if len(result) == 0 or len(lunches) == 0:
			return "No lunch available at %s ):" % restaurant
		else:
			return result

class DeeJays(Restaurant):
	restaurants = ["DeeJays"]
	url = "http://www.alltomkebab.se/index.asp?eatery=31"

	def fetchFood(self, restaurant, today=None):
		if (today != None and today.lower() != "lördag" and today.lower() != "söndag") or (
			today == None and datetime.now().weekday() < 5):
			return "Kebab!! DeeJays Grillbar - Liljeholmsvägen 10, Liljeholmen, Stockholm, Sweden"
		else:
			return "Stängt ):"

class JohnBauer(Restaurant):
	restaurants = ["JB"]
	url = "http://www.johnbauer.nu/web/Restaurang_JB_1.aspx"

	def fetchFood(self, restaurant, today=None):
		response = utility.read_url(self.url)
		data = response["data"]
		
		day = None
		week = None
		lunches = []
		ofset = 0
		found_restaurant = "JB"

		days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
		if not today:
			today = days[datetime.now().isoweekday()-1]


		# find week
		search = re.search('kudden v ([0-9]+)', data)
		if search:
			week = search.group(1)

		# find day
		start = data.lower().find(today.lower())
		search = re.search("</p>", data[start:])
		day = today

		lines = data[start:start+search.end()].split("\n")
		for line in lines:
			search = re.search("&#160;(<em>)?([^<]*)<", line)
			if search:
				print search.group(2)
				lunches.append(search.group(2))


		# create result
		result = ""
		cnt = 1
		if day != None and week != None and found_restaurant != None:
			result = "Lunch " + found_restaurant + " " + day + " v" + week + " "

		for lunch in lunches:
			result += str(cnt) + ": " + lunch + " "
			cnt += 1

		if result[-1:] == " ":
			result = result[:-1]

		if len(result) == 0 or len(lunches) == 0:
			return "No lunch available at %s ):" % restaurant
		else:
			return result



class Food(Command):
	restaurants = None

	def __init__(self):
		self.restaurants = Restaurant()
		r1 = self.restaurants.setNext(Preston())
		r2 = r1.setNext(Blaumesen())
		r3 = r2.setNext(DeeJays())
		r4 = r3.setNext(JohnBauer())

	def trig_lunch(self, bot, source, target, trigger, argument, network, **kwargs):
		""" Presents food, usage: {<restaurant>,list} """
		return self.trig_food(bot, source, target, trigger, argument, network, **kwargs)
		
	def trig_food(self, bot, source, target, trigger, argument, network, **kwargs):
		""" Presents food, usage: {<restaurant>,list} """
		def usage():
			return "Try with ." + trigger + " restaurant [day], I know of: " + ", ".join(self.restaurants.getAllRestaurants())

		argument = argument.strip()
		if argument == "list":
			return "Restaurants: " + ", ".join(self.restaurants.getAllRestaurants()) + " Urls: " + ", ".join(self.restaurants.getAllUrls())
		elif argument:
			self.restaurant[source] = argument
			self.save()
		else:
			if source in self.restaurant:
				argument = self.restaurant[source]
			else:
				return usage()
		
		restaurants = argument.split(",")
		for restaurant in restaurants[0:3]:
			args = restaurant.strip().split(" ")
			data = ""
			if len(args) == 1:
				data = self.restaurants.getFood(self.utf82iso(args[0]))
			elif len(args) == 2:
				data = self.restaurants.getFood(self.utf82iso(args[0]), day=self.utf82iso(args[1]))
			else:
				data = usage()
			p = htmllib.HTMLParser(None)
			p.save_bgn()
			p.feed(data)
			bot.tell(network, target, p.save_end())

	def utf82iso(self, s):
		try:
			return s.decode("utf-8").encode("iso-8859-1")
		except:
			return s

	def save(self): 
		f = open(os.path.join("data", "food_restaurants.txt"), "w") 
		p = pickle.Pickler(f) 
		p.dump(self.restaurant) 
		f.close() 

	def on_load(self): 
		self.restaurant = {}

		try:
			f = open(os.path.join("data", "food_restaurants.txt"), "r") 
			unpickler = pickle.Unpickler(f) 
			self.restaurant = unpickler.load() 
			f.close() 
		except:
			pass

	def on_unload(self): 
		self.restaurant = {}

