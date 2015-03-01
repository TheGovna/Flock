from flask import Flask, render_template, request, redirect, url_for
from twilio.rest import TwilioRestClient
import urllib
import requests
import json
import datetime
from oauth import sign_url

from mongokit import Connection, Document, ObjectId
import oauth

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DEBUG = True
SECRET_KEY = 'development key'

MAILJET_ENDPOINT = "http://pebblewebultranuvo.azurewebsites.net/apis/jetjoin?"
MAILJET_TOMAIL = "tomail="
MAILJET_FROMMAIL = "fromMail=budocf@rose-hulman.edu"
MAILJET_BUSINESS = "business="


TWILIO_ACCOUNT_SID = "ACcdeba5687e73b2f0018fe8b7004e6fc8"
TWILIO_AUTH_TOKEN = "1e389c71315f88b00945ed9499dea847"
TWILIO_NUMBER = "5714512210"
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

YELP_SEARCH_URL = 'http://api.yelp.com/v2/search'
YELP_BUSINESS_URL = 'http://api.yelp.com/v2/business/'

mostRecentlySelectedBusiness = None

app = Flask(__name__)
app.config.from_object(__name__)
connection = Connection(app.config['MONGODB_HOST'], app.config['MONGODB_PORT'])

fakeFriends = {'friends': [
    {'name': 'Melissa Thai', 'email': 'thaimp@rose-hulman.edu', 'phone': '7038811188'},
    {'name': 'Chris Budo', 'email': 'chris@rose-hulman.edu', 'phone': '5135442427'},
    {'name': 'Jeremiah Goist', 'email': 'jeremiah@rose-hulman.edu', 'phone': '2539730487'},
    {'name': 'Brooke Brown', 'email': 'brooke@rose-hulman.edu', 'phone': '8122437113'}]
}

class Entry(Document):
    use_dot_notation = True

    structure = {
        'name': basestring,
        'url': basestring,
        'created_at': datetime.datetime,
        'phone_number': basestring,
        'address': basestring,
        'categories': [basestring]
    }

    default_values = {'created_at': datetime.datetime.utcnow}

    def id(self):
        return self._id

    def __repr__(self):
        return '<Entry %s>' % self['name']

connection.register([Entry])
collection = connection['squeak'].entries

@app.route('/')
def index():
    entries = list(collection.Entry.find())
    return render_template('index.html', saved_entries=entries)

@app.route('/save', methods=['POST'])
def save_entry():
    new_entry = collection.Entry()
    new_entry.name = request.form['name']
    new_entry.url = request.form['url']
    new_entry.phone_number = request.form['phone_number']
    new_entry.address = request.form['address']
    new_entry.categories = request.form.getlist('categories')
    new_entry.save()

    return redirect(url_for('index'))

@app.route('/results', methods=['POST'])
def yelp_search():
    search_term = request.form['term']
    location = request.form['location']

    data = {
        'term': search_term,
        'location': location
    }
    query_string = urllib.urlencode(data)
    api_url = '%s?%s' % (app.config['YELP_SEARCH_URL'], query_string)
    signed_url = sign_url(api_url)
    response = requests.get(signed_url)
    json_response = json.loads(response.text)
    businesses=json_response['businesses']
    if businesses != None:
        return render_template('results.html',
                            search_term=search_term,
                            location=location,
                            businesses=businesses)
    else:
        return render_template('index.html')

@app.route('/invite/<business_id>')
def invite_friends(business_id):
    api_url = YELP_BUSINESS_URL + business_id
    signed_url = sign_url(api_url)
    response = requests.get(signed_url)
    json_response = json.loads(response.text)
    # print(json_response)
    return render_template('invite.html', business_name=json_response['name'], business_id=json_response['id'], friends=fakeFriends['friends'])

def text_friend(business_name, friend_number):
    message = client.messages.create(body="I would love to go to " + business_name + " with you!",
    to=friend_number,    # Replace with your phone number
    from_=TWILIO_NUMBER) # Replace with your Twilio number
    return business_name + ", " + friend_number

@app.route('/notify/<business_id>/<business_name>', methods=['POST'])
def notify_checked_friends(business_id, business_name):
    friends_to_text = request.form.getlist("friend")
    print("FRIENDS TO TEXT:")
    print(friends_to_text)
    for friend_to_text in friends_to_text:
        for friend in fakeFriends['friends']:
            if friend_to_text == friend['name']:
                global MAILJET_TOMAIL
                global MAILJET_BUSINESS
                MAILJET_TOMAIL += friend['email']
                MAILJET_BUSINESS += business_id
                requests.post(MAILJET_ENDPOINT + MAILJET_TOMAIL + "&" + MAILJET_FROMMAIL + "&" + MAILJET_BUSINESS);
                print(friend['name'] + " " + friend['phone'] + " " + MAILJET_ENDPOINT + MAILJET_TOMAIL + "&" + MAILJET_FROMMAIL + "&" + MAILJET_BUSINESS)
                text_friend(business_name, friend['phone'])
    return redirect(url_for('index'))

def create_oauth_url(url):
    consumer = oauth.Consumer(app.config['OAUTH_CONSUMER_KEY'],
                               app.config['OAUTH_CONSUMER_SECRET'])
    token = oauth.Token(app.config['OAUTH_TOKEN'],
                        app.config['OAUTH_TOKEN_SECRET'])
    oauth_request = oauth.Request('GET', url, {})
    oauth_request.update({'oauth_nonce': oauth.generate_nonce(),
                          'oauth_timestamp': oauth.generate_timestamp(),
                          'oauth_token': token.key,
                          'oauth_consumer_key': app.config['OAUTH_CONSUMER_KEY']})
    oauth_request.sign_request(oauth.SignatureMethod_HMAC_SHA1(),
                               consumer,
                               token)
    return oauth_request.to_url()

if __name__ == '__main__':
    app.run()
