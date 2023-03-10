import os
import sys
from syslog import syslog, LOG_ERR, LOG_WARNING, LOG_INFO

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
            errorMessage = "FATAL ERROR: Can't import synology_api.downloadstation: '%s'. libDirs='%s'" % (str(e.args), str(sys.path))
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
                                dsm_version=config['dsm_version'],
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
        config.setdefault('dsm_version', 7)
        return config


class OutputDownloadStation(DownloadStationPlugin):
    '''Add links directly to DownloadStation.'''
    schema = {
        'type': 'object',
        'properties': {
            'hostname': {'type': 'string'},
            'port': {'type': 'integer'},
            'username': {'type': 'string'},
            'password': {'type': 'string'},
            'secure': {'type': 'boolean'},
            'verify': {'type': 'boolean'},
            'destination': {'type': 'string'},
            'dsm_version': {'type': 'integer'}
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
        # syslog(LOG_INFO, "on_task_output called.")
        config = self.prepare_config(config)
        # syslog(LOG_INFO, "config= '%s'" % (str(config)))
        client = self.setup_client(config)
    # Don't add when learning
        if (task.options.learn):
            # syslog(LOG_INFO, "task.options.learn == True, pass.")
            return
    # If nothing accepted do nothing:
        if (not task.accepted):
            syslog(LOG_INFO, "No accepted tasks, pass.")
            return
        haveDest = False
        if (config['destination'] != ''):
            haveDest = True
        # syslog(LOG_INFO, "task = '%s'" % (str(task)))

    # Add the torrents:
        for entry in task.accepted:
            # syslog(LOG_INFO, str(entry))
            # for key in entry.keys():
                # syslog(LOG_INFO, "Key %s = %s" % (key, str(entry[key])))
            # url1 = entry.get('url', '')
            # url2 = entry['url']
            # syslog(LOG_INFO, "url1=%s"%url1)
            # syslog(LOG_INFO, "url2=%s"%url2)
            # syslog(LOG_INFO, str(dir(entry)))
            # syslog(LOG_INFO, str(help(entry)))
            # syslog(LOG_INFO, "URL='%s'" % (entry['url']))

            # syslog(LOG_INFO, "haveDest=%s" % (str(haveDest)))
            if (haveDest == True):
                response = client.create_task(uri=entry['url'], additional_param={'destination': config['destination']})
                # syslog(LOG_INFO, str(response))
            else:
                response = client.create_task(uri=entry['url'])
                # syslog(LOG_INFO, str(response))
            return

@event('plugin.register')
def register_plugin():
    plugin.register(OutputDownloadStation, 'downloadstation', api_ver=2)