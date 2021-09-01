# ------------------------------------------------------------------------------
# Copyright (c) 2021 Tartan Solutions, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
# ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------

import logging
import os
import json

from google.cloud import storage

try:
    from pyupdater.core.uploader import BaseUploader  # type: ignore
except ImportError:  # PyUpdater < 3.0
    from pyupdater.uploader import BaseUploader  # type: ignore

from pyupdater.utils.exceptions import UploaderError

LOG = logging.getLogger(__name__)


class GCSUploader(BaseUploader):
    """Uploader designed to work with GCS"""

    name = 'gcs'
    author = 'Tartan Solutions'

    def set_config(self, config):
        """Step one. Config is previous information, ask user for missing info"""
        bucket_name = config.get('bucket_name')
        bucket_name = self.get_answer(
            'Please enter a bucket name',
            default=bucket_name
        )
        config['bucket_name'] = bucket_name

        bucket_key = config.get('bucket_key')
        bucket_key = self.get_answer(
            'Please enter a bucket key',
            default=bucket_key
        )

        config['bucket_key'] = bucket_key

        gcs_creds_path = config.get('gcs_creds_path')
        if gcs_creds_path is None:
            gcs_creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        gcs_creds_path = self.get_answer(
            'Enter path to Google application credentials JSON file',
            default=gcs_creds_path
        )

        config['gcs_creds_path'] = gcs_creds_path

    def init_config(self, config):
        """Initializes the config for GCS, either pulling from the file set in the environment variable
        or asking the user for credentials."""

        # Try to get bucket from env var
        self.bucket_name = os.environ.get(u'PYU_GCS_BUCKET')
        bucket_name = config.get(u'bucket_name')

        # If there is a bucket name in the repo config we
        # override the env var
        if bucket_name is not None:
            self.bucket_name = bucket_name

        # If nothing is set throw an error
        if self.bucket_name is None:
            raise UploaderError(u'Bucket name is not set',
                                expected=True)

        # Try to get bucket key from env var
        self.bucket_key = os.environ.get(u'PYU_GCS_BUCKET_KEY')
        bucket_key = config.get(u'bucket_key')

        # If there is a bucket key in the repo config we
        # override the env var
        if bucket_key is not None:
            self.bucket_key = bucket_key

        # If nothing is set default to bucket root
        if self.bucket_key is None:
            self.bucket_key = ''

        gcs_creds_path = config.get('gcs_creds_path')
        if gcs_creds_path is None:
            raise UploaderError(u'GCS application credentials path is not set',
                                expected=True)

        # Start by setting config with the GCS creds file
        try:
            with open(gcs_creds_path) as creds_file:
                creds = json.load(creds_file)

            for item in creds:
                if item == 'type':
                    # Special case since type is a reserved keyword
                    self.type_ = creds['type']
                    continue
                self.__setattr__(item, creds[item])
        except:
            LOG.warn(f"Unable to set config with creds file provided in config ({gcs_creds_path}). config: {config}\n Ignoring...")

        required_val_map = {
            'type': self.type_,
            'project_id': self.project_id,
            'private_key_id': self.private_key_id,
            'private_key': self.private_key,
            'client_email': self.client_email,
            'client_id': self.client_id,
            'auth_uri': self.auth_uri,
            'token_uri': self.token_uri,
            'auth_provider_x509_cert_url': self.auth_provider_x509_cert_url,
            'client_x509_cert_url': self.client_x509_cert_url,
        }

        # Ensure we have all the required connection info
        missing_requireds = [v for v in required_val_map if required_val_map[v] is None]
        if len(missing_requireds) > 0:
            raise UploaderError("The following required upload parameters are missing: %s" % ', '.join(missing_requireds))

        self.credentials = required_val_map
        self._connect()

    def _connect(self):
        """Gets a connection to Google Cloud Storage"""
        self.client = storage.Client.from_service_account_info(self.credentials)

    def upload_file(self, filename):
        """Uploads a file to Google Cloud Storage"""

        if not self.bucket_key:
            key = os.path.basename(filename)
        else:
            key = self.bucket_key + '/' + os.path.basename(filename)

        try:
            bucket = self.client.get_bucket(self.bucket_name)
            blob = bucket.blob(key)
            blob.upload_from_filename(filename)
            return True
        except Exception as err:
            LOG.exception('Failed to upload file')
            LOG.debug(err, exc_info=True)

            self._connect()
            return False
