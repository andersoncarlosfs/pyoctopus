from typing import Any
from typing import Dict
from typing import Union

from pyoctopus.controller.abstract import OperationBase
from pyoctopus.controller.utils.http.methods import HttpMethod


class GetCurrentUser(OperationBase):
    identifier: str = "getCurrentUser"
    method: Union[str, HttpMethod] = HttpMethod.GET
    name: str = "get_current_user"
    path: str = "/users/me"
