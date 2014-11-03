#!/usr/local/bin/python
# --------------------- Standard import modules --------------------------------
from cmd import Cmd
import os
from tabulate import tabulate
import requests
import sys
import json

#------------------ Base API Class -----------------------------------------------
class APIClient(object):
    """Creates an API client object
    :param user: the API root user.
    :param password: the API root user password.
    """
    BASE_URL = 'http://localhost/'
    METHOD_ALLOWED = ['get','put','post','delete']

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
            if not response_out.status_code in [200,202,204,401]:
                raise Exception
            else:
                try:
                    result = response_out.json()
                except:
                    result = response_out

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

    def display_plain(self, result):
        print result.text

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

    def resources_action(self, *args, **kwargs):
        if args[0] == '':
            headers = ['name', 'url']
            print tabulate(self.resource_dict.items(),headers, tablefmt="pipe")
        else:
            self.rs_apiurl = BASEAPI()
            self.rs_new_path = self.resource_dict.get(kwargs['resource_name'], None)
            if self.rs_new_path == None:
                return "API Url not avaliable"
            rs_id = args[0][0]
            rc_act = args[0][1]
            self.username = kwargs.get('username', 'root')
            self.password = kwargs.get('password', 'abcd1234')
            try:
                if rc_act == 'start':
                    self.rs_path = self.rs_new_path+str(rs_id)+'/start/'
                    self.rc_response = self.rs_apiurl.post(self.rs_path, '', username=self.username, password=self.password)
                    self.display_plain(self.rc_response)
                elif rc_act == 'stop':
                    self.rs_path = self.rs_new_path+str(rs_id)+'/stop/'
                    self.rc_response = self.rs_apiurl.post(self.rs_path, '', username=self.username, password=self.password)
                    self.display_plain(self.rc_response)
                elif rc_act == 'delete':
                    self.rs_path = self.rs_new_path+str(rs_id)+'/'
                    self.rc_response = self.rs_apiurl.delete(self.rs_path, '', username=self.username, password=self.password)
                    self.display_plain(self.rc_response)
                else:
                    self.rs_path = self.rs_new_path
                    self.rc_response = self.rs_apiurl.get(self.rs_path, username=self.username, password=self.password)
                    if self.rc_response.status == 204 and self.rc_response.text == '':
                        print "Requested Plugin Delete"
            except Exception :
                return "Error in Getting User Data"

        def resources_create(self, *args, **kwargs):
            if args[0] == '':
                headers = ['name', 'url']
                print tabulate(self.resource_dict.items(),headers, tablefmt="pipe")
            else:
                self.rs_apiurl = BASEAPI()
                self.rs_new_path = self.resource_dict.get(kwargs['resource_name'], None)
                if self.rs_new_path == None:
                    return "API Url not avaliable"
                var_name = args[0][0]
                self.username = kwargs.get('username', 'root')
                self.password = kwargs.get('password', 'abcd1234')
                post_data = self.var_dict[var_name]
                try:
                    self.rc_response = self.rs_apiurl.post(self.rs_new_path, data=post_data, username=self.username, password=self.password)
                    if self.rc_response.status == 401 and self.rc_response.text == '':
                        print "Created resource"
                    else:
                        self.display_plain(self.rc_response)
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
    var_dict = {}
    variable = ''
    user_prompt = ''

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
            self.user_prompt = self.prompt[:-2]
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

    def do_resource(self, in_args):
        """ Action on resource ( start /stop / delete)
Example: resource plugins 1 start
         resource jails 1 start"""
        if self.mode == 'enable':
            input_data = in_args.split(' ')
            rc_name = ''
            if len(input_data) >= 2:
                if input_data[0] == 'plugins' :
                    rc_name = 'plugins/plugins'
                elif input_data[0] == 'jails':
                    rc_name = 'jails/jails'
                else:
                    print "Error 2: Did not select correct resource name"
                    print "Ex: resource plugins 1 start"
                    print "Ex: resource plugins 1 stop"
                    print "Ex: resource plugins 1 delete"
                    print "Ex: resource jails 1 start"
                    print "Ex: resource jails 1 stop"
                    print "Ex: resource jails 1 delete"
                    return 0
            else:
                print "help : input arguments"
                print "Ex: resource plugins 1 start"
                print "Ex: resource plugins 1 stop"
                print "Ex: resource plugins 1 delete"
                print "Ex: resource jails 1 start"
                print "Ex: resource jails 1 stop"
                print "Ex: resource jails 1 delete"
                return 0
            call_function = getattr(self,'resources_action')
            call_function(input_data[1:],username=self.username, password=self.password,resource_name=rc_name)
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

    def do_create(self,in_args):
       """ Works on Enbale mode only
    Get the details resources <resources_name> post_json_data
    Eg : create resources account/users post_json_data
    Eg : create resources account/groups post_json_data
    post_json_data is create by set post_json_data
       """
       # Check the invalid Charater as input data
       if in_args in ['?'] or len(in_args) == 0:
           print "Wrong option try '? get'"
           print "Error_1 : Input arguments are wrong"
           print "Try create resources account/users post_json_data "
           print " Eg : create resources account/groups post_json_data"
           return 0

       if self.mode == 'enable':
           try:
               input_data = in_args.split(' ')
               if len(input_data) >= 2:
                   call_function = getattr('resource_create')
               else:
                   print "Error_1 : Input arguments are wrong"
                   print "Try create resources account/users post_json_data "
                   print " Eg : create resources account/groups post_json_data"
                   return 0
           except:
               print "Input error"
           call_function(input_data[1:],username=self.username, password=self.password)
       else :
           print "Only works in Enable mode"

    def do_update(self,in_args):
      """ Works on Enbale mode only
    Get the details resources <resources_name all
    Eg : update resources account/users put_json_data
    Eg : update resources account/groups put_json_data
    put_json_data is create by set put_json_data
      """
      # Check the invalid Charater as input data
      if in_args in ['?'] or len(in_args) == 0:
          print "Wrong option try '? get'"
          print "Error_1 : Input arguments are wrong"
          print "Try update resources account/users put_json_data"
          print " Eg : update resources account/groups put_json_data"
          return 0

      if self.mode == 'enable':
          try:
              input_data = in_args.split(' ')
              if len(input_data) >= 2:
                  call_function = getattr('resource_update')
              else:
                  print "Error_1 : Input arguments are wrong"
                  print "Try get resources <resources_name> all "
                  print "Try update resources account/users put_json_data"
                  print " Eg : update resources account/groups put_json_data"
                  return 0
          except:
              print "Input error"
          call_function(input_data[1:],username=self.username, password=self.password)
      else :
          print "Only works in Enable mode"


    def do_quit(self, args):
        """Quits the program."""
        if self.mode == 'enable':
            self.prompt = self.user_prompt+'>'
            self.mode = 'default'
            print 'Quitting Enable mode'
        elif self.mode == 'variable':
            self.prompt = self.user_prompt+'-enable> '
            self.mode = 'enable'
            print 'Quiting Variable Mode'
        else:
            print "Quitting."
            raise SystemExit

    def do_exit(self, args):
        """Quits the program."""
        if self.mode == 'enable':
            self.prompt = self.user_prompt+'>'
            self.mode = 'default'
            print 'Quitting Enable mode'
        elif self.mode == 'variable':
            self.prompt = self.user_prompt+'-enable> '
            self.mode = 'enable'
            print 'Quiting Variable Mode'
        else:
            print "Quitting."
            raise SystemExit

    def do_EOF(self, line):
        """Control D to exit"""
        return True

    def do_set(self, in_args):
        """ set the variable to for post or put message"""
        if self.mode == 'enable':
            try:
                input_data = in_args.split(' ')
                if len(input_data) == 1:
                    self.line_count = 0
                    self.mode = 'variable'
                    self.variable = input_data[0]
                    self.prompt = self.variable+'_'+str(self.line_count)+'>'
                    self.var_dict[self.variable] = ''
                    print "Added variable values Now and quit using exit command"
                else:
                    print "More than one variable"
            except:
                print "Input error"

    def parseline(self, line):
        if line == 'exit' or line == 'quit':
            ret = Cmd.parseline(self, line)
            return ret
        if self.mode == 'variable':
            data = self.var_dict[self.variable]
            data = data + line
            self.var_dict[self.variable] = data
            #self.prompt = self.variable+'_'+str(self.line_count)+'>'
            ret = Cmd.parseline(self, 'variable')
            return ret
        else:
            ret = Cmd.parseline(self, line)
            return ret

    def do_variable(self,arg):
        self.line_count += 1
        self.prompt = self.variable+'_'+str(self.line_count)+'>'

    def do_show(self,arg):
            if arg in self.var_dict:
                #print json.dumps(self.var_dict[arg])
                if self.is_json(self.var_dict[arg]):
                    print self.var_dict[arg]
                else:
                    print "Data not valid Json"
            else:
                print "Variable Does not Exit"

    # def do_shell(self, line):
    #     """Run a shell command"""
    #     print "running shell command:", line
    #     output = os.popen(line).read()
    #     print output
    #     self.last_output = output

    def do_echo(self, line):
        """Print the input, replacing '$out' with the output of the last shell command"""
        # Obviously not robust
        print line.replace('$out', self.last_output)

    def is_json(self, myjson):
      try:
        json_object = json.loads(myjson)
      except ValueError, e:
        return False
      return True

if __name__ == '__main__':
    prompt = FreenasPrompt()
    if len(sys.argv) > 1:
        prompt.prompt = ' '.join(sys.argv[1:])+"> "
    else :
        prompt.prompt = 'Freenas> '
    prompt.info = 'Welcome to the Freenas shell. \n\
Type help or ? to list commands.'
    prompt.cmdloop(prompt.info)
