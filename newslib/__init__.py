from logging import getLogger

import requests

logger = getLogger(__name__)

requests.urllib3.disable_warnings()
