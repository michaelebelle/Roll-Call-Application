from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.clock import Clock, mainthread
from functools import partial
import json
import csv, datetime, decimal, math, re, os, time
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
###Define Constants
cc = ',';
cnl = '\n';
dnl = '\r\n'
pi = math.pi;
mi2km = 1.609344;
mi2meter = 1609.344;
km2meter = 1000;
feet2meter = 0.3048
Gt = 1;
Gr = 1  # db gain of transmitter and receiver assume to 1 (no gain)
alexp = 2.75  # effective exponent of distance due to environment; 2 for free space
ERk = 6371  # earth radius in km (6371) (or in miles (3963))
ER = 3963  # earth radius in km (6371) (or in miles (3963))
DEC = ERk * pi / 180  # degree-earth-conversion factor:  111.1949266_km or 69.16739826_mile
DRC = 180 / pi  # degree-radian-conversion factor: 57.29577951
rd = "AM,FB,FL,FM,FX"  # radio service codes of radio broadcasters
tv = "CA,DC,DT,LD,TX"  # radio service codes of TV broadcasters
bc = rd + ',' + tv  # radio service codes of radio and TV broadcasters
ps = "GE,GF,GP,IQ,MW,PA,PW,SG,SL,SP,SY,WP,YE,YF,YP,YW"  # RSC of public safety group
gv = "GV"  # US Government GMF
SplittingCharacters = [' ', "'", '"', 'n', 'N', 's', 'S', 'e', 'E', 'w', 'W']
numin = lambda sn: re.search('[\d.-]+', sn)[0] if re.search('\d', sn)[0] else 0
dmsd2dd = lambda dmsd: (abs(dmsd[0]) + dmsd[1] / 60 + dmsd[2] / 3600) * dmsd[3]
data1 = data2 = data3 = data4 = data5 = data6 = data7 = data8 =  data9 = data10 = ''

def dd2dmsd(dd, lcd):
    m, s = divmod(abs(dd) * 3600, 60)
    d, m = divmod(m, 60)
    if dd >= 0:
        cd = lcd[0]
    else:
        cd = lcd[1]
    if 'N' in lcd:
        sd, sm, ss = f'{d:02.0f}', f'{m:02.0f}', f'{s:05.2f}'
    else:
        sd, sm, ss = f'{d:03.0f}', f'{m:02.0f}', f'{s:05.2f}'
    return sd, sm, ss, cd

def fduration(duration):
    ssdur = str(datetime.timedelta(seconds=duration)).split(' ')
    d = f'{int(ssdur[0]):d}d' if len(ssdur) > 1 else ''
    lhms = ssdur[-1].split(':')
    H = int(lhms[0]);
    M = int(lhms[1]);
    S = int(float(lhms[2]))
    h = f'{H:d}h' if H > 0 else ''
    m = f'{M:d}m' if M > 0 else ''
    s = f'{S:d}s' if S > 0 else ''
    return d + h + m + s


numin = lambda sn: re.search('[\d.-]+',sn)[0] if re.search('\d',sn)[0] else 0
tdata = [{'col1': 'Band Number', 'col2': 'BBF (Hz)', 'col3': 'BEF (Hz)', 'col4': 'SWD (s)', 'col5': 'SWP (0|#)', 'col6': 'RBW (Hz)', 'col7': 'Att (dB)', 'col8': 'Ref (dBm)'
          , 'col9': 'TRM', 'col10': 'Band Info'},
        {'col1': '1', 'col2': '0.521e6', 'col3': '1.709e6', 'col4': '0', 'col5': '0', 'col6': '3e2', 'col7': '0', 'col8': '-50', 'col9': 'average'
         , 'col10': 'radio AM'}, # 1
         {'col1': '2', 'col2': '87.8e6', 'col3': '108e6', 'col4': '0', 'col5': '0', 'col6': '1e3', 'col7': '0', 'col8': '-50', 'col9': 'average'
          , 'col10': 'radio FM'}, # 2
         {'col1': '3', 'col2': '162.375e6', 'col3': '162.575e6', 'col4': '0', 'col5': '0', 'col6': '1e2', 'col7': '0', 'col8': '-50', 'col9': 'average'
          , 'col10': 'NOAA NWR'}, # 3
         {'col1': '4', 'col2': '54e6', 'col3': '88e6', 'col4': '0', 'col5': '0', 'col6': '3e3', 'col7': '0', 'col8': '-50', 'col9': 'average'
          , 'col10': 'DTV VHF1'}, # 4
        {'col1': '5', 'col2': '174e6', 'col3': '216e6', 'col4': '0', 'col5': '0', 'col6': '3e3', 'col7': '0', 'col8': '-50', 'col9': 'average'
         , 'col10': 'DTV VHF1'}, # 5
        {'col1': '6', 'col2': '470e6', 'col3': '539e6', 'col4': '0', 'col5': '0', 'col6': '3e3', 'col7': '0', 'col8': '-50', 'col9': 'average'
         , 'col10': 'DTV VHF1'}, # 6
        {'col1': '7', 'col2': '539e6', 'col3': '608e6', 'col4': '0', 'col5': '0', 'col6': '3e3', 'col7': '0', 'col8': '-50', 'col9': 'average'
         , 'col10': 'DTV VHF1'}, # 7
         ]

