import os
import sys
from syslog import syslog, LOG_ERR, LOG_WARNING, LOG_INFO

import requests
import json

from flexget import plugin
from flexget.entry import Entry
from flexget.event import event
from flexget.utils.pathscrub import pathscrub
from flexget.utils.template import RenderError


class DownloadStationPlugin:
    """Base class for DownloadStation client."""

    def on_task_start(self, task, config):
        """Fail early if we can't import /configure the DownloadStation client."""
        self.setup_client(config)
        return

    def setup_client(self, config):
        try:
            from synology_api.downloadstation import DownloadStation
        except ImportError as e:
            currentDirectory = os.getcwd()
            errorMessage = "FATAL ERROR: Can't import synology_api.downloadstation. libDirs='%s'" % str(sys.path)
            syslog(LOG_ERR, errorMessage)
            raise plugin.DependencyError("downloadstation", "downloadstation-client", errorMessage)

        config = self.prepare_config(config)
        client = DownloadStation(
                                ip_address=config['hostname'],
                                port=str(config['port']),
                                username=config['username'],
                                password=config['password'],
                                secure=config['secure'],
                                cert_verify=config['verify'],
                                debug=False,
                                interactive_output=False,
        )
        return client


    def prepare_config(self, config):
        config.setdefault('hostname', 'localhost')
        config.setdefault('port', 5001)
        config.setdefault('username', 'admin')
        config.setdefault('secure', True)
        config.setdefault('verify', False)
        config.setdefault('destination', '')
        return config


class OutputDownloadStation(DownloadStationPlugin):
    '''Add magnet links directly to DownloadStation.'''
    schema = {
        'type': 'object',
        'properties': {
            'hostname': {'type': 'string'},
            'port': {'type': 'integer'},
            'username': {'type': 'string'},
            'password': {'type': 'string'},
            'secure': {'type': 'boolean'},
            'verify': {'type': 'boolean'},
            'destination': {'type': 'string'}
        },
        'required': ['hostname', 'username', 'password']
    }

    def prepare_config(self, config):
        config = super().prepare_config(config)
        return config
    
    def __init__(self) -> None:
        self.apiVersion = 2
        return
    
    @plugin.priority(120)
    def on_task_output(self, task, config):
        '''Add torrents to DownloadStation at exit.'''
        config = self.prepare_config(config)
        client = self.setup_client(config)
    # Don't add when learning
        if (task.options.learn):
            return
        if (not task.accepted):
            return
        haveDest = False
        if (config['destination'] != ''):
            haveDest = True
    # Add the torrents:
        for entry in task.accepted:
        # Use magnet links only:
            if (entry.get('url', '').startswith('magnet:')):
                if (haveDest == True):
                    client.create_task(uri=entry['url'], additional_param={'destination': config['destination']})
                else:
                    client.create_task(uri=entry['url'])
        return

@event('plugin.register')
def register_plugin():
    plugin.register(OutputDownloadStation, 'downloadstation', api_ver=2)