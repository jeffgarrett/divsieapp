from google.appengine.api import urlfetch
from divsieapp.models import Secret
import json
import logging
import os
import urllib


class OAuth2Error:
    def __init__(self, msg):
        self.message = msg

class GoogleOAuth2:
    __scopes = {
        "email": "https://www.googleapis.com/auth/userinfo.email",
        "profile": "https://www.googleapis.com/auth/userinfo.profile"
    }

    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/auth"
    ACCESS_TOKEN_ENDPOINT = "https://accounts.google.com/o/oauth2/token"
    USERINFO_ENDPOINT = 'https://www.googleapis.com/oauth2/v1/userinfo'

    def __init__(self, redirect_uri, scopes=["email"], prompt=None, offline=False, state=None):
        self.redirect_uri = redirect_uri
        self.scope = " ".join([self.__scopes[x] for x in scopes])
        self.response_type = "code"
        self.prompt = prompt
        self.offline = offline
        if offline:
            self.access_type = "offline"
        else:
            self.access_type = "online"
        self.state = state

    # Step 1: User visits the auth_url.
    def get_auth_url(self):
        params = {
            "response_type": self.response_type,
            "client_id": Secret.get_secret('google_client_id').value, 
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "access_type": self.access_type
        }
        if self.prompt:
            params["prompt"] = self.prompt
        if self.state:
            params["state"] = self.state
        auth_url = self.AUTH_ENDPOINT + '?' + urllib.urlencode(params)
        logging.info("OAuth2: Creating auth_url: %s" % (auth_url,))
        return auth_url

    # Step 2: OAuth2 calls back to our redirect_uri.
    def handle_redirect_uri(self, request):
        # If the user disapproves, we are alerted here.
        error = request.GET.get("error")
        if error:
            logging.warning("OAuth2: Error: %s" % (error,))
            raise OAuth2Error(error)

        authorization_code = request.GET.get("code")

        payload = {
            "code": authorization_code,
            "client_id": Secret.get_secret('google_client_id').value,
            "client_secret": Secret.get_secret('google_client_secret').value,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        encoded_payload = urllib.urlencode(payload)

        logging.info("OAuth2: Requesting access token. Payload: %s" % (payload,))
        result = json.loads(urlfetch.fetch(url=self.ACCESS_TOKEN_ENDPOINT,
                                           payload=encoded_payload,
                                           method=urlfetch.POST,
                                           headers={"Content-Type": "application/x-www-form-urlencoded"}).content)
        logging.info("OAuth2: Access token response: %s" % (result,))
        error = result.get("error")
        if error:
            logging.error("OAuth2: Error: %s" % (error,))
            raise OAuth2Error(error)

        self.access_token = result['access_token']
        # unverified emails?
        # persist tokens
        # return tokens

    # Step 3: request userinfo
    def request_userinfo(self):
        userinfo = json.loads(urlfetch.fetch(self.USERINFO_ENDPOINT,
                              headers={'Authorization': 'Bearer ' + self.access_token}).content)
        logging.info("OAuth2: User info is: %s" % (userinfo,))
        error = userinfo.get("error")
        if error:
            logging.error("OAuth2: Error: %s" % (error,))
            raise OAuth2Error(error)
        return userinfo
