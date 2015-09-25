import requests, json
from datetime import date
import calendar

class User:
    def __init__(self, id, name, email):
        self.id     = id
        self.name   = name
        self.email  = email

    def __str__(self):
        return '{} {} {}'.format(self.id, self.name, self.email)

    def __repr__(self):
        return self.__str__()

class Harvest:
    def __init__(self, url, email, pw):
        self.url    = url
        self.email  = email
        self.pw     = pw

    def _json_req(self, url):
        u = '{}{}'.format(self.url, url)
        # print u
        r = requests.get(u, auth=(self.email, self.pw), headers={'Accept': 'application/json'})
        # print r.status_code
        return r.json()

    def get_users(self):
        users_json = self._json_req('/people')
        users = [usr['user'] for usr in users_json if usr['user']['is_active']]
        users = [User(user['id'], ' '.join((user['first_name'], user['last_name'])).encode('utf-8').strip(), user['email']) for user in users]
        return users

    def get_week(self):
        return self._json_req('/time/week')

    def get_user_entries(self, user, date_from, date_to):
        f = date_from.strftime("%Y%m%d")
        t = date_to.strftime("%Y%m%d")
        return self._json_req('/people/{}/entries?from={}&to={}'.format(user.id, f, t))

    def get_user_monthly_hours(self, user, year, month):
        entries = self.get_user_entries(user, date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1]))
        hours = sum([entry['day_entry']['hours'] for entry in entries])
        return hours

def count_reference_hours(year, month):
    """
    Count how many reported hours there should be
    in the given month. Each Mon-Fri should be
    reported as 8 hours.
    """

    ref_hours = 0
    for d in range(calendar.monthrange(year, month)[1]):
        weekday = date(year, month, d+1).weekday()
        ref_hours += 8 if weekday < 5 else 0
    return ref_hours

# import config
with open('config.json') as f:
    cfg = json.load(f)

hv = Harvest(cfg['url'], cfg['email'], cfg['password'])
users = hv.get_users()

# output csv
print 'Month,Reference_hours,{}'.format(','.join([user.name for user in users]))

# check jan - aug
for month in range(1, 9):
    print '{},{},{}'.format(
            calendar.month_name[month],
            count_reference_hours(2015, month),
            ','.join([str(hv.get_user_monthly_hours(user, 2015, month)) for user in users]))
