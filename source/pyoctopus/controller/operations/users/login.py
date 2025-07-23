from argparse import ArgumentParser
from typing import Any
from typing import Optional
from typing import Union

from aiohttp import ClientSession

from pyoctopus.controller.operation import OperationBase
from pyoctopus.controller.utils.http.methods import HttpMethod


class LoginUserOperation(OperationBase):
    identifier: str = "loginUser"
    method: Union[str, HttpMethod] = HttpMethod.POST
    path: str = "/users/login"

    def __init__(
        self, 
        session: ClientSession,
        url: str, 
        token: str,
        username: str, 
        password: str
    ) -> None:
        super().__init__(session, url, token)
        
        self.username = username
        self.password = password
        
    @property
    def body(self) -> Optional[Union[str, bytes]]:
        return {
            "Username": self.username,
            "Password": self.password
        }
