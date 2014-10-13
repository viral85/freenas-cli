#!/usr/local/bin/python
# --------------------- Standard import modules --------------------------------
from cmd import Cmd
import os
from tabulate import tabulate
import requests
import sys

#------------------ Base API Class -----------------------------------------------
class APIClient(object):
    """Creates an API client object
    :param user: the API root user.
    :param password: the API root user password.
    """
    BASE_URL = 'http://localhost/'
    METHOD_ALLOWED = ['get','put','post']

    def __init__(self, user=None, passwd=None):
        # userid and api key sent with every request
        self.user = user
        self.passwd = passwd
        # the error description if it occured
        self.error = None

    def _request(self, method, path, data=None, **params):
        # if we're testing use the sandbox url
        api_url = self.BASE_URL + path
        auth = (params['username'], params['password'])
        # add the authentication parameters (sent with every request)
        # params.update({self.user:self.passwd})
        # the api request result
        result = None
        #Raise custome exception when method not allowed
        if not method in self.METHOD_ALLOWED:
            raise 'Method Not Allowed'
        try:
            # send a request to the api server
            req_method = getattr(requests,method)
            response_out = req_method(api_url,auth=auth,)

            # raise an exception if status code is not 200
            if response_out.status_code is not 200:
                raise Exception
            else:
                result = response_out.json()

        except requests.ConnectionError:
            self.error = 'API connection error.'
        except requests.HTTPError:
            self.error = 'An HTTP error occurred.'
        except requests.Timeout:
            self.error = 'Request timed out.'
        except Exception:
            self.error = 'An unexpected error occurred.'

        return result

    def get(self, path, **params):
        return self._request('get', path, **params)

    def put(self, path, data, **params):
        return self._request('put', path, data=data, **params)

    def post(self, path, data, **params):
        return self._request('post', path, data=data, **params)

    def delete(self, path, data, **params):
        return self._request('delete', path, data=data, **params)

# -------------------------------------------------------------------------------
class BASEAPI(APIClient):
    BASE_URL = 'http://localhost'
    METHOD_ALLOWED = ['get','post','put','delete']

class GroupAPI(APIClient):
    BASE_URL = 'http://localhost/api/v1.0'
    METHOD_ALLOWED = ['get','post','put','delete']

class ActiveDirAPI(APIClient):
    BASE_URL = 'http://localhost/api/v1.0/directoryservice/activedirectory/'
    METHOD_ALLOWED = ['get',]

class LdpaAPI(APIClient):
    BASE_URL = 'http://localhost/api/v1.0/directoryservice/ldap/'
    METHOD_ALLOWED = ['get','put']

class JailsConfAPI(APIClient):
    BASE_URL = 'http://localhost/api/v1.0/jails/configuration/'
    METHOD_ALLOWED = ['get','post','put','delete']

class JailsAPI(APIClient):
    BASE_URL = 'http://localhost/api/v1.0/jails/jails'
    METHOD_ALLOWED = ['get','post','delete']

# -------------------------------------------------------------------------------
class FreenasAPI(object):

    resource_dict = {}

    def display_tabulate(self, result):
        headers = result[0].keys()
        table = []
        for loop in result:
            table.append(loop.values())
        print tabulate(table,headers, tablefmt="pipe")

    def get_tastypie_resource(self, *args, **kwargs):
        self.resource_url = BASEAPI()
        self.format_url = '/api/v1.0/?format=json'
        self.username = kwargs.get('username', 'root')
        self.password = kwargs.get('password', 'abcd1234')
        try:
            self.resource_out = self.resource_url.get(self.format_url, username=self.username, password=self.password)
            for loop in self.resource_out.keys():
                self.resource_dict[loop] = self.resource_out[loop]['list_endpoint']
            print "Welcome to Enbale/Debug Mode"
        except Exception:
            return "Could not connect to Freenas API"


    def users(self,*args,**kwargs):
        self.user_apiurl = BASEAPI()
        self.user_path = self.resource_dict.get('account/users', None)
        if self.user_path == None:
            return "API Url not avaliable"
        user_id = kwargs.get('id','all')
        if user_id != 'all':
            self.user_path = '/account/users/'+str(user_id)+'/'
        self.username = kwargs.get('username', 'root')
        self.password = kwargs.get('password', 'abcd1234')
        try:
            self.user_response = self.user_apiurl.get(self.user_path, username=self.username, password=self.password)
            self.display_tabulate(self.user_response)
        except Exception :
            return "Error in Getting User Data"

    def groups(self,*args,**kwargs):
        self.group_apiurl = GroupAPI()
        self.group_path = '/account/groups/'
        group_id = kwargs.get('id','all')
        if group_id != 'all':
            self.group_path = '/account/groups/'+str(group_id)+'/'
        self.username = kwargs.get('username', 'root')
        self.password = kwargs.get('password', 'abcd1234')
        try:
            self.group_response = self.group_apiurl.get(self.group_path, username=self.username, password=self.password)
            self.display_tabulate(self.group_response)
        except Exception :
            return "Error in Getting Group Data"

    def resources(self, *args, **kwargs):
        if args[0] == '':
            headers = ['name', 'url']
            print tabulate(self.resource_dict.items(),headers, tablefmt="pipe")
        else:
            self.rs_apiurl = BASEAPI()
            self.rs_path = self.resource_dict.get(args[0][0], None)
            if self.rs_path == None:
                return "API Url not avaliable"
            rs_id = args[0][1]
            if rs_id != 'all':
                self.rc_path = self.resource_dict[args[0][0]]+str(rs_id)+'/'
            self.username = kwargs.get('username', 'root')
            self.password = kwargs.get('password', 'abcd1234')
            try:
                self.rc_response = self.rs_apiurl.get(self.rs_path, username=self.username, password=self.password)
                self.display_tabulate(self.rc_response)
            except Exception :
                return "Error in Getting User Data"


