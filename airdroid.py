"""
OverAirdroid
An unofficial API script to make automating Airdroid functions easier.
Created by Matthew Bryant
Working with Python 3, md5 import working by Thomas Leick
"""
import datetime
import requests
import base64
import urllib
import time
import json
from hashlib import md5
import sys
from bs4 import BeautifulSoup

class overairdroid:
    """
    Converts the callback Javascript to a dict of the JSON
    @input_json Inputted JSON packed in Airdroid callback stuff
    return  Returns a dict of inputted Airdroid Javascript
    """
    def air2json( self, input_json ):
        init_json = input_json
        init_json = init_json.replace("_jqjsp(", "")
        init_json = init_json[:-1]
        init_json = json.loads( init_json )
        return init_json

    """
    Make viewing trees a lot easier
    @input_dict The input dictionary for viewing
    return None
    """
    def pprint( self, input_dict):
        print(json.dumps(input_dict, sort_keys=True, indent=4, separators=(',', ': ')))

    """
    Initialize all of the needed variables
    @inut_dict  The input dict with all of our needed values

    return None
    """
    def initialize_variables( self, input_dict ):
        self.channel_token = input_dict['result']['device'][0]['channelToken']
        self.device_id = input_dict['result']['device'][0]['deviceId']
        self.id = str( input_dict['result']['device'][0]['id'] )
        self.imsi = input_dict['result']['device'][0]['imsi']
        self.logic_key = input_dict['result']['device'][0]['logicKey']
        self.content_id = input_dict['result']['device'][0]['id']
        self.account_id = input_dict['result']['id']
        self.manufacturer = input_dict['result']['device'][0]['manu']
        self.model = input_dict['result']['device'][0]['model']
        self.phone_ip = str( input_dict['result']['device'][0]['netOpts']['ip'] )
        self.phone_port = str( input_dict['result']['device'][0]['netOpts']['port'] )
        self.phone_socket_port = str( input_dict['result']['device'][0]['netOpts']['socket_port'] )
        self.phone_ssl_port = str( input_dict['result']['device'][0]['netOpts']['ssl_port'] )
        self.phone_wifi = input_dict['result']['device'][0]['netOpts']['usewifi']
        self.get_bb()

    def statusmsg( self, input_string ):
        if self.verbose:
            print("[ STATUS ] " + input_string)

    def errormsg( self, input_string ):
        if self.verbose:
            print("[ ERROR ] " + input_string)

    """
    Initialize the OverTheAirdroid object
    @in_username    The Airdroid username
    @in_password    The Airdroid password
    @in_verbose     Should the program be verbose?
    return None
    """
    def __init__(self, in_username, in_password, in_verbose = True):
        self.username = in_username
        self.password = in_password
        self.verbose = in_verbose

        global_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0',
        }

        self.s = requests.Session()
        self.s.headers.update( global_headers )

        # Internal variables
        self.channel_token = ""
        self.device_id = ""
        self.logic_key = ""
        self.imsi = ""
        self.id = ""
        self.account_id = ""
        self.model = ""
        self.manufacturer = ""
        self.phone_ip = ""
        self.phone_port = ""
        self.phone_socket_port = ""
        self.phone_ssl_port = ""
        self.phone_wifi = False
        self.var_7bb = ""

        # Extra phone info variables
        self.battery_charge = ""
        self.is_charging = ""
        self.app_count = ""
        self.contact_count = ""
        self.music_count = ""
        self.ebook_count = ""
        self.photo_count = ""
        self.video_count = ""
        self.external_sd_location = ""
        self.gsm_bars = ""
        self.model = ""
        self.orientation = ""
        self.os_version = ""
        self.external_sd_size = ""
        self.external_sd_free = ""
        self.storage_size = ""
        self.storage_size_free = ""
        self.wifi_name = ""
        self.wifi_bars = ""

        # Attempt a log in
        self.is_loggedin = self.login()

    """
    Login to Airdroid

    return  True on success and False on failure
    """
    def login( self ):
        self.statusmsg( "Logging in to AirDroid..." )
        r = self.s.get('http://web.airdroid.com/', )

        get_data = {
            'mail': self.username,
            'pwd': self.password,
            'callback': '_jqjsp',
            'keep': '0',
        }

        r = self.s.get('https://id.airdroid.com/p9/user/signIn.html', params=get_data)

        info = self.air2json( r.text )

        if info['msg'] == "success!":
            self.initialize_variables( info )
            self.statusmsg( "Login was successful!" )
            self.statusmsg( "Phone address: " + self.phone_ip + ":" + self.phone_port )
            return True
        else:
            self.errormsg( "Login failed!" )
            return False

    """
    Wakeup the Android device if an action hasn't been preformed in a while
    return  True on success and False on failure
    """
    def wakeup( self ):
        n = datetime.datetime.now()
        get_data = {
            "id": self.device_id,
            "accountId": self.account_id,
            "logicKey": self.logic_key,
            "callback": "_jqjsp",
            "_" + str( int( time.mktime(n.timetuple()) ) ): "",
        }

        r = self.s.get( 'http://lb.airdroid.com:9081/wakePhone', params=get_data )

        response = self.air2json( r.text )

        if response['msg'] == "wake phone success":
            return True
        else:
            return False

    """
    Get the "bb" value needed to preform Airdroid actions
    return  String of bb value
    """
    def get_bb( self ):
        n = datetime.datetime.now()
        unix_time = str( int( time.mktime(n.timetuple()) ) )
        m = md5.new()
        m.update( unix_time + self.device_id + self.logic_key )
        key = unix_time + m.digest().encode("hex")

        get_data = {
            "keeplogin": 0,
            "type": 2,
            "key": key,
            "7bb": "null",
            "callback": "_jqjsp",
            "_" + unix_time: "",
        }

        r = self.s.get('http://' + self.phone_ip + ':' + self.phone_port + '/sdctl/comm/checklogin/', params=get_data)

        self.var_7bb = self.air2json( r.text )['7bb']

    """
    Open URL on Android device

    @url    String of the URL to open
    return  None
    """
    def url_open( self, url ):
        n = datetime.datetime.now()
        unix_time = str( int( time.mktime(n.timetuple()) ) )

        get_data = {
            "url": url,
            "7bb": self.var_7bb,
            "callback": "_jqjsp",
            "_" + unix_time: "",
        }

        r = self.s.get('http://' + self.phone_ip + ':' + self.phone_port + '/sdctl/comm/openurl/', params=get_data)

    """
    Why is this still here?
    """
    def display_info( self ):
        n = datetime.datetime.now()
        unix_time = str( int( time.mktime(n.timetuple()) ) )

        get_data = {
            "7bb": self.var_7bb,
            "callback": "_jqjsp",
            "_" + unix_time: "",
        }

        r = self.s.get('http://' + self.phone_ip + ':' + self.phone_port + '/sdctl/device/overview/', params=get_data)

        info = self.air2json( r.text )

        self.battery_charge = info['battery']
        self.is_charging = info['batterycharging']
        self.app_count = info['counts']['app']
        self.contact_count = info['counts']['contacts']
        self.music_count = info['counts']['music']
        self.ebook_count = info['counts']['ebook']
        self.photo_count = info['counts']['photo']
        self.video_count = info['counts']['video']
        self.external_sd_location = info['ex_sd']
        self.gsm_bars = info['gsm_signal']
        self.model = info['model']
        self.orientation = info['orientation']
        self.os_version = info['osversion']
        self.external_sd_size = info['size']['ext_sd_avail']
        self.external_sd_free = info['size']['ext_sd_size']
        self.storage_size = info['size']['sys_size']
        self.storage_size_free = info['size']['sys_avail']
        self.wifi_name = info['wifi_name']
        self.wifi_bars = info['wifi_signal']

    """
    Set the Android clipboard
    @data   Data to set the clipboard to
    return  True on success and False on failure
    """
    def set_clipboard( self, data ):
        n = datetime.datetime.now()
        unix_time = str( int( time.mktime(n.timetuple()) ) )

        layer_data = {
            "content": base64.b64encode( data )
        }

        post_data = {
            "content": urllib.quote_plus( json.dumps( layer_data ) ),
        }

        r = self.s.post('http://' + self.phone_ip + ':' + self.phone_port + '/sdctl/comm/clipboard/set?7bb=' + self.var_7bb, data=post_data)

        result = json.loads( r.text )

        if result['result'] == 0:
            return True
        else:
            return False

    """
    Get the Android device's clipboard
    return  The clipboard contents
    """
    def get_clipboard( self ):
        self.statusmsg( "Grabbing clipboard contents..." )
        n = datetime.datetime.now()
        unix_time = str( int( time.mktime(n.timetuple()) ) )

        get_data = {
            "7bb": self.var_7bb,
            "callback": "_jqjsp",
            "_" + unix_time: "",
        }

        r = self.s.get('http://' + self.phone_ip + ':' + self.phone_port + '/sdctl/comm/clipboard/get', params=get_data)

        response = self.air2json( r.text )
        data = json.loads( urllib.unquote_plus( base64.b64decode( response['content'] ) ) )

        self.statusmsg( "Clipboard contents grabbed!" )
        return data['result']

    """
    Send an SMS from Android phone
    @phone_number   Integer of the phone number to send the SMS to
    @message        String of the SMS message to be sent
    return True on success and False on failure
    """
    def sms( self, phone_number, message ):
        self.statusmsg( "Sending SMS..." )
        n = datetime.datetime.now()
        unix_time = str( int( time.mktime(n.timetuple()) ) )

        layer1 = {
            "number": phone_number,
            "content": str( message ),
            "threadId": unix_time,
        }

        layer2 = {
            "content": base64.b64encode( urllib.quote_plus( urllib.quote_plus( json.dumps( layer1 ) ) ) ),
        }

        post_data = {
            "params": json.dumps( layer2 ),
        }

        r = self.s.post('http://' + self.phone_ip + ':' + self.phone_port + '/sdctl/sms/send/single/?7bb=' + self.var_7bb, data=post_data)
        response = json.loads( r.text )
        if "threadId" in base64.b64decode( response['content'] ):
            self.statusmsg( "SMS sent!" )
            return True
        else:
            self.errormsg( "Error sending SMS!" )
            return False
