"""
Reza Raji
July 2022
Simple app to replace the now discontinued and defunct Russound TCH1 unit
Hardcoded for my controllers and zones but not worth trying to make that all user-programmable (for now)
Uses a converted russound RNET library to work on serial port (russound_serial.py)
"""
import russound_serial
from http.server import BaseHTTPRequestHandler, HTTPServer

host_name = '192.168.1.200'  # Change this to your Raspberry Pi IP address
host_port = 8000

#RUSSOUND SYSTEM SETTINGS - modify to match your system
CONTROLLER_COUNT=2  #how many Russound controllers are daisy chained. Russound allows max of 6
#Zone names in order (control 1 then 2, ...)
ZONE_NAMES = ['Guest Bath', 'Dining Room', 'Kitchen', 'Master Bed', 'Master Bath', 'Nick', 'Office', 'Play Room', 'Alex', 'Living Room', 'Patio', 'Pool']
SOURCE_NAMES = ['Sonos', 'Apple']   #Source names in order. Russound allows max of 6
global current_cmd
global current_zone
global new_volume

SERIAL_PORT = '/dev/ttyUSB0'       # for RPi
BAUD = 19200

#Initiate connection to Russound system
x = russound_serial.Russound(SERIAL_PORT, BAUD)

def all_on():     #All zones ON
    for controller in range(1, CONTROLLER_COUNT+1):
        for zone in range(1, 7):
            x.set_power(controller, zone, '1')
            print(controller, zone)


def all_off():   #All zones OFF
    for controller in range(1, CONTROLLER_COUNT+1):
        for zone in range(1, 7):
            x.set_power(controller, zone, '0')
            print(controller, zone)


def controller_ID (zone_name):  #return the controller ID string based on the name of the zone (returns a number between 1-6)
    return str(int((ZONE_NAMES.index(zone_name)/6)+1))


def zone_ID(zone_name):         #return the zone ID string based on the name of the zone (returns a number between 1-6)
    return str((ZONE_NAMES.index(zone_name)%6)+1)


def source_ID(source_name):     #return the source ID string based on the name of the zone (returns a number between 1-6)
    return str(SOURCE_NAMES.index(source_name))


def print_all_zones():
    # Print all the Zone names with their control and zone IDs
    for x in range(len(ZONE_NAMES)):
        print(ZONE_NAMES[x], controller_ID(ZONE_NAMES[x]), zone_ID(ZONE_NAMES[x]))
    for x in range(len(SOURCE_NAMES)):
        print(SOURCE_NAMES[x], int(source_ID(SOURCE_NAMES[x])) + 1)


