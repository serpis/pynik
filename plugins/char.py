#-*- coding: iso-8859-1 -*-
import sys
from commands import Command

chars = [{'dec':'32', 'oct':'040', 'hex':'20', 'bin':'00100000', 'symbol':'&nbsp;', 'html':'&#32;', 'desc':'Space'},
{'dec':'33', 'oct':'041', 'hex':'21', 'bin':'00100001', 'symbol':'!', 'html':'&#33;', 'desc':'Exclamation mark'},
{'dec':'34', 'oct':'042', 'hex':'22', 'bin':'00100010', 'symbol':'\"', 'html':'&#34;', 'desc':'Double quotes (or speech marks)'},
{'dec':'35', 'oct':'043', 'hex':'23', 'bin':'00100011', 'symbol':'#', 'html':'&#35;', 'desc':'Number'},
{'dec':'36', 'oct':'044', 'hex':'24', 'bin':'00100100', 'symbol':'$', 'html':'&#36;', 'desc':'Dollar'},
{'dec':'37', 'oct':'045', 'hex':'25', 'bin':'00100101', 'symbol':'%', 'html':'&#37;', 'desc':'Percent sign'},
{'dec':'38', 'oct':'046', 'hex':'26', 'bin':'00100110', 'symbol':'&', 'html':'&#38;', 'desc':'Ampersand'},
{'dec':'39', 'oct':'047', 'hex':'27', 'bin':'00100111', 'symbol':'\'', 'html':'&#39;', 'desc':'Single quote'},
{'dec':'40', 'oct':'050', 'hex':'28', 'bin':'00101000', 'symbol':'(', 'html':'&#40;', 'desc':'Open parenthesis (or open bracket)'},
{'dec':'41', 'oct':'051', 'hex':'29', 'bin':'00101001', 'symbol':')', 'html':'&#41;', 'desc':'Close parenthesis (or close bracket)'},
{'dec':'42', 'oct':'052', 'hex':'2A', 'bin':'00101010', 'symbol':'*', 'html':'&#42;', 'desc':'Asterisk'},
{'dec':'43', 'oct':'053', 'hex':'2B', 'bin':'00101011', 'symbol':'+', 'html':'&#43;', 'desc':'Plus'},
{'dec':'44', 'oct':'054', 'hex':'2C', 'bin':'00101100', 'symbol':',', 'html':'&#44;', 'desc':'Comma'},
{'dec':'45', 'oct':'055', 'hex':'2D', 'bin':'00101101', 'symbol':'-', 'html':'&#45;', 'desc':'Hyphen'},
{'dec':'46', 'oct':'056', 'hex':'2E', 'bin':'00101110', 'symbol':'.', 'html':'&#46;', 'desc':'Period, dot or full stop'},
{'dec':'47', 'oct':'057', 'hex':'2F', 'bin':'00101111', 'symbol':'/', 'html':'&#47;', 'desc':'Slash or divide'},
{'dec':'48', 'oct':'060', 'hex':'30', 'bin':'00110000', 'symbol':'0', 'html':'&#48;', 'desc':'Zero'},
{'dec':'49', 'oct':'061', 'hex':'31', 'bin':'00110001', 'symbol':'1', 'html':'&#49;', 'desc':'One'},
{'dec':'50', 'oct':'062', 'hex':'32', 'bin':'00110010', 'symbol':'2', 'html':'&#50;', 'desc':'Two'},
{'dec':'51', 'oct':'063', 'hex':'33', 'bin':'00110011', 'symbol':'3', 'html':'&#51;', 'desc':'Three'},
{'dec':'52', 'oct':'064', 'hex':'34', 'bin':'00110100', 'symbol':'4', 'html':'&#52;', 'desc':'Four'},
{'dec':'53', 'oct':'065', 'hex':'35', 'bin':'00110101', 'symbol':'5', 'html':'&#53;', 'desc':'Five'},
{'dec':'54', 'oct':'066', 'hex':'36', 'bin':'00110110', 'symbol':'6', 'html':'&#54;', 'desc':'Six'},
{'dec':'55', 'oct':'067', 'hex':'37', 'bin':'00110111', 'symbol':'7', 'html':'&#55;', 'desc':'Seven'},
{'dec':'56', 'oct':'070', 'hex':'38', 'bin':'00111000', 'symbol':'8', 'html':'&#56;', 'desc':'Eight'},
{'dec':'57', 'oct':'071', 'hex':'39', 'bin':'00111001', 'symbol':'9', 'html':'&#57;', 'desc':'Nine'},
{'dec':'58', 'oct':'072', 'hex':'3A', 'bin':'00111010', 'symbol':':', 'html':'&#58;', 'desc':'Colon'},
{'dec':'59', 'oct':'073', 'hex':'3B', 'bin':'00111011', 'symbol':';', 'html':'&#59;', 'desc':'Semicolon'},
{'dec':'60', 'oct':'074', 'hex':'3C', 'bin':'00111100', 'symbol':'<', 'html':'&#60;', 'desc':'Less than (or open angled bracket)'},
{'dec':'61', 'oct':'075', 'hex':'3D', 'bin':'00111101', 'symbol':'=', 'html':'&#61;', 'desc':'Equals'},
{'dec':'62', 'oct':'076', 'hex':'3E', 'bin':'00111110', 'symbol':'>', 'html':'&#62;', 'desc':'Greater than (or close angled bracket)'},
{'dec':'63', 'oct':'077', 'hex':'3F', 'bin':'00111111', 'symbol':'?', 'html':'&#63;', 'desc':'Question mark'},
{'dec':'64', 'oct':'100', 'hex':'40', 'bin':'01000000', 'symbol':'@', 'html':'&#64;', 'desc':'At symbol'},
{'dec':'65', 'oct':'101', 'hex':'41', 'bin':'01000001', 'symbol':'A', 'html':'&#65;', 'desc':'Uppercase A'},
{'dec':'66', 'oct':'102', 'hex':'42', 'bin':'01000010', 'symbol':'B', 'html':'&#66;', 'desc':'Uppercase B'},
{'dec':'67', 'oct':'103', 'hex':'43', 'bin':'01000011', 'symbol':'C', 'html':'&#67;', 'desc':'Uppercase C'},
{'dec':'68', 'oct':'104', 'hex':'44', 'bin':'01000100', 'symbol':'D', 'html':'&#68;', 'desc':'Uppercase D'},
{'dec':'69', 'oct':'105', 'hex':'45', 'bin':'01000101', 'symbol':'E', 'html':'&#69;', 'desc':'Uppercase E'},
{'dec':'70', 'oct':'106', 'hex':'46', 'bin':'01000110', 'symbol':'F', 'html':'&#70;', 'desc':'Uppercase F'},
{'dec':'71', 'oct':'107', 'hex':'47', 'bin':'01000111', 'symbol':'G', 'html':'&#71;', 'desc':'Uppercase G'},
{'dec':'72', 'oct':'110', 'hex':'48', 'bin':'01001000', 'symbol':'H', 'html':'&#72;', 'desc':'Uppercase H'},
{'dec':'73', 'oct':'111', 'hex':'49', 'bin':'01001001', 'symbol':'I', 'html':'&#73;', 'desc':'Uppercase I'},
{'dec':'74', 'oct':'112', 'hex':'4A', 'bin':'01001010', 'symbol':'J', 'html':'&#74;', 'desc':'Uppercase J'},
{'dec':'75', 'oct':'113', 'hex':'4B', 'bin':'01001011', 'symbol':'K', 'html':'&#75;', 'desc':'Uppercase K'},
{'dec':'76', 'oct':'114', 'hex':'4C', 'bin':'01001100', 'symbol':'L', 'html':'&#76;', 'desc':'Uppercase L'},
{'dec':'77', 'oct':'115', 'hex':'4D', 'bin':'01001101', 'symbol':'M', 'html':'&#77;', 'desc':'Uppercase M'},
{'dec':'78', 'oct':'116', 'hex':'4E', 'bin':'01001110', 'symbol':'N', 'html':'&#78;', 'desc':'Uppercase N'},
{'dec':'79', 'oct':'117', 'hex':'4F', 'bin':'01001111', 'symbol':'O', 'html':'&#79;', 'desc':'Uppercase O'},
{'dec':'80', 'oct':'120', 'hex':'50', 'bin':'01010000', 'symbol':'P', 'html':'&#80;', 'desc':'Uppercase P'},
{'dec':'81', 'oct':'121', 'hex':'51', 'bin':'01010001', 'symbol':'Q', 'html':'&#81;', 'desc':'Uppercase Q'},
{'dec':'82', 'oct':'122', 'hex':'52', 'bin':'01010010', 'symbol':'R', 'html':'&#82;', 'desc':'Uppercase R'},
{'dec':'83', 'oct':'123', 'hex':'53', 'bin':'01010011', 'symbol':'S', 'html':'&#83;', 'desc':'Uppercase S'},
{'dec':'84', 'oct':'124', 'hex':'54', 'bin':'01010100', 'symbol':'T', 'html':'&#84;', 'desc':'Uppercase T'},
{'dec':'85', 'oct':'125', 'hex':'55', 'bin':'01010101', 'symbol':'U', 'html':'&#85;', 'desc':'Uppercase U'},
{'dec':'86', 'oct':'126', 'hex':'56', 'bin':'01010110', 'symbol':'V', 'html':'&#86;', 'desc':'Uppercase V'},
{'dec':'87', 'oct':'127', 'hex':'57', 'bin':'01010111', 'symbol':'W', 'html':'&#87;', 'desc':'Uppercase W'},
{'dec':'88', 'oct':'130', 'hex':'58', 'bin':'01011000', 'symbol':'X', 'html':'&#88;', 'desc':'Uppercase X'},
{'dec':'89', 'oct':'131', 'hex':'59', 'bin':'01011001', 'symbol':'Y', 'html':'&#89;', 'desc':'Uppercase Y'},
{'dec':'90', 'oct':'132', 'hex':'5A', 'bin':'01011010', 'symbol':'Z', 'html':'&#90;', 'desc':'Uppercase Z'},
{'dec':'91', 'oct':'133', 'hex':'5B', 'bin':'01011011', 'symbol':'[', 'html':'&#91;', 'desc':'Opening bracket'},
{'dec':'92', 'oct':'134', 'hex':'5C', 'bin':'01011100', 'symbol':'\\', 'html':'&#92;', 'desc':'Backslash'},
{'dec':'93', 'oct':'135', 'hex':'5D', 'bin':'01011101', 'symbol':']', 'html':'&#93;', 'desc':'Closing bracket'},
{'dec':'94', 'oct':'136', 'hex':'5E', 'bin':'01011110', 'symbol':'^', 'html':'&#94;', 'desc':'Caret - circumflex'},
{'dec':'95', 'oct':'137', 'hex':'5F', 'bin':'01011111', 'symbol':'_', 'html':'&#95;', 'desc':'Underscore'},
{'dec':'96', 'oct':'140', 'hex':'60', 'bin':'01100000', 'symbol':'`', 'html':'&#96;', 'desc':'Grave accent'},
{'dec':'97', 'oct':'141', 'hex':'61', 'bin':'01100001', 'symbol':'a', 'html':'&#97;', 'desc':'Lowercase a'},
{'dec':'98', 'oct':'142', 'hex':'62', 'bin':'01100010', 'symbol':'b', 'html':'&#98;', 'desc':'Lowercase b'},
{'dec':'99', 'oct':'143', 'hex':'63', 'bin':'01100011', 'symbol':'c', 'html':'&#99;', 'desc':'Lowercase c'},
{'dec':'100', 'oct':'144', 'hex':'64', 'bin':'01100100', 'symbol':'d', 'html':'&#100;', 'desc':'Lowercase d'},
{'dec':'101', 'oct':'145', 'hex':'65', 'bin':'01100101', 'symbol':'e', 'html':'&#101;', 'desc':'Lowercase e'},
{'dec':'102', 'oct':'146', 'hex':'66', 'bin':'01100110', 'symbol':'f', 'html':'&#102;', 'desc':'Lowercase f'},
{'dec':'103', 'oct':'147', 'hex':'67', 'bin':'01100111', 'symbol':'g', 'html':'&#103;', 'desc':'Lowercase g'},
{'dec':'104', 'oct':'150', 'hex':'68', 'bin':'01101000', 'symbol':'h', 'html':'&#104;', 'desc':'Lowercase h'},
{'dec':'105', 'oct':'151', 'hex':'69', 'bin':'01101001', 'symbol':'i', 'html':'&#105;', 'desc':'Lowercase i'},
{'dec':'106', 'oct':'152', 'hex':'6A', 'bin':'01101010', 'symbol':'j', 'html':'&#106;', 'desc':'Lowercase j'},
{'dec':'107', 'oct':'153', 'hex':'6B', 'bin':'01101011', 'symbol':'k', 'html':'&#107;', 'desc':'Lowercase k'},
{'dec':'108', 'oct':'154', 'hex':'6C', 'bin':'01101100', 'symbol':'l', 'html':'&#108;', 'desc':'Lowercase l'},
{'dec':'109', 'oct':'155', 'hex':'6D', 'bin':'01101101', 'symbol':'m', 'html':'&#109;', 'desc':'Lowercase m'},
{'dec':'110', 'oct':'156', 'hex':'6E', 'bin':'01101110', 'symbol':'n', 'html':'&#110;', 'desc':'Lowercase n'},
{'dec':'111', 'oct':'157', 'hex':'6F', 'bin':'01101111', 'symbol':'o', 'html':'&#111;', 'desc':'Lowercase o'},
{'dec':'112', 'oct':'160', 'hex':'70', 'bin':'01110000', 'symbol':'p', 'html':'&#112;', 'desc':'Lowercase p'},
{'dec':'113', 'oct':'161', 'hex':'71', 'bin':'01110001', 'symbol':'q', 'html':'&#113;', 'desc':'Lowercase q'},
{'dec':'114', 'oct':'162', 'hex':'72', 'bin':'01110010', 'symbol':'r', 'html':'&#114;', 'desc':'Lowercase r'},
{'dec':'115', 'oct':'163', 'hex':'73', 'bin':'01110011', 'symbol':'s', 'html':'&#115;', 'desc':'Lowercase s'},
{'dec':'116', 'oct':'164', 'hex':'74', 'bin':'01110100', 'symbol':'t', 'html':'&#116;', 'desc':'Lowercase t'},
{'dec':'117', 'oct':'165', 'hex':'75', 'bin':'01110101', 'symbol':'u', 'html':'&#117;', 'desc':'Lowercase u'},
{'dec':'118', 'oct':'166', 'hex':'76', 'bin':'01110110', 'symbol':'v', 'html':'&#118;', 'desc':'Lowercase v'},
{'dec':'119', 'oct':'167', 'hex':'77', 'bin':'01110111', 'symbol':'w', 'html':'&#119;', 'desc':'Lowercase w'},
{'dec':'120', 'oct':'170', 'hex':'78', 'bin':'01111000', 'symbol':'x', 'html':'&#120;', 'desc':'Lowercase x'},
{'dec':'121', 'oct':'171', 'hex':'79', 'bin':'01111001', 'symbol':'y', 'html':'&#121;', 'desc':'Lowercase y'},
{'dec':'122', 'oct':'172', 'hex':'7A', 'bin':'01111010', 'symbol':'z', 'html':'&#122;', 'desc':'Lowercase z'},
{'dec':'123', 'oct':'173', 'hex':'7B', 'bin':'01111011', 'symbol':'{', 'html':'&#123;', 'desc':'Opening brace'},
{'dec':'124', 'oct':'174', 'hex':'7C', 'bin':'01111100', 'symbol':'|', 'html':'&#124;', 'desc':'Vertical bar'},
{'dec':'125', 'oct':'175', 'hex':'7D', 'bin':'01111101', 'symbol':'}', 'html':'&#125;', 'desc':'Closing brace'},
{'dec':'126', 'oct':'176', 'hex':'7E', 'bin':'01111110', 'symbol':'~', 'html':'&#126;', 'desc':'Equivalency sign - tilde'},
{'dec':'127', 'oct':'177', 'hex':'7F', 'bin':'01111111', 'symbol':'', 'html':'&#127;', 'desc':'Delete'},
]

def find_symbol(symbol):
	if len(symbol) > 1:
		return "Only one character, please."
	dec = ord(symbol)
	for char in chars:
		if int(char['dec']) == dec:
			return char_print(char)
	return "Symbol not found in table."

def char_print(char):
	return "%s (%s) - BIN: %s HEX: %s HTML: %s DEC: %s OCT: %s" % (char['desc'], char['symbol'], char['bin'], char['hex'], char['html'], char['dec'], char['oct'])

class CharCommand(Command):
    def trig_char(self, bot, source, target, trigger, argument):
		if argument:
			return find_symbol(argument)
		else:
			return "No argument."

# Testing
#symbol = sys.argv[1]
#print find_symbol(symbol)