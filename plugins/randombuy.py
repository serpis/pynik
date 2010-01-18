# -*- coding: latin-1 -*-

# Plugin created by Merola

import re
import utility
from commands import Command

def random_product_list_dealextreme():
	# Fetch the web page
	response = utility.read_url("http://www.dealextreme.com/products.dx/random.gadgets")
	data = response["data"].replace("\r\n", "")
	
	result = []
	
	product_pattern = "\<a href='\/details.dx\/sku.(\d+)' style=\" font-family: Verdana; font-size: 9pt;\"\>\s+(.+?)\s+\<\/a\>" + \
			".+?" + "style=\"font-size: 11pt;\"\>\s+\$(\d+\.\d\d)\s+\<\/font\>"
	product_iterator = re.finditer(product_pattern, data)
	
	for match in product_iterator:
		result.append(match.groups([1, 2, 3])) # [sku, title, price]
	
	return result

def random_product_dealextreme(min_price, max_price, hardcore, removal_filter):
	conversion_rate = utility.currency_conversion(1, 'usd', 'sek')
	if conversion_rate == None:
		return "Ajdå, nu gick något fel :("
	
	#print "debug: " + str(conversion_rate) + " " + str(min_price) + " " + str(max_price) + " " + str(hardcore)
	
	products = random_product_list_dealextreme()
	result_diff = 0
	result_product = None
	
	if min_price == max_price:
		# OK, let's try to find the closest match...
		
		closest_diff = 10000000000000000000000000000000000000
		closest_product = None
		
		for product in products:
			if (not removal_filter) or (not re.match(removal_filter, product[1].lower())):
				diff = float(product[2]) * conversion_rate - min_price
				if abs(diff) < abs(closest_diff):
					closest_diff = diff
					closest_product = product
		
		if closest_product:
			result_diff = closest_diff
			result_product = closest_product
		else:
			return "Hmm, ingen produkt var närmast din önskade kostnad :S"
	
	else:
		# We have an interval to match against.
		
		for product in products:
			if (not removal_filter) or (not re.match(removal_filter, product[1].lower())):
				cost = float(product[2]) * conversion_rate
				if min_price <= cost and cost <= max_price:
					result_diff = cost - max_price
					result_product = product
					break
		
		if not result_product:
			return "Ingen produkt med lagom pris hittades, ändra dina krav eller försök igen!"
	
	diff_string = str(round(result_diff, 2))
	if result_diff > 0:
		diff_string = "+" + diff_string
	
	if hardcore:
		return "Köööööp! http://www.dealextreme.com/shoppingcart.dx/add." + result_product[0] + "~quantity.1#_ctl0_content_pCheckout (" + diff_string + " SEK i förhållande till maxpris)"
	else:
		return "$" + result_product[2] + ": " + result_product[1] + " | " + diff_string + " SEK i förhållande till maxpris | http://www.dealextreme.com/details.dx/sku." + result_product[0]

class RandomBuyCommand(Command):
	usage = "Användning: .köp <maxkostnad>|<intervall>|=<ungefärlig kostnad> | Många 'ö' ger direktlänk till kassan med produkt tillagd, istället för produktdetaljer. Kostnader anges i hela svenska kronor!"
	
	def __init__(self):
		pass
		
	def on_privmsg(self, bot, source, target, message):
		m = re.match(r'\.k((ö|Ã¶)+)p(.*)', message)
		if not m:
			return # Not a trigger
		
		# Collect arguments
		args = [m.group(1), m.group(3).strip()]
		
		# Show usage
		if not args[1]:
			bot.tell(target, self.usage)
			return
		
		m = re.match(r'(((\d+)-(\d+))|(\d+)|=(\d+))(!?)', args[1])
		if m:
			if m.group(2):
				min_price = int(m.group(3))
				max_price = int(m.group(4))
			elif m.group(5):
				min_price = 0
				max_price = int(m.group(5))
			elif m.group(6):
				min_price = int(m.group(6))
				max_price = min_price
			else:
				bot.tell(target, "Ojoj, nu gick det fel igen :(")
			
			if m.group(7):
				removal_filter = ".*batter(y|ies).*"
			else:
				removal_filter = None
			
		else:
			bot.tell(target, "Hörru, så gör man inte! " + self.usage)
		
		# Length varies depending on encoding, so this is not a good way to do it
		hardcore = (len(args[0]) > 3)
		
		# Randomize from dealextreme.com
		result = random_product_dealextreme(min_price, max_price, hardcore, removal_filter)
		
		# Tell the appropriate target
		if target[0] == '#':
			bot.tell(target, result)
		else:
			bot.tell(source, result)
		
