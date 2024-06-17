from ckan.lib.uploader import ResourceUpload
from ckan import plugins as p
import os
import hashlib
import mimetypes
import logging
import requests

logging.basicConfig()
log = logging.getLogger(__name__)


class CivityResourceUpload(ResourceUpload):
    """
    This class 'appends' the default ResourceUpload by calculating a hash and setting the correct format
    The hash might be useful later to check if a file actually changed (e.g. an user uploaded a copy of a file with a
    different name) and the format is when a different file type is uploaded (e.g. instead of a CSV it is now a XLS or
    shapefile)
    """

    upload_file = None
    mimetype = None

    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    def __init__(self, resource):
        super(CivityResourceUpload, self).__init__(resource)
        if self.upload_file is not None and resource.get('url_type', None) is 'upload':
            # read the upload_file in chunks of BUF_SIZE and update the sha1 until finished and set the hash
            sha1 = hashlib.sha1()
            while True:
                data = self.upload_file.read(self.BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
            self.upload_file.seek(0, os.SEEK_SET)
            resource['hash'] = sha1.hexdigest()
        elif resource.get('url_type', None) is '' and resource.get('url', None) is not None:
            url = resource.get('url')
            resource['size'] = None
            resource['hash'] = None
            try:
                request = requests.get(url, stream=True)
                hash = hashlib.sha1()
                size = 0
                for chunk in request.iter_content(chunk_size=self.BUF_SIZE):
                    hash.update(chunk)
                    size += len(chunk)
                resource['size'] = size
                resource['hash'] = hash.hexdigest()
            except Exception as e:
                log.warning("Something went wrong when fetching the file. Will continue with hash/size equal None: {}".format(e.message))
                pass
        # if self.mimetype is not None or self.filename is not None or resource.get('url', None) is not None:
        #     # if the filename has an extension use this, otherwise try to guess it from the mimetype. if any of the both
        #     # gave a result set the format
        #     file_extension = None
        #     if self.filename is not None:
        #         filename, file_extension = os.path.splitext(self.filename)
        #     if resource.get('url', None) is not None:
        #         filename, file_extension = os.path.splitext(resource.get('url'))
        #     if file_extension is None and self.mimetype is not None:
        #         file_extension = mimetypes.guess_extension(self.mimetype)
        #     if file_extension:
        #         file_format = file_extension[1:].upper()
        #         resource['format'] = file_format
            # if file_extension == '' and not resource.get('format', None) and p.plugin_loaded('spatial'):
            #     from ckanext.spatial.harvesters.base import guess_resource_format
            #     resource['format'] = guess_resource_format(resource.get('url', None))
