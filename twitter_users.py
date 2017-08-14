import base64
import json
import sys
import pickle
import argparse

'''
   twitter_users.py by Pierfrancesco Ghedini
   Twitter account @pierfghedini
   http://informaticasanitaria.it
   Pithon 3 and Python 2 tested

   Partially adapted from application_only_auth.py
   https://github.com/pabluk/twitter-application-only-auth

   by
   Pablo Seminario
   Rafael Reimberg
   Chris Hawkins

'''

try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, HTTPError

try:
    # For Python 3.0 and later
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib
    from urllib import urlencode

try:
    # For Python 3.4 and later
    from pathlib import Path
except ImportError:
    # Fall back to Python 2's pathlib2
    from pathlib2 import Path

API_ENDPOINT = 'https://api.twitter.com'
API_VERSION = '1.1'
REQUEST_TOKEN_URL = '%s/oauth2/token' % API_ENDPOINT
REQUEST_RATE_LIMIT = '%s/%s/application/rate_limit_status.json' % \
                     (API_ENDPOINT, API_VERSION)

# CONSUMER SECRETS
# To register an app visit https://dev.twitter.com/apps/new
CONSUMER_KEY = 'PUT_HERE_YOUR_CONSUMER_KEY'
CONSUMER_SECRET = 'PUT_HERE_YOUR_CONSUMER_SECRET'

# Common functions

def arg_parse():
    # Command line processing
    parser = argparse.ArgumentParser(description='Browse Twitter Users.')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity',
                    action='store_true')
    parser.add_argument('-u', '--user', help='User to work on', required=True)

    parser.add_argument('-r', '--rate', help='Maximun rate of query',
                    action='store_true')
    
    args = parser.parse_args()

    return (args.user, args.verbose, args.rate)

def read_old_list(user):
    # Getting back the objects:
    myFile = Path(user + '.pickle')
    if myFile.is_file():
        if sys.version_info < (3,0):
            # Python 2.7 compatible
            with open(user + '.pickle', mode="r") as f:
                list_to_read = pickle.load(f)
            return list_to_read
        else:
            with open(user + '.pickle', mode="br") as f:
                list_to_read = pickle.load(f)
            return list_to_read

    else:
        return {}

def save_old_list(user, list_to_save):
    # Saving the objects:
    if sys.version_info < (3,0):
        # Python 2.7 compatible
        with open(user + '.pickle', 'w') as f:
            pickle.dump(list_to_save, f)
    else:
        with open(user + '.pickle', 'wb') as f:
            pickle.dump(list_to_save, f)

class ClientException(Exception):
    pass

class Client(object):
    """This class implements the Twitter's Application-only authentication."""
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = ''

    def request(self, url, verb="GET", body=None):
        """Send an authenticated request to the Twitter API."""
        if not self.access_token:
            self.access_token = self._get_access_token()

        if verb != "GET":
            request = Request(url, urlencode(body).encode('UTF-8'))
        else:
            request = Request(url)

        request.add_header('Authorization', 'Bearer %s' % self.access_token)
        try:
            response = urlopen(request)
        except HTTPError:
            raise ClientException

        raw_data = response.read().decode('utf-8')
        data = json.loads(raw_data)
        return data

    def rate_limit_status(self, resource=''):
        """Returns a dict of rate limits by resource."""
        response = self.request(REQUEST_RATE_LIMIT)
        if resource:
            resource_family = resource.split('/')[1]
            return response['resources'][resource_family][resource]
        return response

    def _get_access_token(self):
        """Obtain a bearer token."""
        bearer_token = '%s:%s' % (self.consumer_key, self.consumer_secret)
        encoded_bearer_token = base64.b64encode(bearer_token.encode('ascii'))
        request = Request(REQUEST_TOKEN_URL)
        request.add_header('Content-Type',
                           'application/x-www-form-urlencoded;charset=UTF-8')
        request.add_header('Authorization',
                           'Basic %s' % encoded_bearer_token.decode('utf-8'))

        request_data = 'grant_type=client_credentials'.encode('ascii')
        if sys.version_info < (3,4):
            request.add_data(request_data)
        else:
            request.data = request_data

        response = urlopen(request)
        raw_data = response.read().decode('utf-8')
        data = json.loads(raw_data)
        return data['access_token']