# -------------------------------------------------------------------------------
# Cli Section.
# All cli need to be supported need to added here.
# -------------------------------------------------------------------------------
class FreenasPrompt(Cmd, FreenasAPI):

    last_output = ''
    mode = 'default'
    username  = 'root'
    password = 'abcd1234'

    def do_hello(self, args):
        """Says hello. If you provide a name, it will greet you with it."""
        if len(args) == 0:
            name = 'stranger'
        else:
            name = args
        print "Welcome to Freenas, %s" % name

    def do_en(self, in_args):
        """Move to Enbale Mode """
        if self.mode == 'default':
            self.prompt = self.prompt[:-2]+'-enable> '
            self.mode = 'enable'
            call_function = getattr(self,'get_tastypie_resource')
            call_function(in_args,username=self.username, password=self.password)
        else:
            print "Already in Enable mode"

    def do_resources(self, in_args):
        """ to get all resources url"""
        if self.mode == 'enable':
            call_function = getattr(self,'resources')
            call_function(in_args,username=self.username, password=self.password)
        else :
            print "Only works in Enable mode"

    def do_get(self,in_args):
        """ Works on Enbale mode only
 Get the details resources <resources_name all
 Eg : get resources jails/jails all
 Eg : get resources account/users all
        """
        # Check the invalid Charater as input data
        if in_args in ['?'] or len(in_args) == 0:
            print "Wrong option try '? get'"
            print "Error_1 : Input arguments are wrong"
            print "Try get resources <resources_name> all "
            print " Eg : get resources jails/jails all"
            print " Eg : get resources account/users all"
            return 0

        if self.mode == 'enable':
            try:
                input_data = in_args.split(' ')
                if len(input_data) >= 2:
                    call_function = getattr(self,input_data[0])
                else:
                    print "Error_1 : Input arguments are wrong"
                    print "Try get resources <resources_name> all "
                    print " Eg : get resources jails/jails all"
                    print " Eg : get resources account/users all"
                    return 0
            except:
                print "Input error"
            call_function(input_data[1:],username=self.username, password=self.password)
        else :
            print "Only works in Enable mode"

    def do_quit(self, args):
        """Quits the program."""
        if self.mode == 'enable':
            self.prompt = 'Freenas>'
            self.mode = 'default'
            print 'Quitting Enable mode'
        else:
            print "Quitting."
            raise SystemExit

    def do_exit(self, args):
        """Quits the program."""
        if self.mode == 'enable':
            self.prompt = 'Freenas>'
            self.mode = 'default'
            print 'Quitting Enable mode'
        else:
            print "Quitting."
            raise SystemExit

    def do_EOF(self, line):
        """Control D to exit"""
        return True

    def do_shell(self, line):
        """Run a shell command"""
        print "running shell command:", line
        output = os.popen(line).read()
        print output
        self.last_output = output

    def do_echo(self, line):
        """Print the input, replacing '$out' with the output of the last shell command"""
        # Obviously not robust
        print line.replace('$out', self.last_output)


if __name__ == '__main__':
    prompt = FreenasPrompt()
    if len(sys.argv) > 1:
        prompt.prompt = ' '.join(sys.argv[1:])+"> "
    else :
        prompt.prompt = 'Freenas> '
    prompt.info = 'Welcome to the Freenas shell. \n\
Type help or ? to list commands.'
    prompt.cmdloop(prompt.info)
