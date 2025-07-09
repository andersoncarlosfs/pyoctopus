from enum import Enum


class HttpHeader(str, Enum):
    CONTENT_TYPE = "Content-Type"
    X_OCTOPUS_API_KEY = "X-Octopus-ApiKey"
