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

from pyoctopus.controller.operation import OperationBase
from pyoctopus.controller.utils.octopus import OctopusBase


class Main(OctopusBase):
    def __init__(
        self, 
        host: str, 
        token: str
    ) -> None:
        self.__host=host,
        self.__token=token

    def __call__(
        self, 
        **kwargs
    ) -> None:
        # Retrieving the command
        command = kwargs.pop("command")

        # Searching the operation
        for operation in Main.__get_classes():
            if getattr(operation, "name") == command:
                # Invoking the operation
                operation(
                    host=self.__host,
                    token=self.__token
                )()

    @staticmethod
    def __get_classes(
        module: str = "pyoctopus.controller.operations", 
        type: object = OperationBase
    ):
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
            "--token",
            dest="token",
            type=str,
            required=not environ.get("PYOCTOPUS_TOKEN", "").strip(),
            default=environ.get("PYOCTOPUS_TOKEN", SUPPRESS)
        )
        main_argument_parser.add_argument(
            "--host",
            dest="host",
            type=str,
            required=not environ.get("PYOCTOPUS_HOST", "").strip(),
            default=environ.get("PYOCTOPUS_HOST", SUPPRESS)
        )

        # Retrieving the arguments
        arguments = vars(main_argument_parser.parse_args())

        # Running PyOctopus
        Main(
            host=arguments.pop("host"),
            token=arguments.pop("token")
        )(**arguments)


if __name__ == "__main__":
    Main.main()
