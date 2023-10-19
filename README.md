# flexget-downloadstation
 DownloadStation client plugin for flexget

## Requirements:
- Synology NAS with DownloadStation. (Tested using DSM 6.2.4, but should work with DSM 6 and 7)
- synology pyhton API. Which can be found at: https://github.com/N4S4/synology-api
- flexget.

## Installation:
- install flexget
- install synology-api; On DSM it's best to install the library in /[INSTALL_VOLUME]/@appstore/flexget/env/lib/python3.11/site-packages/, and make sure the ownerships are set to 'sc-flexget:synocommunity'.
- Move downloadstation.py to flexgetConfigPath/plugins/client. On most linux systems this can be found at $HOME/.config/flexget/. On DSM this can be found at /var/packages/flexget/var/. (Thanks to  once375ml for that info.)

## Configuration options:
- hostname: The hostname of the NAS
- port: The port number to connect to
- secure: True -> use SSL.
- verify: True -> Verify SSL certificate. Most nas's use self-signed certificates, and this would normally be false.
- username: The username to connect with.
- password: The password to connect with.
- dsm_version: The version number of DSM on the nas. Note: for version 6.2.4, set this to 6, for 7.1 etc, set this to 7

## Configuration sample:
templates:
  tv:
    downloadstation:
      hostname: localhost
      port: 5001
      secure: true
      verify: false
      username: admin
      password: ChangeMe
      dsm_version: 6

    series_premiere:
      quality: sdtv+

tasks:
  eztv:
    rss: https://eztv.re/ezrss.xml
    quality: sdtv+
    template: tv

