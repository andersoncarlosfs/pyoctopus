"""
Base class for defining operations that interact with the Octopus Deploy REST API.

This abstract class defines the structure for all operations including:
- Setting required metadata such as HTTP method, path, and identifier
- Registering command-line arguments dynamically
- Executing the HTTP request with aiohttp

Subclasses must define `identifier`, `method`, and `path`, and can override
`parameters` and `body` properties to control request content.
"""

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from inspect import Parameter, signature
from typing import Any, Dict, List, Optional, Union, get_type_hints

from aiohttp import ClientSession

from pyoctopus.controller.utils.http.content.types import ContentType
from pyoctopus.controller.utils.http.headers import HttpHeader
from pyoctopus.controller.utils.http.methods import HttpMethod


class OperationBase(ABC):
    """
    Abstract base class for Octopus Deploy operations.

    Subclasses must set:
    - `identifier`: A unique string to register this operation as a CLI subcommand.
    - `method`: HTTP method (e.g., "GET", "POST", or an HttpMethod enum).
    - `path`: The REST API endpoint path to call.
    """

    identifier: str
    method: Union[str, HttpMethod]
    path: str

    def __init__(
        self,
        session: ClientSession,
        url: str,
        token: str
    ) -> None:
        """
        Initialize the operation with a session, base URL, and API token.

        Args:
            session (ClientSession): A shared aiohttp session for making HTTP requests.
            url (str): The base URL of the Octopus Deploy server.
            token (str): API key for authenticating requests.
        """
        self.__session = session
        self.__url = url
        self.__headers = {
            HttpHeader.CONTENT_TYPE: ContentType.JSON,
            HttpHeader.X_OCTOPUS_API_KEY: token
        }

    async def __call__(self) -> Any:
        """
        Execute the HTTP request using aiohttp.

        Uses:
        - `self.method` for HTTP verb
        - `self.path` for endpoint
        - `self.parameters` for query parameters
        - `self.body` for request body
        - `self.__headers` for authentication and content type

        Returns:
            Parsed JSON response from the API.
        """
        async with self.__session.request(
            self.method,
            f"{self.__url}{self.path}",
            params=self.parameters,
            json=self.body,
            headers=self.__headers
        ) as response:
            response.raise_for_status()
            return await response.json()

    @classmethod
    def set_parser(cls, parser: ArgumentParser, shared: Optional[List[str]] = None) -> None:
        """
        Dynamically adds CLI arguments to the given ArgumentParser based on the constructor.

        Args:
            parser (ArgumentParser): Parser for this specific subcommand.
            shared (Optional[List[str]]): Parameter names that are shared and should be skipped.
        """
        parser.set_defaults(command=cls)

        for name, value in signature(cls.__init__).parameters.items():
            if name in shared:
                continue

            kind = get_type_hints(cls.__init__).get(name)
            default = value.default if value.default is not Parameter.empty else None

            if kind is bool:
                group = parser.add_mutually_exclusive_group()
                group.add_argument(f"--{name}", dest=name, action="store_true")
                group.add_argument(f"--no-{name}", dest=name, action="store_false")
                parser.set_defaults(**{name: default})
            else:
                parser.add_argument(
                    f"--{name}",
                    type=kind,
                    required=value.default is Parameter.empty,
                    default=default
                )

    @property
    def body(self) -> Optional[Union[str, bytes]]:
        """
        Return the HTTP request body to be sent.

        Can be overridden by subclasses to provide payload content.
        Defaults to None (no body).

        Returns:
            Optional[Union[str, bytes]]: Request body or None.
        """
        return None

    @property
    def parameters(self) -> Optional[Dict[str, Any]]:
        """
        Return the query parameters for the request.

        Can be overridden by subclasses to include API filters or other data.
        Defaults to None (no parameters).

        Returns:
            Optional[Dict[str, Any]]: Query parameters or None.
        """
        return None
