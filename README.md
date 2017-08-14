# twitter_users.py
Command Line tool to browse Twitter Users

Python script, tested for Python 2.7 and Python 3.0 and later 

## Credits
       Partially adapted from application_only_auth.py
  
       https://github.com/pabluk/twitter-application-only-auth

       by
       Pablo Seminario
       Rafael Reimberg
       Chris Hawkins

## Usage
At the comand line execute:

    python twitter_users.py -h

to get the following usage notes:

    usage: twitter_users.py [-h] [-v] -u USER [-r]
    Browse Twitter Users.
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Increase output verbosity
      -u USER, --user USER  User to work on
      -r, --rate            Maximun rate of query
  
## Get your Twitter keys to autenticate
In order to use the script you have to obtain keys from Twitter.

Go to "Twitter Application Management" at https://apps.twitter.com/

Sign in and follow instructions to accreditate your APP.

Modify the scrpit with the keys you obtained:

    CONSUMER_KEY = 'PUT_HERE_YOUR_CONSUMER_KEY'
    CONSUMER_SECRET = 'PUT_HERE_YOUR_CONSUMER_SECRET'
    
## Features

The tool, by means of Twitter REST API, gets Followers and Friends of a given user. it provides the New followers and the Lost followers since the previous run.

It gives also the Not Following Friends: the Friends not following the given user.

    Tot: 520 follower.
    New follower: 10
    Lost follower: 1
    Unchanged follower: 509
    
    Tot: 795 friends.
    Friends not following: 355

In verbose mode, the tool gives the lists of New Followers, of Lost Followers and Not Following Friends.