xdata = [{'col1': 'Band Number', 'col2': 'BBF (Hz)', 'col3': 'BEF (Hz)', 'col4': 'SWD (s)', 'col5': 'SWP (0|#)', 'col6': 'RBW (Hz)', 'col7': 'Att (dB)', 'col8': 'Ref (dBm)'
          , 'col9': 'TRM', 'col10': 'Band Info'},
        {'col1': '1', 'col2': '150e6', 'col3': '174e6', 'col4': '0', 'col5': '0', 'col6': '3e3', 'col7': '0', 'col8': '-50', 'col9': 'average'
         , 'col10': 'PS 150MHz'}, # 1
         {'col1': '2', 'col2': '450e6', 'col3': '512e6', 'col4': '0', 'col5': '0', 'col6': '3e3', 'col7': '0', 'col8': '-50', 'col9': 'average'
          , 'col10': 'PS 450MHz'}, # 2
         {'col1': '3', 'col2': '758e6', 'col3': '775e6', 'col4': '0', 'col5': '0', 'col6': '3e3', 'col7': '0', 'col8': '-50', 'col9': 'average'
          , 'col10': 'PS 760MHz'}, # 3
         {'col1': '4', 'col2': '851e6', 'col3': '862e6', 'col4': '0', 'col5': '0', 'col6': '3e3', 'col7': '0', 'col8': '-50', 'col9': 'average'
          , 'col10': 'PS 850MHz'}, # 4
         ]

class Tabelle(BoxLayout):
    pass

class Table(BoxLayout):

        try:
            rcsinputs = open("rcsinputs.txt", 'w')
            rcsinputs.write(data1 + ' ' + data2 + ' '+  data3 + ' ' + data4 + ' ' + data5 + ' ' + data6 + ' ' + data7 + ' ' + data8 + ' ' + data9 + ' ' + data10)
            rcsinputs.close()
        except (RuntimeError, ValueError, TypeError, UnboundLocalError):
            content=Label(text="Get rcsbands.txt first." + "\n" + "Touch outside to dismiss.", halign='center', valign='middle')
            popup = Popup(title="Save Error", content=content, size_hint=(.6, .6)).open()


class VVScreen(Screen):
    def save(self):
        data = json.dumps(xdata)
        with open('example.json', 'w') as json_file:
            json.dump(data, json_file)


class RVScreen(Screen):

    def save(self):
        data = json.dumps(tdata)
        with open('example.json', 'w') as json_file:
            json.dump(data, json_file)






class CustomScreen(Screen):
    pass

