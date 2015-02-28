import oauth2
OAUTH_CONSUMER_KEY = 'uL6xCtuJTiEFCVrsf6ubbQ'
OAUTH_CONSUMER_SECRET = 'xfBEGe2ZFJJmyWnWpBhiPA4cMDo'
OAUTH_TOKEN = 'AnpMbjAY-5MIm8yCT5oZ_AXMx2rEGocU'
OAUTH_TOKEN_SECRET = 'wbYbOmAZflFnxLDNjH9vJAyqUGg'


def sign_url(url):
    consumer = oauth2.Consumer(OAUTH_CONSUMER_KEY, OAUTH_CONSUMER_SECRET)
    token = oauth2.Token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    oauth_request = oauth2.Request('GET', url, {})
    oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
                          'oauth_timestamp': oauth2.generate_timestamp(),
                          'oauth_token': token.key,
                          'oauth_consumer_key': OAUTH_CONSUMER_KEY})
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(),
                               consumer,
                               token)
    return oauth_request.to_url()