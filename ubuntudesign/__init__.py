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

    def get(self, file_path):
        asset_data_url = urljoin(self.server_url, '{0}/info'.format(file_path))

        api_response = self._request('get', asset_data_url)

        return self._format_asset(api_response.json())

    def all(self, search=''):
        url = self.server_url

        # Search, if requested
        if search:
            url += '?q={0}'.format(search)

        api_response = self._request('get', url)

        return self._format_assets(api_response.json())

    def create(self, asset_content, friendly_name, tags='', optimize=False):
        """
        Create an asset on the server
        You must provide the asset with a friendly name
        for the server to generate a path from.
        """

        return self._create_asset({
            'asset': b64encode(asset_content),
            'friendly-name': friendly_name,
            'tags': tags,
            'optimize': optimize,
            'type': 'base64'
        })

    def create_at_path(self, asset_content, url_path, tags=''):
        """
        Create asset at a specific URL path on the server
        """

        return self._create_asset({
            'asset': b64encode(asset_content),
            'url-path': url_path,
            'tags': tags,
            'type': 'base64'
        })

    def update(self, file_path, tags):
        asset_url = urljoin(self.server_url, file_path)

        api_response = self._request(
            'put',
            asset_url,
            data={
                'tags': tags
            }
        )

        return self._format_asset(api_response.json())

    def _create_asset(self, asset_data):
        api_response = self._request(
            'post',
            self.server_url,
            data=asset_data,
            allowed_errors=[409]
        )

        response = api_response.json()

        if api_response.status_code < 300:
            response = self._format_asset(response)

        return response

    def _format_assets(self, data):
        formatted_data = []

        for datum in data:
            formatted_data.append(self._format_asset(datum))

        return formatted_data

    def _format_asset(self, datum):
        mimetype = mimetypes.guess_type(datum["file_path"])[0]

        return {
            "file_path": datum["file_path"],
            "tags": datum["tags"],
            "url": urljoin(self.server_url, datum["file_path"]),
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