class MyServer(BaseHTTPRequestHandler):
    """ A special implementation of BaseHTTPRequestHander for handling my GET and POST requests
    """
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        #Serve the main html page
        if (self.path == '/'):
            html = '''
                <!DOCTYPE html>
                <style>
                .content {
                  max-width: 500px;
                  margin: auto;
                }
                h1 { 
                  display: block;
                  font-size: 4em;
                  font-family:"helvetica";
                }
                .button {
                  border: 2px solid white;
                  color: white;
                  height:100px;
                  width:100%;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  font-size: 35px;
                  margin: 2px;
                  cursor: pointer;
                  white-space: nowrap;
                  border-radius: 8px;
                }
                .buttonOn {background-color: #4CAF50;} /* Green */
                .buttonOff {background-color: #DC143C;} /* Red */
                .buttonAllOff {width: 80%; background-color: #DC143C;}
                .buttonGo {width: 100%; background-color: #6593ff;}
                </style>
    
                <body>
                  <center>
                  <h1>Russound Mobile App</h1>
                  <form method="post" action="/post">
                    <button class="button buttonAllOff" type="submit" value="Off, All" name="button">All Off</button>
                    <table style="width:80%">
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Guest Bath" name="button">Guest Bath</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Guest Bath" name="button">Guest Bath</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Guest Bath" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Dining Room" name="button">Dining Room</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Dining Room" name="button">Dining Room</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Dining Room" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Kitchen" name="button">Kitchen</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Kitchen" name="button">Kitchen</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Kitchen" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Master Bed" name="button">Master Bed</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Master Bed" name="button">Master Bed</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Master Bed" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Master Bath" name="button">Master Bath</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Master Bath" name="button">Master Bath</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Master Bath" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Nick" name="button">Nick</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Nick" name="button">Nick</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Nick" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Office" name="button">Office</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Office" name="button">Office</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Office" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Play Room" name="button">Play Room</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Play Room" name="button">Play Room</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Play Room" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Alex" name="button">Alex</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Alex" name="button">Alex</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Alex" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Living Room" name="button">Living Room</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Living Room" name="button">Living Room</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Living Room" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Patio" name="button">Patio</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Patio" name="button">Patio</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Patio" name="button">></button></td>
                    </tr>
                    <tr>
                    <td><button class="button buttonOn" type="submit" value="On, Pool" name="button">Pool</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, Pool" name="button">Pool</button></td>
                    <td><button class="button buttonGo" type="submit" value="Go, Pool" name="button">></button></td>
                    </tr>
                    </table>
                  </form>
                </center>
                </body>
                </html>
            '''
            self.do_HEAD()
            self.wfile.write(html.encode("utf-8"))

        #Serve the zone-specif html page
        elif (self.path == '/go'):
            # Have to use double braces due to the variable substitution being done using the string format function
            html = '''
                <!DOCTYPE html>
                <style>
                .content {{
                  max-width: 500px; 
                  margin: auto;
                }}
                h1 {{
                  display: block;
                  font-size: 4em;
                  font-family:"helvetica";
                }}
                h2 {{
                  display: block;
                  font-size: 3em;
                  font-family:"helvetica";
                }}
                .button {{
                  border: 2px solid white;
                  color: white;
                  height:100px;
                  width:90%;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  font-size: 35px;
                  margin: 2px;
                  cursor: pointer;
                  white-space: nowrap;
                  border-radius: 8px;
                }}
                .buttonOn {{background-color: #4CAF50;}} /* Green */
                .buttonOff {{background-color: #DC143C;}} /* Red */
                .buttonAllOff {{width: 90%; background-color: #DC143C;}}
                .buttonGo {{width: 75%; background-color: #6593ff;}}
                </style>

               <body>
                  <center>
                  <h1>{zonetitle}</h1>
                  <form method="post" action="/post">
                    <table style="width:80%">
                    <tr>
                    <td><h2>Zone</h2>
                    <td><button class="button buttonOn" type="submit" value="On, zone" name="button">ON</button></td>
                    <td><button class="button buttonOff" type="submit" value="Off, zone" name="button">OFF</button></td>
                    </tr>
                    <tr>
                    <td><h2>Source</h2>
                    <td><button class="button buttonOn" type="submit" value="Source, Sonos" name="button">Sonos</button></td>
                    <td><button class="button buttonOff" type="submit" value="Source, Apple" name="button">Apple</button></td>
                    </tr>
                    <tr>
                    <td><h2>Volume</h2>
                    <td><button class="button buttonOn" type="submit" value="Up, zone" name="button">UP</button></td>
                    <td><button class="button buttonOff" type="submit" value="Down, zone" name="button">DOWN</button></td>
                    </tr>
                
                    </table>
                    <br><br><br><br>
                    <td><button class="button buttonGo" type="submit" value="Back, none" name="button">Back</button></td>
                
                  </form>
                </center>
                </body>
                </html>
            '''
            self.do_HEAD()
            output = html.format(zonetitle=current_zone)
            self.wfile.write(output.encode("utf-8"))


    def do_POST(self):
        global current_cmd
        global current_zone
        global new_volume

        # Handle the posts from all pages (need to be careful to have unique commands across all pages)

        content_length = int(self.headers['Content-Length'])  # Get the size of data
        post_data = self.rfile.read(content_length).decode("utf-8")  # Get the data
        payload = post_data.split("=")[1] #"On, ..."
        payload_cmd = payload.split("%2C+")[0] #"On"
        payload_zone = payload.split("%2C+")[1] #Zone #
        payload_zone = payload_zone.replace("+", " ")   #replace any spaces that were converted to "+" via the HTML Post

        if payload_cmd == "Go":
            current_cmd = payload_cmd
            current_zone = payload_zone
            new_vollume = x.get_volume(controller_ID(current_zone), zone_ID(current_zone))
            self._redirect('/go')  # Redirect to zone details page

        if payload_cmd == "On":
            if payload_zone == "zone":
                x.set_power(controller_ID(current_zone), zone_ID(current_zone), '1')
                self._redirect('/go')  # Redirect back same page
            else:
                x.set_power(controller_ID(payload_zone), zone_ID(payload_zone), '1')
                self._redirect('/')  # Redirect back to the root url

        if payload_cmd == "Off":
            if payload_zone == "All":
                all_off()
                self._redirect('/')  # Redirect back to the root url
            elif payload_zone == "zone":
                x.set_power(controller_ID(current_zone), zone_ID(current_zone), '0')
                self._redirect('/go')  # Redirect back same page
            else:
                x.set_power(controller_ID(payload_zone), zone_ID(payload_zone), '0')
                self._redirect('/')  # Redirect back to the root url

        if payload_cmd == "Back":
            self._redirect('/')  # Redirect back to the root url

        if payload_cmd == "Source":
            x.set_source(controller_ID(current_zone), zone_ID(current_zone), source_ID(payload_zone))
            self._redirect('/go')  # Redirect back same page

        if payload_cmd == "Up":
            current_volume = x.get_volume(controller_ID(current_zone), zone_ID(current_zone))
            new_volume = current_volume + 5
            if (new_volume > 50):
                new_volume = 50 #cap to max level acceptaed by stystem (50 is = 100%)
            x.set_volume(controller_ID(current_zone), zone_ID(current_zone), new_volume)
            self._redirect('/go')  # Redirect back same page

        if payload_cmd == "Down":
            current_volume = x.get_volume(controller_ID(current_zone), zone_ID(current_zone))
            new_volume = current_volume - 5
            if (new_volume < 0):
                new_volume = 0 #cap to min level acceptaed by stystem
            x.set_volume(controller_ID(current_zone), zone_ID(current_zone), new_volume)
            self._redirect('/go')  # Redirect back same page


if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
