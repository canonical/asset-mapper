# System
import mimetypes
from base64 import b64encode
from urlparse import urljoin

# Modules
import requests


class AssetMapper:
    """
    Map data from the Assets API into model objects
    """

    auth_token = ""
    server_url = ""
    image_types = ["image/png", "image/jpeg", "image/svg+xml", "image/gif"]

    def __init__(self, server_url, auth_token):
        self.server_url = server_url
        self.auth_token = auth_token

    def get(self, filename):
        asset_data_url = urljoin(self.server_url, '{0}.json'.format(filename))

        api_response = self._request('get', asset_data_url)

        return self._format_asset(api_response.json())

    def all(self, search=''):
        url = self.server_url

        # Search, if requested
        if search:
            url += '?q={0}'.format(search)

        api_response = self._request('get', url)

        return self._format_assets(api_response.json())

    def create(self, asset_content, filename, tags):
        api_response = self._request(
            'post',
            self.server_url,
            data={
                'asset': b64encode(asset_content),
                'filename': filename,
                'tags': tags,
                'type': 'base64'
            },
            allowed_errors=[409]
        )

        response = api_response.json()

        if api_response.status_code < 300:
            response = self._format_asset(response)

        return response

    def update(self, filename, tags):
        asset_url = urljoin(self.server_url, filename)

        api_response = self._request(
            'put',
            asset_url,
            data={
                'tags': tags
            }
        )

        return self._format_asset(api_response.json())

    def _format_assets(self, data):
        formatted_data = []

        for datum in data:
            formatted_data.append(self._format_asset(datum))

        return formatted_data

    def _format_asset(self, datum):
        mimetype = mimetypes.guess_type(datum["filename"])[0]

        return {
            "filename": datum["filename"],
            "tags": datum["tags"],
            "url": urljoin(self.server_url, datum["filename"]),
            "image": mimetype in self.image_types,
            "created": datum["created"]
        }

    def _request(
        self, method, url,
        data=None, headers={}, allowed_errors=[]
    ):
        if self.auth_token:
            headers['Authorization'] = 'token {0}'.format(self.auth_token)

        response = requests.request(
            method=method,
            url=url,
            data=data,
            headers=headers
        )

        # Throw an error if we have a bad status
        if response.status_code not in allowed_errors:
            response.raise_for_status()

        return response
