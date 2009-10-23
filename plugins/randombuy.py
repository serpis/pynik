# -*- coding: latin-1 -*-

# Plugin created by Merola

import re
import utility
from commands import Command

def random_product_dealextreme(min_price, max_price, hardcore):
	conversion_rate = utility.currency_conversion(1, 'usd', 'sek')
	if conversion_rate == None:
		return "Ajdå, nu gick något fel :("
	
	bot.tell("#botnik", "debug: " + conversion_rate + " " + min_price + " " + max_price)
	
	# Fetch the web page
	response = utility.read_url("http://www.dealextreme.com/products.dx/random.gadgets")
	data = response["data"].replace("\r\n", "")
	#data = data.replace("&nbsp;", "")
	
	product_pattern = "\<a href='\/details.dx\/sku.(\d+)' style=\" font-family: Verdana; font-size: 9pt;\"\>\s+(.+?)\s+\<\/a\>" + \
			".+?" + "style=\"font-size: 11pt;\"\>\s+\$(\d+\.\d\d)\s+\<\/font\>"
	product_iterator = re.finditer(product_pattern, data)
	
	for match in product_iterator:
		cost = float(match.group(3)) * conversion_rate
		if min_price <= cost and cost <= max_price:
			if hardcore:
				return "Köööööp! http://www.dealextreme.com/shoppingcart.dx/add." + match.group(1) + "~quantity.1#_ctl0_content_pCheckout"
			else:
				return "$" + match.group(3) + ": " + match.group(2) + " | http://www.dealextreme.com/details.dx/sku." + match.group(1)
	
	return "Ingen produkt med lagom pris hittades, ändra dina krav eller försök igen!"

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
		
		m = re.match(r'((\d+)-(\d+))|(\d+)|=(\d+)', args[1])
		if m:
			if m.group(1):
				min_price = m.group(2)
				max_price = m.group(3)
			elif m.group(4):
				min_price = 0
				max_price = m.group(4)
			elif m.group(5):
				min_price = m.group(5) - 7.5
				max_price = m.group(5) + 7.5
			else:
				bot.tell(target, "Ojoj, nu gick det fel igen :(")
		else:
			bot.tell(target, "Hörru, så gör man inte! " + self.usage)
			
		# Randomize from dealextreme.com
		
		# Length varies depending on encoding, so this is not a good way to do it
		hardcore = (len(args[0]) > 3)
		bot.tell(target, random_product_dealextreme(min_price, max_price, hardcore))
		
