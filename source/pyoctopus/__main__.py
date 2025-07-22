from argparse import ArgumentParser
from argparse import SUPPRESS
from asyncio import run
from importlib import import_module
from importlib_resources import files
from inspect import getmembers
from inspect import getfile
from inspect import isclass
from inspect import signature
from os import environ
from os.path import dirname
from pkgutil import iter_modules

from aiohttp import ClientSession

from pyoctopus.controller.operation import OperationBase


class Main:        
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

    async def __call__(
        self
    ) -> None:
        # Setting an argument parser
        parser = ArgumentParser(description="PyOctopus")

        # Setting an argument subparsers
        subparsers = parser.add_subparsers(dest="command", required=True)
        
        shared = [name for name in signature(OperationBase.__init__).parameters]

        for operation in Main.__get_classes():
            # Setting an argument subparser for processing the data
            getattr(operation, "set_parser")(
                parser=subparsers.add_parser(
                    getattr(operation, "identifier")
                ),
                shared=shared
            )

        # Setting the main arguments
        parser.add_argument(
            "--token",
            dest="token",
            type=str,
            required=not environ.get("OCTOPUS_REST_TOKEN", "").strip(),
            default=environ.get("OCTOPUS_REST_TOKEN", SUPPRESS)
        )
        parser.add_argument(
            "--url",
            dest="url",
            type=str,
            required=not environ.get("OCTOPUS_REST_URL", "").strip(),
            default=environ.get("OCTOPUS_REST_URL", SUPPRESS)
        )
        parser.add_argument(
            "--timeout",
            dest="timeout",
            type=int,
            required=False,
            default=environ.get("OCTOPUS_REST_TIMEOUT", SUPPRESS)
        )

        # Retrieving the arguments
        arguments = vars(parser.parse_args())

        # Searching the operation
        async with ClientSession(timeout=arguments.pop("timeout", None)) as session:
            print(
                await arguments.pop(
                    "command"
                )(
                    session=session,
                    url=arguments.pop("url"),
                    token=arguments.pop("token"),
                    **arguments
                )()
            )

    @staticmethod
    def main() -> None:
        run(Main()())


if __name__ == "__main__":
    Main().main()
