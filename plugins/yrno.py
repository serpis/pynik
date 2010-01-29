# coding: iso-8859-1
import re
import utility
import string
import os
import pickle
import urllib2
from datetime import datetime
from commands import Command

# .yr location => next X hours forecast
# .yr location hour/date => forecast "overview", ie next 3 days
# .yrltf location/lat,long => long term forecast

class YrNo(Command):
    places = {}

    def trig_yr(self, bot, source, target, trigger, argument, network, **kwargs):
        """ yr.no usage: location, [hour/date/"today"] """

        argument = self.iso2utf8(argument)

        # Ugly hack FIXME
        import signal
        signal.alarm(20)                

        if not argument:
            if source in self.places:
                argument = self.places[source]
            else:
                argument = 'ryd'

        args = argument.split(",")
        if len(args) > 1:
            return "Not implemented, insert more beer"

        self.places[source] = argument
        self.save()

        # Search for town
        url = "http://www.yr.no/soek.aspx?sted=" + urllib2.quote(args[0])
        request = urllib2.Request(url)
        request.add_header("Cookie", "brp=spr=eng")
        response = urllib2.urlopen(request)

        #print response.geturl()

        if response.geturl().find("http://www.yr.no/soek.aspx?sted=") != -1:
            search = re.search('<a href="(/place/[^"]*)" title="[^"]*">', response.read())
            if search:
                url = "http://www.yr.no" + urllib2.quote(search.group(1))
                #print url
                request = urllib2.Request(url)
                request.add_header("Cookie", "brp=spr=eng")
                response = urllib2.urlopen(request)

                #print response.geturl()
            else:
                return "Could not find any such place. Maybe you should move?"
        
        # Parse overview page
        stedbaseurl = response.geturl()
        
        # Get Hour by Hour view
        url = stedbaseurl + "hour_by_hour.html"
        response = urllib2.urlopen(url)

        #print stedbaseurl

        search = re.search('\/([^\/]*)\/$', stedbaseurl)
        if search:
            town = urllib2.unquote(search.group(1))
        else:
            town = "unknown"
     
        data = response.read()
        ofset = 0
        hbh = {}
        lhbh = []

        for i in range(1, 100):
            search = re.search('<th>([^ ]*) <strong>([^<]*)</strong></th>', data[ofset:])
            if search:
                ofset += search.end()
                #print "'%s' '%s'" % (search.group(1), search.group(2))
                key = search.group(1) + " " + search.group(2)
                hbh[key] = {}
                hbh[key]['day'] = search.group(1)
                hbh[key]['time'] = search.group(2)

                # FIXME should add end here

                # Search for all properties
                search = re.search('<td title="([^"]*)">', data[ofset:])
                if search:
                    hbh[key]['weather'] = search.group(1)

                search = re.search('<td class="precipitation">([0-9\.]*) mm</td>', data[ofset:])
                if search:
                    hbh[key]['precipitation'] = search.group(1)

                search = re.search('<td class="(plus|minus)"[^>]*>([\-0-9]*)[^<]*</td>', data[ofset:])
                if search:
                    hbh[key]['temp'] = search.group(2)

                search = re.search('<img src="[^"]*" title="([^,]*), ([0-9]*) m/s from ([^"]*)"', data[ofset:])
                if search:
                    hbh[key]['wind'] = search.group(1)
                    hbh[key]['wind_strength'] = search.group(2)
                    hbh[key]['wind_direction'] = search.group(3)

                search = re.search('<td class="pressure">([^<]*)</td>', data[ofset:])
                if search:
                    hbh[key]['pressure'] = search.group(1)

                lhbh.append(hbh[key])
            else:
                break

        #print hbh
#        for x in hbh.items():
#            print x

        result = "Weather in %s at " % town
        for t in lhbh[:4]:
            result += "%s: %s %sC %s mm %s m/s %s " % (t["time"], t["weather"], t["temp"], t["precipitation"], t["wind_strength"], t["wind_direction"])

        # Find rain!
        rains = ""
        for t in lhbh:
            if float(t["precipitation"]) > 0.1:
                rains += "%s%s %smm " % (t["day"][:2], t["time"], t["precipitation"])

        if len(rains) != 0:
            result += "DANGER rain! " + rains

        return result

    def iso2utf8(self, s):
        try:
            return s.decode("utf-8").encode("utf-8")
        except:
            # is probably iso
            return s.decode("iso-8859-1").encode("utf-8")

    def save(self):
        try:
            f = open(os.path.join("data", "yrno.txt"), "w")
            p = pickle.Pickler(f)
            p.dump(self.places)
            f.close()
        except IOError:
            pass

    def on_load(self): 
        self.places = {}
        
        try:
            f = open(os.path.join("data", "yrno.txt"), "r") 
            unpickler = pickle.Unpickler(f)
            self.places = unpickler.load()
            f.close()
        except:
            pass
        
    def on_unload(self): 
        self.places = {}

#print YrNo().trig_yr(None, None, None, None, "Hjaltevad", None)
#print YrNo().trig_yr(None, None, None, None, "Link\xf6ping", None)
#print YrNo().trig_yr(None, None, None, None, "Link\xc3\xb6ping", None)
#print YrNo().trig_yr(None, None, None, None, "Linkoping", None)
#print YrNo().trig_yr(None, None, None, None, "Kiruna", None)
#print YrNo().trig_yr(None, None, None, None, "Uppsala", None)
