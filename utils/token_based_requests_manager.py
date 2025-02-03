import logging
import time

import jwt
import requests

logger = logging.getLogger(__name__)


class TokenBasedRequests:
    def __init__(
        self,
        authentication_url,
        auth_credentials_dict,
        headers=None,
        token_prefix="Bearer ",
        accepted_status_codes=None,
    ):
        if accepted_status_codes is None:
            accepted_status_codes = [200, 201, 202, 203, 204]
        if headers is None:
            headers = {}
        self.authentication_url = authentication_url
        self.auth_credentials = auth_credentials_dict
        self.accepted_status_codes = accepted_status_codes
        self.token_prefix = token_prefix
        self.headers = headers
        self.token_expiration = None

    def post(self, endpoint_url, data, data_to_log_fields=None, extra_headers=None, timeout=None):
        """
        data_to_log_fields: fields from data dict that should be logged if the response status code is not in
            accepted_status_codes
        """
        if extra_headers is None:
            extra_headers = {}
        if data_to_log_fields is None:
            data_to_log_fields = []
        return self.__request(endpoint_url, data, data_to_log_fields, extra_headers=extra_headers)

    def get(self, endpoint_url, extra_headers=None, params=None, timeout=None):
        """
        data_to_log_fields: fields from data dict that should be logged if the response status code is not in
            accepted_status_codes
        """
        if extra_headers is None:
            extra_headers = {}
        return self.__request(endpoint_url, params, [], "GET", extra_headers=extra_headers, timeout=timeout)

    def delete(self, endpoint_url, extra_headers=None, params=None, timeout=None):
        """
        Performs a DELETE request.
        """
        if extra_headers is None:
            extra_headers = {}
        return self.__request(endpoint_url, params, [], "DELETE", extra_headers=extra_headers, timeout=timeout)

    def __call_requests(self, endpoint_url, data, method="POST", headers=None, timeout=None):
        if headers is None:
            headers = {}
        if method == "POST":
            return requests.post(endpoint_url, verify=True, json=data, headers=headers, timeout=timeout)
        elif method == "GET":
            return requests.get(endpoint_url, verify=True, headers=headers, params=data, timeout=timeout)
        elif method == "DELETE":
            return requests.delete(endpoint_url, verify=True, headers=headers, params=data, timeout=timeout)
        else:
            raise NotImplementedError("only POST, GET and DELETE methods are implemented")

    def __request(self, endpoint_url, data, data_to_log_fields, method="POST", extra_headers=None, timeout=None):
        if extra_headers is None:
            extra_headers = {}
        self.check_token()
        headers = dict(self.headers)
        headers.update(extra_headers)
        result = self.__call_requests(endpoint_url, data, method, headers, timeout)
        if result.status_code not in self.accepted_status_codes:
            extra_data = ""
            for key in data_to_log_fields:
                # get data to log from data
                extra_data = key + " = " + str(data[key]) + ", "
            error_text = "Data API CashIO error while requesting url:%s, status_code:%s,response text:%s" % (
                result.url,
                result.status_code,
                result.text,
            )
            if extra_data:
                error_text = error_text + ", extra information: " + extra_data
            logger.error(error_text)
        return result

    def update_token(self):
        try:
            result = requests.post(self.authentication_url, verify=True, json=self.auth_credentials)
            if result.status_code == 200:
                self.headers.update({"Authorization": self.token_prefix + str(result.json()["id_token"])})
                self.token_expiration = jwt.decode(result.json()["id_token"], options={"verify_signature": False})[
                    "exp"
                ]
            else:
                logger.error("getting Authentication token Failed for %s" % self.authentication_url)
        except Exception as e:
            logger.error(
                "Couldn't authenticate reach %s for authentication error details: %s", self.authentication_url, e
            )

    def check_token(self):
        if not self.token_expiration or self.token_expiration < int(time.time()) + 10:
            self.update_token()
