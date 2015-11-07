#    Logs.tf averager
#    Copyright (C) 2015  Octavio Garcia Aguirre
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
__author__ = 'otton'
import json
import requests
from enum import Enum
class steamtype(Enum):
    error = 0
    steamid = 1
    steamid3 = 2
    steamid64 = 3

def getjson(steamid):#accepts only id64
    return json.loads(requests.get("http://logs.tf/json_search?&player="+str(steamid)).content.decode())
def getmatchjson(logid):
    return json.loads(requests.get("http://logs.tf/json/"+str(logid)).content.decode())

def idtoid64(steamid):#STEAM_0:A:B
    A = int(steamid[8:9])
    B = int(steamid[10:])
    return 76561197960265728 + (B*2) + A
def id3toid64(steamid3):#[U:1:B*2+A]
    B_TIMES_2_PLUS_A=int(steamid3[5:len(steamid3)-1])
    return 76561197960265728 + B_TIMES_2_PLUS_A

def idtoid3(steamid):
    A = int(steamid[8:9])
    B = int(steamid[10:])
    return "[U:1:"+(B*2+A).__str__()+"]"

def id64toid3(steamid):
    return "[U:1:"+steamid-76561197960265728+"]"

def id3toid(steamid):
    B_TIMES_2_PLUS_A=int(steamid[5:len(steamid)-1])
    A=B_TIMES_2_PLUS_A%2
    B=(B_TIMES_2_PLUS_A-A)/2
    return "STEAM_0:"+A.__str__()+":"+B.__str__()
def id64toid(steamid):
    B_TIMES_2_PLUS_A=int(steamid)-76561197960265728
    A=B_TIMES_2_PLUS_A%2
    B=(B_TIMES_2_PLUS_A-A)/2
    return "STEAM_0:"+A.__str__()+":"+B.__str__()

def steamIdType(steamid):
    type=steamtype.error
    if steamid[:8]=="STEAM_0:":
        type=steamtype.steamid
    elif steamid[:5]=="[U:1:":
        type=steamtype.steamid3
    elif steamid.isdigit():
        type=steamtype.steamid64
    return type

class statistic:
    def __init__(self):
        self.sum=0
        self.squared_sum=0
        self.n=0

    def __repr__(self):
        return self.__dict__
    def __str__(self):
        return "sum="+self.sum.__str__()+" squared_sum="+self.squared_sum.__str__()+" n="+self.n.__str__()
class class_information:
    def __init__(self,classname="Default"):
        self.classname=classname
        self.kills=statistic()
        self.deaths=statistic()
        self.assists=statistic()
        self.dpm=statistic()

    def __repr__(self):
        return self.__dict__.__str__()
    def __str__(self):
        return "class=("+self.classname+") kills=("+self.kills.__str__()+") deaths=("+\
            self.deaths.__str__()+") assists=("+self.assists.__str__()+") dpm=("+\
            self.dpm.__str__()+")"

if __name__=='__main__':
    import sys
    import datetime
    import time

    if(len(sys.argv)==1):
        exit()
    steamid=sys.argv[1]
    date_begin=0
    date_end=int(time.time())
    debug=False
    if(len(sys.argv)>=4):
        date_begin=time.mktime(datetime.datetime.strptime(sys.argv[2],'%d/%m/%Y').timetuple())
        date_end=time.mktime(datetime.datetime.strptime(sys.argv[3],'%d/%m/%Y').timetuple())
        if(len(sys.argv)>=5):
            debug=sys.argv[4]=="debug"

        if debug:
            print("Begin")
            print(date_begin)
            print("End")
            print(date_end)
    type=steamIdType(steamid)
    if type==steamtype.error:
        print("Steamid format is wrong",file=sys.stderr)
        exit(0)
    if type==steamtype.steamid:
        pass
    elif type==steamtype.steamid3:
        steamid=id3toid(steamid)
    elif type==steamtype.steamid64:
        steamid=id64toid(steamid)

    steamid3=idtoid3(steamid)
    steamid64=idtoid64(steamid)

    if debug:
        print(steamid)
        print(steamid3)
        print(steamid64)



    steamid3=idtoid3(steamid)

    playerjson=getjson(steamid)


    dict={}
    dict["scout"]=class_information("scout")
    dict["soldier"]=class_information("soldier")
    dict["pyro"]=class_information("pyro")
    dict["demoman"]=class_information("demoman")
    dict["heavyweapons"]=class_information("heavyweapons")
    dict["engineer"]=class_information("engineer")
    dict["medic"]=class_information("medic")
    dict["sniper"]=class_information("sniper")
    dict["spy"]=class_information("spy")


    completed=0
    for i in playerjson["logs"]:
        i_id = i["id"]
        i_date = i["date"]
        print("Looking at "+str(i_id), file=sys.stderr)
        print("Date "+datetime.datetime.fromtimestamp(int(i_date)).strftime('%Y-%m-%d %H:%M:%S'),file=sys.stderr)

        if(i_date>date_end):
            print("Above the date limit, passing",file=sys.stderr)
            continue

        if(i_date<date_begin):
            print("Under the date limit, stopping",file=sys.stderr)
            break

        match=getmatchjson(i_id)
        idconverted=steamid
        for id in match["players"]:#we dont really loop through we just need 1 element to check what type the log uses
            match_id_type=steamIdType(id)
            if match_id_type==steamtype.steamid:
                idconverted=steamid
            elif match_id_type==steamtype.steamid3:
                idconverted=steamid3
            elif match_id_type==steamtype.steamid64:
                idconverted=steamid64
            else:
                print("Log Corrupted")
                exit(1)
            break

        stats=match["players"][idconverted]
        for stat in stats["class_stats"]:

            class_name=stat["type"]
            if class_name=="unknown" or class_name=="undefined":
                continue

            kills=int(stat["kills"])
            deaths=int(stat["deaths"])
            assists=int(stat["assists"])
            n=float(stat["total_time"])/match["length"] #add the % of played time, againts the full match time

            dict[class_name].kills.sum+=kills
            dict[class_name].kills.squared_sum+=kills*kills
            dict[class_name].kills.n+=n #amount of matches played with that class

            dict[class_name].deaths.sum+=deaths
            dict[class_name].deaths.squared_sum+=deaths*deaths
            dict[class_name].deaths.n+=n

            dict[class_name].assists.sum+=assists
            dict[class_name].assists.squared_sum+=assists*assists
            dict[class_name].assists.n+=n

            if int(stat["total_time"])==0:#if you use a class less than a second we get a division by zero
                continue
            dpm=int(stat["dmg"])/int(stat["total_time"])
            dpm*=60
            dict[class_name].dpm.sum+=dpm
            dict[class_name].dpm.squared_sum+=dpm*dpm
            dict[class_name].dpm.n+=n

        print("completed "+completed.__str__()+" of "+playerjson["results"].__str__(),file=sys.stderr)
        completed+=1

    print("{")
    first=True
    for i in dict:
        if not first:
            print(",")
        else:
            first=False

        print("\""+i+"\":{")
        print("\"kills\":")
        print(json.dumps(dict[i].kills.__dict__))
        print(",")

        print("\"deaths\":")
        print(json.dumps(dict[i].deaths.__dict__))
        print(",")
        print("\"assists\":")
        print(json.dumps(dict[i].assists.__dict__))
        print(",")
        print("\"dpm\":")
        print(json.dumps(dict[i].dpm.__dict__))

        print("}")
    print("}")
