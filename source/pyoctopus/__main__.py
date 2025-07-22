from argparse import ArgumentParser
from argparse import SUPPRESS
from importlib import import_module
from importlib_resources import files
from inspect import getmembers
from inspect import getfile
from inspect import isclass
from os import environ
from os.path import dirname
from pkgutil import iter_modules

from pyoctopus.controller.base import OperationBase


class Main:
    def __init__(self, username: str, password: str, token: str, host: str) -> None:
        self.host=host
        self.username=username
        self.password=password
        self.token=token

    def __call__(self, **kwargs) -> None:
        # Retrieving the command
        command = kwargs.pop("command")

        # Searching the operation
        for operation in Main.__get_classes():
            if getattr(operation, "name") == command:
                # Invoking the operation
                operation(
                    host=self.host,                                
                    username=self.username,
                    password=self.password,
                    token=self.token
                )()

    @staticmethod
    def __get_classes(module: str = "pyoctopus.controller.operations", type: object = OperationBase):
        for submodule in iter_modules([dirname(getfile(import_module(module)))]):
            submodule = getattr(submodule, "name")

            if submodule:
                if not submodule.startswith(r"."):
                    submodule = r"." + submodule

                for _, member in getmembers(import_module(submodule, package=module), isclass):
                    if isclass(member) and issubclass(member, type) and module in getattr(member, "__module__"):
                        yield member

    @staticmethod
    def main() -> None:
        # Setting an argument parser
        main_argument_parser = ArgumentParser(description="PyOctopus")

        # Setting an argument subparsers
        subparsers = main_argument_parser.add_subparsers(dest="command", required=True)

        # Setting a list of generic subparsers
        generic_argument_parser = {}

        for operation in Main.__get_classes():
            # Setting a command
            command = getattr(operation, "name")

            # Setting an argument subparser for processing the data
            generic_argument_parser[command] = subparsers.add_parser(command)

        # Setting the main arguments
        main_argument_parser.add_argument(
            "--username",
            dest="username",
            type=str,
            required=False,
            default=environ.get("PYOCTOPUS_USERNAME", SUPPRESS)
        )
        main_argument_parser.add_argument(
            "--password",
            dest="password",
            type=str,
            required=False,
            default=environ.get("PYOCTOPUS_PASSWORD", SUPPRESS)
        )
        main_argument_parser.add_argument(
            "--token",
            dest="token",
            type=str,
            required=False,
            default=environ.get("PYOCTOPUS_TOKEN", SUPPRESS)
        )
        main_argument_parser.add_argument(
            "--host",
            dest="host",
            type=str,
            required=not environ.get("PYOCTOPUS_HOST", "").strip(),
            default=environ.get("PYOCTOPUS_HOST", None)
        )

        # Retrieving the arguments
        arguments = vars(main_argument_parser.parse_args())

        if not (arguments.get("token") or (arguments.get("username") and arguments.get("password"))):
            main_argument_parser.error("the following arguments are required: --token or both --username and --password")

        # Running PyOctopus
        Main(
            username=arguments.pop("username", None),
            password=arguments.pop("password", None),
            token=arguments.pop("token", None),
            host=arguments.pop("host"),
        )(**arguments)


if __name__ == "__main__":
    Main.main()
