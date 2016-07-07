#!/usr/bin/env python3

import praw
import csv
from datetime import datetime, timedelta

#-------------------------------------------------
#OPTIONS

USERNAME = ''
PASSWORD = ''
user_agent = 'management by /u/kevinosaurus' #user-agent details
csv_list = ['log1.csv', 'log2.csv'] #log1 corresponds to subreddit 1's data, etc. 
sr_list = ['all', 'letschat'] #sr stands for subreddit
limit = 25 #get 25 latest/newest posts from subreddit
POST_LIMIT = 10
TIMER = 60 #seconds
COMMENTS = '''
You have posted similar links too frequently. Please try again later.

I am a bot. Message /u/kevinosaurus for more help!

'''
MOD_TITLE = 'bot report' # you can use the %(old_c)s etc variables in the title too!
MOD_MSG = '''
Bot report
----------
Old thread: %(old_t)s
New thread: %(new_t)s

Old thread creator: %(old_c)s
New thread creator: %(new_c)s

''' # %(old_t)s and such are the variables. You can change the messages and retain the variables.

#-------------------------------------------------

def main():
    r = praw.Reddit(user_agent=user_agent)
    r.login(USERNAME, PASSWORD, disable_warning=True)
    for sr in sr_list:
        subreddit = r.get_subreddit(sr)
        with open(csv_list[sr_list.index(sr)], 'r+') as file:
            fieldnames = ['key', 'username', 'datetime', 'location']
            reader = csv.DictReader(file)
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            newFile = []
            for thread in subreddit.get_new(limit=limit):
                if thread.url != thread.permalink:
                    t_key = thread.url
                    t_user = thread.author
                    t_date = datetime.fromtimestamp(thread.created)
                    t_loc = thread.permalink
                    for row in reader:
                        if row['key'] == t_key:
                            t_exist = True
                            t_csv_key = row['key']
                            t_csv_date = row['datetime']
                            t_csv_user = row['username']
                        else:
                            t_exist = False
                    if t_exist:
                        if (datetime.fromtimestamp(t_csv_date) + timedelta(days=POST_LIMIT)) < datetime.now():
                            thread.add_comment(COMMENTS)
                            thread.delete
                        else:
                            for row2 in reader:
                                if t_key not in newFile && t_key != row['key']:
                                    newFile.append(row2)
                            writer.writerows(newFile)
                            writer.writerow({'key': t_key, 'username': t_user, 'datetime': t_date, 'location': t_loc})
                        if t_csv_user != t_user:
                            MOD_TITLE = MOD_TITLE % {'old_t': t_csv_key, 'new_t': t_key, 'old_c': t_csv_user, 'new_c': t_user}
                            MOD_MSG = MOD_MSG % {'old_t': t_csv_key, 'new_t': t_key, 'old_c': t_csv_user, 'new_c': t_user}
                            r.send_message('/r/'+sr, MOD_TITLE, MOD_MSG)
                    else:
                        writer.writerow({'key': t_key, 'username': t_user, 'datetime': t_date, 'location': t_loc})

while True:
    main()
    time.sleep(TIMER)
                                
