import json
import datetime
from random import randint

with open('tests/data/user.json') as f:
    users = json.load(f)

with open('tests/data/speech.json') as f:
    speeches = json.load(f)
    date_format = '%Y-%m-%d %H:%M:%S'
    for speech in speeches:
        speech['start_time'] = datetime.datetime.strptime(speech['start_time'], date_format)
        speech['end_time'] = datetime.datetime.strptime(speech['end_time'], date_format)

with open('tests/data/role.json') as f:
    roles = json.load(f)

with open('tests/data/user_speech.json') as f:
    user_speeches = json.load(f)
    len_users = len(users) - 1
    len_speeches = len(speeches) - 1
    len_roles = len(roles) - 1
    used = {}
    for user_speech in user_speeches:
        i_users = randint(0, len_users)
        i_speeches = randint(0, len_speeches)
        i_roles = randint(0, len_roles)

        while 'uid' not in users[i_users].keys() or not users[i_users]['uid']:
            i_users = randint(0, len_users)

        if users[i_users]['uid'] not in used.keys():
            used[users[i_users]['uid']] = set()

        while ('key' not in speeches[i_speeches].keys() or not speeches[i_speeches]['key'] or
               speeches[i_speeches]['key'] in used[users[i_users]['uid']]):
            i_speeches = randint(0, len_speeches)

        used[users[i_users]['uid']].add(speeches[i_speeches]['key'])

        while 'value' not in roles[i_roles].keys() or not roles[i_roles]['value']:
            i_roles = randint(0, len_roles)
        user_speech['uid_key'] = f'{users[i_users]["uid"]}_{speeches[i_speeches]["key"]}'
        user_speech['uid'] = users[i_users]['uid']
        user_speech['key'] = speeches[i_speeches]['key']
        user_speech['role'] = roles[i_roles]['value']

with open('tests/data/token.json') as f:
    tokens = json.load(f)
    tokens[0]['uid'] = users[1]['uid']
    for i in range(1, len(tokens)):
        if users[i]['uid']:
            tokens[i]['uid'] = users[i]['uid']
        else:
            tokens[i]['uid'] = users[1]['uid']