class FirstScreen(Screen):
    def validate_input(self, sinput):
        try:
            sinput, sid = sinput.split('|||')
            sinput = sinput.strip()
            ltsin = len(sinput)
            self.ids[sid].text = sinput
            print(sinput)
            Clock.schedule_once(partial(self._refocus_textinput, sid, ltsin))
        except (RuntimeError, ValueError, TypeError):
            content = Label(text="Check the input is entered." + "\n" + "Touch outside to dismiss.", halign='center',
                            valign='middle')
            popup = Popup(title="Radius Error", content=content, size_hint=(.6, .6)).open()

    def _refocus_textinput(self, *args):
        self.ids[args[0]].cursor = (args[1], 0)
        self.ids[args[0]].get_focus_next().focus = True

    def format_radius(self, sinradius):  # convert input-radius to km; validate on enter
        try:
            sid = 'radius_input'
            sinradius = (
                re.search('[ \S]+:', sinradius)[0][:-1] if re.search('[ \S]+:', sinradius) else sinradius).strip()
            ltsin = len(sinradius)
            radius = float(numin(sinradius))
            if 'mi' in sinradius:
                radiusmi = radius
                radius *= mi2km
            else:
                radiusmi = radius / mi2km
            sinradius += f' : [{radius:0.3f} km] = {radiusmi:0.3f} miles'
            self.ids[sid].text = sinradius
            Clock.schedule_once(partial(self._refocus_textinput, sid, ltsin))
        except (RuntimeError, ValueError, TypeError):
            content = Label(text="Check that radius is entered." + "\n" + "Touch outside to dismiss.", halign='center',
                            valign='middle')
            popup = Popup(title="Radius Error", content=content, size_hint=(.6, .6)).open()

    def format_duration(self, sduration):  # checks if duration entered and in right format
        try:
            sid = 'duration_input'
            sduration = sduration.split(':', 1)[0].strip()
            ltsin = len(sduration)
            sdurations = sduration + 's'
            D = float(re.search('[\d. ]+d', sdurations)[0][:-1]) if re.search('[\d. ]+d', sdurations) else 0
            H = float(re.search('[\d. ]+h', sdurations)[0][:-1]) if re.search('[\d. ]+h', sdurations) else 0
            M = float(re.search('[\d. ]+m', sdurations)[0][:-1]) if re.search('[\d. ]+m', sdurations) else 0
            S = float(re.search('[\d. ]+s', sdurations)[0][:-1]) if re.search('[\d. ]+s', sdurations) else 0
            tduration = D * 86400 + H * 3600 + M * 60 + S
            sduration += f' : [{tduration:0.0f} seconds] = {fduration(tduration)}'
            self.ids[sid].text = sduration
            Clock.schedule_once(partial(self._refocus_textinput, sid, ltsin))
        except (AttributeError, ValueError):
            content = Label(
                text="Please ensure that 'duration' is entered and in the proper format." + "\n" + "(hrhr:minmin:secsec)" + "\n" + "Touch outside to dismiss.",
                halign='center', valign='middle')
            popup = Popup(title="Duration Error", content=content, size_hint=(.6, .6)).open()

    def save(self):
        agent = self.ids['agent_input'].text
        event = self.ids['event_input'].text
        activity = self.ids['activity_input'].text
        radius = self.ids['radius_input'].text
        duration = self.ids['duration_input'].text
        ip = self.ids['ip_input'].text
        comments = self.ids['comments_input'].text
        rcsinputs = open("rcsinputs.txt", 'w')

        rcsinputs.write("Agent: " + agent + "\n" + "Event: " + event + "\n" + "Activity: " + activity + "\n" + "Radius: " + radius + "\n" + "Duration: " + duration + "\n" + "IP: " + ip + "\n" + "Comments: " + comments + "\n")
        rcsinputs.close()








class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'spalte1_SP': str(x['col1']), 'spalte2_SP': str(x['col2']), 'spalte3_SP': str(x['col3']),
                      'spalte4_SP': str(x['col4']),'spalte5_SP': str(x['col5']), 'spalte6_SP': str(x['col6']),
                      'spalte7_SP': str(x['col7']), 'spalte8_SP': str(x['col8']), 'spalte9_SP': str(x['col9'])
                      , 'spalte10_SP': str(x['col10'])} for x in tdata]

class VV(RecycleView):
    def __init__(self, **kwargs):
        super(VV, self).__init__(**kwargs)
        self.data = [{'data1': str(x['col1']), 'data2': str(x['col2']), 'data3': str(x['col3']),
                      'data4': str(x['col4']), 'data5': str(x['col5']), 'data6': str(x['col6']),
                      'data7': str(x['col7']), 'data8': str(x['col8']), 'data9': str(x['col9'])
                         , 'data10': str(x['col10'])} for x in xdata]




