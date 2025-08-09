"""
Main entry point for the PyOctopus CLI.

This module uses argparse to dynamically discover available operations
in the `pyoctopus.controller.operations` module and constructs a command-line
interface to invoke them. It supports passing in API credentials via command-line
arguments or environment variables and handles execution asynchronously.
"""

from argparse import ArgumentParser, SUPPRESS
from asyncio import run
from importlib import import_module
from importlib_resources import files
from inspect import getmembers, getfile, isclass, signature
from os import environ
from os.path import dirname
from pkgutil import iter_modules

from aiohttp import ClientSession

from pyoctopus.controller.operation import OperationBase


class Main:
    """
    PyOctopus command-line interface initializer.

    This class handles the discovery of available operations, constructs
    an argument parser, and executes the selected operation with proper
    arguments and an aiohttp client session.
    """

    @staticmethod
    def __get_classes(
        module: str = "pyoctopus.controller.operations",
        type: object = OperationBase
    ):
        """
        Recursively discover all classes in the given module that inherit from a base type.

        Args:
            module (str): Base module path to search.
            type (object): The base class to filter by.

        Yields:
            type: Classes that are subclasses of the given type and defined within the module.
        """
        for submodule in iter_modules([dirname(getfile(import_module(module)))]):
            name = getattr(submodule, "name")

            if name:
                if not name.startswith("."):
                    name = "." + name

                # If it's a package, recurse into it
                if submodule.ispkg:
                    yield from Main.__get_classes(f"{module}{name}")
                else:
                    # Import the submodule and check for matching classes
                    for _, member in getmembers(import_module(name, package=module), isclass):
                        if issubclass(member, type) and module in getattr(member, "__module__"):
                            yield member

    async def __call__(self) -> None:
        """
        Builds the CLI, parses arguments, and runs the selected operation.

        This method is asynchronous and manages:
        - Parser creation
        - Subcommand discovery
        - Argument parsing
        - aiohttp session lifecycle
        """
        parser = ArgumentParser(description="PyOctopus - Octopus Deploy CLI")

        # Discovering available commands
        subparsers = parser.add_subparsers(dest="command", required=True)

        # Extract shared args from OperationBase.__init__
        shared = [name for name in signature(OperationBase.__init__).parameters]

        for operation in Main.__get_classes():
            # Register a subparser for each operation
            getattr(operation, "set_parser")(
                parser=subparsers.add_parser(getattr(operation, "identifier")),
                shared=shared
            )

        # Main arguments with environment variable fallback
        parser.add_argument(
            "--token",
            dest="token",
            type=str,
            required=not environ.get("OCTOPUS_REST_TOKEN", "").strip(),
            default=environ.get("OCTOPUS_REST_TOKEN", SUPPRESS),
            help="API token for Octopus Deploy (or set OCTOPUS_REST_TOKEN env var)"
        )
        parser.add_argument(
            "--url",
            dest="url",
            type=str,
            required=not environ.get("OCTOPUS_REST_URL", "").strip(),
            default=environ.get("OCTOPUS_REST_URL", SUPPRESS),
            help="Octopus Deploy server URL (or set OCTOPUS_REST_URL env var)"
        )
        parser.add_argument(
            "--timeout",
            dest="timeout",
            type=int,
            required=False,
            default=environ.get("OCTOPUS_REST_TIMEOUT", SUPPRESS),
            help="Request timeout in seconds (optional, can use OCTOPUS_REST_TIMEOUT)"
        )

        # Parse arguments
        arguments = vars(parser.parse_args())

        # Execute the appropriate command with an aiohttp session
        async with ClientSession(timeout=arguments.pop("timeout", None)) as session:
            print(
                await arguments.pop("command")(
                    session=session,
                    url=arguments.pop("url"),
                    token=arguments.pop("token"),
                    **arguments
                )()
            )

    @staticmethod
    def main() -> None:
        """
        Entry point for the CLI when invoked directly.

        Calls the asynchronous CLI logic using asyncio.run().
        """
        run(Main()())


if __name__ == "__main__":
    Main.main()
