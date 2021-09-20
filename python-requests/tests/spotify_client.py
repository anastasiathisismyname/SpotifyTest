import base64
import datetime
from urllib.parse import urlencode
import requests



class SpotifyAPI:
    access_token = None
    access_token_expires = datetime.datetime.now()
    token_url = "https://accounts.spotify.com/api/token"
    base_url = "api.spotify.com"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_headers = { "Authorization": f"Basic {self.get_client_credentials()}" }
        self.token_data = { "grant_type": "client_credentials" }
        self.access_token = self.get_access_token()
        self.resource_header = { "Authorization": f"Bearer {self.access_token}" }

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        if self.client_secret is None or self.client_id is None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def perform_auth(self):
        r = requests.post(self.token_url, data=self.token_data, headers=self.token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client due to: {r.status_code}: {r.text}")
        data = r.json()
        access_token = data['access_token']
        expires_in = data['expires_in']  # seconds
        expires = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        return True

    def get_access_token(self):
        now = datetime.datetime.now()
        if self.access_token_expire < now:
            self.perform_auth()
            return self.get_access_token()
        elif self.get_access is None:
            self.perform_auth()
            return self.get_access_token()
        return self.get_access

    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        endpoint = f"https://{base_url}/{version}/{resource_type}/{lookup_id}"
        r = requests.get(endpoint, headers=self.resource_header)
        if r.status_code not in range(200, 299):
            print(f"Actual status code returned: {r.status_code}")
            return {}
        return r.json()

    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')

    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')

    def base_search(self, query_params):  # type
        r = requests.get(f"{self.base_url}/v1/search?{query_params}", headers=self.resource_header)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def search(self, query=None, operator=None, operator_query=None, search_type='artist'):
        if query is None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
        if operator and operator_query:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        print(query_params)
        return self.base_search(query_params)