class SecondScreen(Screen):
    def validate_input(self, sinput):
        try:
            sinput, sid = sinput.split('|||')
            sinput = sinput.strip()
            ltsin = len(sinput)
            self.ids[sid].text = sinput
            Clock.schedule_once(partial(self._refocus_textinput, sid, ltsin))
        except (RuntimeError, ValueError, TypeError):
            content = Label(text="Check the input is entered." + "\n" + "Touch outside to dismiss.", halign='center',
                            valign='middle')
            popup = Popup(title="Radius Error", content=content, size_hint=(.6, .6)).open()
    def format_elevation(self, selevation):  # format elevation to meter from meter (m) or feet (ft)
        try:
            sid = 'elevation_input'
            selevation = selevation.split(':', 1)[0].strip()
            ltsin = len(selevation)
            elevation = float(numin(selevation))
            if 'ft' in selevation or 'feet' in selevation or 'foot' in selevation:
                elevationft = elevation
                elevation *= feet2meter
            elif 'km' in selevation:
                elevation *= km2meter
                elevationft = elevation / feet2meter
            elif 'meter' in selevation or ('m' in selevation and not re.search('[a-ln-z]+', selevation)):
                elevationft = elevation / feet2meter
            elif re.search('[a-z]+', selevation):
                emessage = "Invalid '" + re.search('[a-zA-Z]+', selevation)[0] + "' unit."
                raise TypeError()
            else:
                elevationft = elevation / feet2meter
            selevation += f' : [{elevation:0.3f} m] = {elevationft:0.3f} ft'
            self.ids[sid].text = selevation
            Clock.schedule_once(partial(self._refocus_textinput, sid, ltsin))
        except (RuntimeError, ValueError, TypeError):
            content = Label(text=emessage + "\n" + "Touch outside to dismiss.", halign='center', valign='middle')
            popup = Popup(title="Elevation Error", content=content, size_hint=(.6, .6)).open()

    def _refocus_textinput(self, *args):
        self.ids[args[0]].cursor = (args[1], 0)
        self.ids[args[0]].get_focus_next().focus = True

    def format_latlong(self, slatlong):  # adds degrees/minutes/seconds to longitude
        lcd = [];
        di = '';
        dn = 1
        try:
            if 'LATITUDE' in slatlong:
                sid = 'latitude_input'
                lcd = ['N', 'S']
                slatlong = slatlong.split(':', 1)[0].strip()
                if 'n' in slatlong.lower():
                    di = 'N';
                    dn = 1
                elif 's' in slatlong.lower():
                    di = 'S';
                    dn = -1
            elif 'LONGITUDE' in slatlong:
                sid = 'longitude_input'
                lcd = ['E', 'W']
                slatlong = slatlong.split(':', 1)[0].strip()
                if 'e' in slatlong.lower():
                    di = 'E';
                    dn = 1
                elif 'w' in slatlong.lower():
                    di = 'W';
                    dn = -1
            #            lstr = [s for sd in slatlong.split(' ') for sm in sd.split("'") for s in sm.split('"') if s]
            ltsin = len(slatlong)
            lstr = [slatlong]
            for sc in SplittingCharacters:
                lsc = []
                for str in lstr:
                    lsc += list(filter(('').__ne__, str.split(sc)))
                lstr = lsc
            dmsd = [0, 0, 0, dn];
            i = 0
            for str in lstr:
                try:
                    dmsd[i] = float(str)
                    i += 1
                except:
                    continue
                if i > 2:
                    break
            if dmsd[0] < 0:
                dmsd[3] = -1
            dd = dmsd2dd(dmsd)
            sdmsd = dd2dmsd(dd, lcd)
            slatlong += f' : [{dd:0.7f}] = {sdmsd[0]} {sdmsd[1]}\' {sdmsd[2]}" {sdmsd[3]}'
            self.ids[sid].text = slatlong
            Clock.schedule_once(partial(self._refocus_textinput, sid, ltsin))
        except (RuntimeError, ValueError, TypeError):
            content = Label(
                text="Check that latitude/longitude has been validated." + "\n" + "Touch outside to dismiss.",
                halign='center', valign='middle')
            popup = Popup(title="Latitude/Longitude Error", content=content, size_hint=(.6, .6)).open()

    def save(self):
        address = self.ids['address_input'].text
        citystatezip = self.ids['citystatezip_input'].text
        country = self.ids['country_input'].text
        latitude = self.ids['latitude_input'].text
        longitude = self.ids['longitude_input'].text
        elevation = self.ids['elevation_input'].text
        rcsinputs = open("rcsinputs.txt", 'a')

        rcsinputs.write(
            "Address: " + address  + "\n" + "City/State/Zip: " + citystatezip + "\n" + "Country: " +  country + "\n" "Latitude: " + latitude + "\n" + "Longitude: " + longitude + ': ' + "\n" + "Elevation: " + elevation + "\n")
        rcsinputs.close()




class TestingApp(App):

    def build(self):
        root = ScreenManager()
        root.add_widget(FirstScreen(name='FirstScreen'))
        root.add_widget(SecondScreen(name = 'SecondScreen'))
        root.add_widget(RVScreen(name='RVScreen'))
        return root




    def save(self, event, activity, agent, address, citystatezip, country, latitude, longitude, elevation, radius, duration, ip, comments, spectrum): # formats and prompts user to save rcsinputs.txt file
        inheader = ['#<Event Name:', '#<Activity:', '#<Agent:', '#<Nearest Address:', '#<City, State Zip-code:', '#<Country:',
                '#<Collection Center Latitude:', '#<Collection Center Longitude:', '#<Collection Center Elevation:',
                '#<Collection Center Radius:', '#<Scan Duration ([s]econd|{m}inute|{h}our|{d}ay|{c}ycle:',
                '#<Instrument Info [IP Address]:', '#<Comments:']
        try:
            indata = [event, activity, agent, address, citystatezip, country, latitude, longitude, elevation, radius, duration, ip, comments]
            inputs = cnl.join([' '.join(te) for te in list(zip(inheader, indata)) ])
            rcsinputs = open("rcsinputs.txt", 'w')
            rcsinputs.write(inputs)
            rcsinputs.close()

        except (RuntimeError, ValueError, TypeError, UnboundLocalError):
            content=Label(text="Get rcsbands.txt first." + "\n" + "Touch outside to dismiss.", halign='center', valign='middle')
            popup = Popup(title="Save Error", content=content, size_hint=(.6, .6)).open()



if __name__ == '__main__':
    TestingApp().run()