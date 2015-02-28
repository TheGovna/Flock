from flask import Flask, render_template, request, redirect, url_for
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
YELP_SEARCH_URL = 'http://api.yelp.com/v2/search'
YELP_BUSINESS_URL = 'http://api.yelp.com/v2/business/'

mostRecentlySelectedBusiness = None

app = Flask(__name__)
app.config.from_object(__name__)
connection = Connection(app.config['MONGODB_HOST'], app.config['MONGODB_PORT'])

fakeFriends = {'friends': [
    {'name': 'Melissa Thai', 'email': 'thaimp@rose-hulman.edu', 'phone': '7038811188'},
    {'name': 'Chris Budo', 'email': 'chris@rose-hulman.edu', 'phone': '1111111111'},
    {'name': 'Jeremiah Goist', 'email': 'jeremiah@rose-hulman.edu', 'phone': '2222222222'},
    {'name': 'Brooke Brown', 'email': 'brooke@rose-hulman.edu', 'phone': '3333333333'}]
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
    return render_template('results.html',
                            search_term=search_term,
                            location=location,
                            businesses=json_response['businesses'])

@app.route('/invite/<business_id>')
def invite_friends(business_id):
    api_url = YELP_BUSINESS_URL + business_id
    signed_url = sign_url(api_url)
    response = requests.get(signed_url)
    json_response = json.loads(response.text)
    print(json_response)
    return render_template('invite.html', business_name=json_response['name'], friends=fakeFriends['friends'])

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
