"""
Script to upload firmware to Cisco Viptela vManage.

Author: Santhosh Balasa
"""

import sys
import logging
import requests


from requests.exceptions import ConnectionError
from http.client import HTTPConnection

logger = logging.getLogger("urllib3")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

HTTPConnection.debuglevel = 1


# Global
vmanage_session = None
vmanage_host = "192.168.245.110"
vmanage_port = "8443"
vmanage_user = "viptela_user"
vmanage_pass = "viptela_passwrd_2020"
firmware_path = "/home/viptela-19.2.2-mips64.tar.gz"
logger.name = __file__
requests.packages.urllib3.disable_warnings()


class RestAPI:
    def __init__(self, vmanage_host, vmanage_port, username, password):
        self.vmanage_host = vmanage_host
        self.vmanage_port = vmanage_port
        self.session = requests.cookies.RequestsCookieJar()
        self.login(username, password)

    def login(self, username, password):
        """
        Function to login to vManage
        Args:
            username (str): User name of vManage
            password (str): Password of vManage
        """
        logger.debug("Logging into Viptela SD-WAN vManage")
        # Format data for loginForm
        login_data = {"j_username": username, "j_password": password}

        # Url for posting login data
        base_url = f"https://{self.vmanage_host}:{self.vmanage_port}"
        login_url = base_url + "/j_security_check"
        logger.info(login_url)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
        }

        sess = requests.Session()
        login_response = sess.post(
            url=login_url,
            data=login_data,
            verify=False,
            headers=headers,
            timeout=100,
        )

        if b"<html>" in login_response.content:
            logger.info("Login Failed")
            sys.exit(0)

        # update token to session headers
        self.session[self.vmanage_host] = sess

    def post_request(self, mount_point, payload, files):
        """
        Function to perform POST call to vManage
        Args:
            mount_point (str): API url
            payload (dict): Payload body to be passed
            files (list): Firmware path
        """
        url = f"https://{self.vmanage_host}:{self.vmanage_port}/{mount_point}"
        logger.debug(f"Calling POST {url}")
        response = self.session[self.vmanage_host].post(
            url=url,
            data=payload,
            files=files,
            headers=None,
            verify=False,
            timeout=100,
        )
        if response.status_code == "200":
            return response.text
        else:
            return response.reason


if __name__ == "__main__":
    vmanage_session = RestAPI(vmanage_host, vmanage_port, vmanage_user, vmanage_pass)
    payload = {"name": firmware_path.split("/")[-1]}
    files = [("filename", open(firmware_path, "rb"))]
    response = vmanage_session.post_request(
        "dataservice/device/action/software/package",
        payload=payload,
        files=files,
    )
    print(response)
