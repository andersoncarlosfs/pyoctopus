from http import HTTPStatus
from http.client import HTTPSConnection
from json import dumps
from json import loads
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union


from pyoctopus.controller.utils.http.content.types import ContentType
from pyoctopus.controller.utils.http.headers import HttpHeader
from pyoctopus.controller.utils.http.methods import HttpMethod
from pyoctopus.controller.utils.octopus import OctopusBase


class OperationBase(OctopusBase, HTTPSConnection):
    identifier: str = ""
    method: Union[str, HttpMethod] = ""
    name: str = ""
    path: str = "/api"
    
    def __init__(
        self, 
        host: str, 
        username: str, 
        password: str, 
        port: int = None, 
        token: str = None
    ) -> None:
        super().__init__(
            host=host, 
            port=port
        )
        self.__headers = {
            HttpHeader.CONTENT_TYPE: ContentType.JSON,
            HttpHeader.X_OCTOPUS_API_KEY: token
        }
        
    def request(
        self,
        method: Union[str, HttpMethod],
        url: str,
        body: Optional[Union[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        if headers is None:
            headers = self.__headers
        else:
            for key, value in self.__headers.items():
                if key not in headers:
                    headers[key] = value

        super().request(method, url, body=body, headers=headers)
    
    def getresponse(
        self
    ) -> Dict[str, Any]: 
        response = super().getresponse()
        
        if response.status == HTTPStatus.OK:
            return loads(response.read().decode())

        return {
            "data": response.read().decode(),
            "reason": response.reason,
            "status": response.status
        }
        
    def __call__(
        self
    ) -> Dict[str, Any]:
        self.request(self.method, self.path)
        
        return self.getresponse()