if __name__ == "__main__":

    # Parse command line
    user, verb, rate = arg_parse()

    # Client Initialization
    client = Client(CONSUMER_KEY, CONSUMER_SECRET)

    if rate:
        print(json.dumps(client.rate_limit_status(), indent=4, sort_keys=True))

    print("##########################################################")
    print("Reading follower...")
    ncursor = -1
    fwer_dict = {}
    fwer_ids = []
    list_ptr = -1
    list_count = 99
    fwer_dict_old = read_old_list(user)

    while ncursor != 0:
        fwer = client.request('https://api.twitter.com/1.1/followers/ids.json?cursor=' + str(ncursor) + '&screen_name=' + user + '&skip_status=true&include_user_entities=false&count=5000')

        print(len(fwer["ids"]))
        for obj in fwer["ids"]:
            if list_count < 99:
                list_count += 1
            else:
                list_count = 0
                list_ptr += 1

            if list_count == 0:
                fwer_ids.append(str(obj))
            else:
                fwer_ids[list_ptr] = fwer_ids[list_ptr] + "," + str(obj)

        ncursor = fwer["next_cursor"]

    # Find Screen_name from ID and store in fwer_dict 
    for obj_ids in fwer_ids:

        lups = client.request('https://api.twitter.com/1.1/users/lookup.json', "POST", {'user_id' : obj_ids, 'include_entities' : 'false'})
        for obj in lups:
            fwer_dict[obj["screen_name"]] = obj["name"]
            #print(str('Follower ' + obj["screen_name"] + " : " + obj["name"]))

    print("##########################################################\n")
    print("##########################################################")
    print("Reading friends...")
    ncursor = -1
    frds_dict = {}

    while ncursor != 0:
        friends = client.request('https://api.twitter.com/1.1/friends/list.json?cursor=' + str(ncursor) + '&screen_name=' + user + '&skip_status=true&include_user_entities=false&count=200')

        print(len(friends["users"]))

        for obj in friends["users"]:
            frds_dict[obj["screen_name"]] = obj["name"]

        ncursor = friends["next_cursor"]

    print("##########################################################\n")

    # Find differences
    len_fwer = len(fwer_dict)
    len_frds = len(frds_dict)

    fwer = set(fwer_dict.keys())
    fwer_old = set(fwer_dict_old.keys())
    fr = set(frds_dict.keys())

    new_list = fwer.difference(fwer_old)
    tot_new = len(new_list)
    if verb:
        for obj in new_list:
            print(str(obj) + " -" + fwer_dict[obj] + "- NEW FOLLOWER")

    print("\n")

    lost_list = fwer_old.difference(fwer)
    tot_lost = len(lost_list)
    if verb:
        for obj in lost_list:
            print(str(obj) + " -" + fwer_dict_old[obj] + "- LOST FOLLOWER")

    print("\nTot: " + str(len_fwer) + " follower.")
    print("New follower: " + str(tot_new))
    print("Lost follower: " + str(tot_lost))
    print("Unchanged follower: " + str(len_fwer - tot_new))

    fr_n_following = fr.difference(fwer)
    n_following = len(fr_n_following)

    print("\nTot: " + str(len_frds) + " friends.")
    print("Friends not following: " + str(n_following) + "\n")

    if verb:
        for obj in fr_n_following:
            print(str(obj) + " -" + frds_dict[obj] + "- Friend not FOLLOWING")

    # Now save current list as the future old list
    save_old_list(user, fwer_dict)
