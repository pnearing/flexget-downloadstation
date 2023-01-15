
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
        self.setup_clent(config)
        return

    def setup_client(self, config):
        try:
            from synology_api.downloadstation import DownloadStation
        except ImportError as e:
            errorMessage = "FATAL ERROR: Can't import synology_api.downloadstation."
            syslog(LOG_ERR, errorMessage)
            raise plugin.DependencyError("downloadstation", "downloadstation-client", "synology_api is required but not found.")

        config = self.prepare_config(config)
        return DownloadStation()


    def prepare_config(self, config):
        config.setdefault('hostname', 'localhost')
        config.setdefault('port', 5001)
        config.setdefault('username', 'admin')
        config.setdefault('secure', True)
        config.setdefault('verify', False)
        return config
