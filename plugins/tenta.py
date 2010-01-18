# coding: utf-8

__author__ = 'Simon Pantzare'

from commands import Command
from urllib import urlencode, urlopen
from datetime import datetime
import sgmllib, string

class StrippingParser(sgmllib.SGMLParser):
    """**NOTE:** Borrowed from http://code.activestate.com/recipes/52281/"""

    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib
    
    def __init__(self, valid_tags=None):
        self.valid_tags = valid_tags if valid_tags is not None else ()
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = [] 
        
    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)
        
    def handle_entityref(self, name):
        if self.entitydefs.has_key(name): 
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
        self.result = "%s&%s%s" % (self.result, name, x)
    
    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:       
            self.result = self.result + '<' + tag
            for k, v in attrs:
                if string.lower(k[0:2]) != 'on' and \
                    string.lower(v[0:10]) != 'javascript':
                    self.result = '%s %s="%s"' % (self.result, k, v)
            endTag = '</%s>' % tag
            self.endTagList.insert(0,endTag)    
            self.result = self.result + '>'
                
    def unknown_endtag(self, tag):
        if tag in self.valid_tags:
            try:
                self.result = "%s</%s>" % (self.result, tag)
                remTag = '</%s>' % tag
                self.endTagList.remove(remTag)
            except ValueError:
                pass

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
                self.result = self.result + self.endTagList[j]    
        

def strip_tags(s, valid_tags=None):
    """Strip illegal HTML tags from string s"""
    parser = StrippingParser(valid_tags)
    parser.feed(s)
    parser.close()
    parser.cleanup()
    return parser.result


class TentaSearchParseError(ValueError):
    pass


class TentaSearch(object):
    
    def __init__(self, course):
            self.course = course


    def get_url(self):
        course = self.course
        base_url = 'https://www4.student.liu.se/tentasearch?'
        none_chosen = 'Ingen vald'
        args = [
            ('kurskod', course),
            ('kursnamn', ''),
            ('datum', ''),
            ('inst', none_chosen),
            ('fakultet', none_chosen),
            ('ord', none_chosen)
        ]
        return base_url + urlencode(args)
    

    def get_data(self):
        handle = urlopen(self.get_url())
        lines = handle.readlines()
        start = stop = -1

        def strip(str):
            return strip_tags(str, ('td',)) .replace('&nbsp;', '').strip()

        parse_lines = [strip(line) for line in lines if len(strip(line))]

        for i, l in zip(range(len(parse_lines)), parse_lines):
            if start != -1 and stop != -1:
                break
            if l == '<td width="*" valign="top">\n</td>':
                start = i + 2
            elif l == '<td>Kurskod</td>\t<td></td>':
                stop = i - 1
        
        if start < 0 or stop < 0:
            raise TentaSearchParseError()
        for i in (start, stop):
            try:
                parse_lines[i]
            except IndexError:
                raise TentaSearchParseError()
        
        def despace(str, char=' '):
            str = str.replace(char * 2, char)
            if str.find(char * 2) != -1:
                str = despace(str, char)
            return str

        parsed_data = []
        for line in parse_lines[start:stop]:
            line = line.replace('>', '>\t')
            line = strip_tags(line)
            for ch in [' ', '\t']:
                line = despace(line, ch)
            line = line.decode('latin1')

            parts = [p.strip() for p in line.split('\t') if len(p.strip())]
            def get_date(str):
                return datetime.strptime(str, '%Y&#45;%m&#45;%d%H')
            dates = [get_date(parts[2] + parts[i]) for i in (3, 5)]
            parts = parts[0:2] + dates + parts[6:]
            parsed_data.append(tuple(parts))
        return parsed_data


class tenta(Command):
    def __init__(self):
        pass

    def trig_tenta(self, bot, source, target, trigger, argument):
        course = argument.strip()
        if len(course) < 4:
            return "Usage: .tenta <course>"
        
        try:
            tenta_data = TentaSearch(course).get_data()
        except:
            return 'Error retrieving data.'

        if len(tenta_data):
            abbrevs = {}
            codes = {}
            for entry in tenta_data:
                (code, abbrev, start, end, _, _) = entry
                if not codes.has_key(code):
                    codes[code] = []
                    abbrevs[code] = abbrev

                date_text = start.strftime('%Y-%m-%d %H:%M')
                date_text += end.strftime('--%H:%M')
                codes[code].append(date_text)

            formatted = []
            for (code, text) in codes.iteritems():
                abbrev = abbrevs[code]
                formatted.append("%s %s: %s" % (code, abbrev, ', '.join(text)))
            
            formatted.sort()
            return ' | '.join(formatted).encode('utf-8')
        else:
            return "Nothing found."
