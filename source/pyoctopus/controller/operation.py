from abc import ABC 
from abc import abstractmethod
from argparse import ArgumentParser
from inspect import Parameter
from inspect import signature
from typing import Any
from typing import Dict
from typing import get_type_hints
from typing import List
from typing import Optional
from typing import Union

from aiohttp import ClientSession

from pyoctopus.controller.utils.http.content.types import ContentType
from pyoctopus.controller.utils.http.headers import HttpHeader
from pyoctopus.controller.utils.http.methods import HttpMethod


class OperationBase(ABC): 
    identifier: str
    method: Union[str, HttpMethod]
    path: str
    
    def __init__(
        self, 
        session: ClientSession,
        url: str, 
        token: str
    ) -> None:
        self.__session = session
        self.__url = url
        self.__headers = {
            HttpHeader.CONTENT_TYPE: ContentType.JSON,
            HttpHeader.X_OCTOPUS_API_KEY: token
        }
        
    async def __call__(
        self
    ) -> Any:     
        async with self.__session.request(self.method, f"{self.__url}{self.path}", params=self.parameters, json=self.body, headers=self.__headers) as response:
            response.raise_for_status()
            
            return await response.json()
    
    @classmethod
    def set_parser(cls, parser: ArgumentParser, shared: Optional[List[str]] = None) -> None:
        parser.set_defaults(command=cls)
        
        for name, value in signature(cls.__init__).parameters.items():
            if name in shared:
                continue

            kind = get_type_hints(cls.__init__).get(name)
            
            default = value.default if value.default is not Parameter.empty else None

            if kind is bool:
                group = parser.add_mutually_exclusive_group()
                
                group.add_argument(
                    f"--{name}",
                    dest=name,
                    action="store_true"
                )
                group.add_argument(
                    f"--no-{name}",
                    dest=name,
                    action="store_false"
                )
                
                parser.set_defaults(**{name: default})
                
            else:
                parser.add_argument(
                    f"--{name}",
                    type=kind,
                    required=value.default is Parameter.empty,
                    default=default
                )
    
    @property
    def body(
        self
    ) -> Optional[Union[str, bytes]]:
        return None
        
    @property
    def parameters(
        self
    ) -> Optional[Dict[str, Any]]:
        return None
