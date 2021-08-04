from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
import weakref
from kivy.clock import Clock
import csv, datetime, decimal, math, re, os, time
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


class Row(GridLayout):
    pass

class Table(GridLayout):
    pass


class Rows(BoxLayout):
    def __init__(self, **kwargs):
        super(Rows, self).__init__(**kwargs)
        Clock.schedule_once(self.fill)
        self._rows = {}

    def fill(self, dt):
        for i in range(8):
            row = Row()
            self.add_widget(row)
            self._rows["row"+str(i)] = weakref.ref(row)


    def save(self):
        for id, row in self._rows.items():
            print(id)
            children = row().children
            col = len(children) - 1
            for ti in children:
                print('\tcol#', col, ti.text)
                col -= 1

class Tables(BoxLayout):
    def __init__(self, **kwargs):
        super(Tables, self).__init__(**kwargs)
        Clock.schedule_once(self.fill)
        self._tables = {}

    def fill(self, dt):
        for i in range(5):
            table = Table()
            self.add_widget(table)
            self._tables["row"+str(i)] = weakref.ref(table)

    def save(self):
        for id, table in self._tables.items():
            print(id)
            children = table().children
            col = len(children) - 1
            for ti in children:
                print('\tcol#', col, ti.text)
                col -= 1

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

class ShipmentsScreen(Screen):
    pass


class TestApp(App):
    def build(self):
        root = ScreenManager()
        root.add_widget(FirstScreen(name='FirstScreen'))
        root.add_widget(SecondScreen(name='SecondScreen'))
        root.add_widget(ShipmentsScreen(name='ShipmentsScreen'))
        return root

if __name__ == '__main__':
    TestApp().run()
