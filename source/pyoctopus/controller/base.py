from abc import ABC
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


class OperationBase(ABC, HTTPSConnection):
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
        super().__init__(host, port)
        self.username = username
        self.password = password
        self.token = token
        self.headers = {
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
        if not self.headers[HttpHeader.X_OCTOPUS_API_KEY]:
            self.headers.pop(HttpHeader.X_OCTOPUS_API_KEY, None)
            
            super().request(
                HttpMethod.POST, 
                f"{OperationBase.path}/users/login",
                body=dumps({
                    "Username": self.username,
                    "Password": self.password
                }),
                headers=self.headers
            )
            
            response = super().getresponse()
            
            if response.status == HTTPStatus.OK:
                super().request(
                    HttpMethod.GET, 
                    f"{OperationBase.path}/users/access-token",
                    body=None,
                    headers=self.headers
                )
                
                response = super().getresponse()
            
                if response.status == HTTPStatus.OK:
                    self.headers[HttpHeader.X_OCTOPUS_API_KEY] = loads(response.read().decode())["AccessToken"]

        if headers is None:
            headers = self.headers
        else:
            

        headers[HttpHeader.X_OCTOPUS_API_KEY] = self.token

        super().request(method, url, body=body, headers=headers)
    
    def getresponse(
        self
    ) -> Dict[str, Any]: 
        response = super().getresponse()
        
        data = response.read().decode()
        
        if response.status == HTTPStatus.OK:
            return loads(data)

        return {
            "data": data,
            "reason": response.reason,
            "status": response.status
        }
        
    def __call__(
        self
    ) -> Dict[str, Any]:
        self.request(self.method, self.path)
        
        return self.getresponse()
