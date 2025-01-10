# nxt.locator module -- Locate NXT bricks
# Copyright (C) 2021  Nicolas Schodet
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
"""
The :mod:`.locator` module allows to detect connected NXT bricks and to create
corresponding :class:`~nxt.brick.Brick` objects.

The :func:`find` function is your main starting point to create a NXT-Python program.

If you want to make a command line tool, :func:`add_arguments` and
:func:`find_with_options` will make it easy to allow choosing a brick from the command
line.
"""
import argparse
import configparser
import importlib
import logging
import os
from collections.abc import Iterable, Iterator, MutableMapping
from typing import Callable, Literal, Optional, Union, overload

import nxt.brick

__all__ = ["find", "add_arguments", "find_with_options", "BrickNotFoundError"]

logger = logging.getLogger(__name__)


class BrickNotFoundError(Exception):
    """Exception raised when searching for a NXT brick, but no brick can be found."""

    pass


def _get_default_backends(**filters: Union[str, int, None]) -> list[str]:
    """Get default backends names.

    :param filters: Additional filter keywords or backends parameters, used to select
       additional backend based on some filter parameters.
    """
    backends = []
    if "filename" in filters:
        backends.append("devfile")
    if "server_host" in filters or "server_port" in filters:
        backends.append("socket")
    backends.extend(["usb", "bluetooth"])
    return backends


def _get_backends(backends: list[Union[str, object]]) -> Iterator[object]:
    """Get backends objects.

    :param backends: Specify backends to use.
    :return: An iterator on the backends object list.
    """
    for backend in backends:
        if isinstance(backend, str):
            if not backend.isidentifier():
                raise ValueError("invalid backend identifier")
            module = importlib.import_module(f"nxt.backend.{backend}")
            backend = module.get_backend()
        if backend is not None:
            yield backend


def _get_config(
    config: Optional[str] = "default",
    config_filenames: Optional[Iterable[Union[str, bytes, os.PathLike]]] = None,
) -> Optional[MutableMapping[str, str]]:
    """Read configuration file and get requested configuration.

    :param config: Name of the configuration file section to use, or ``None`` to disable
       configuration reading.
    :param config_filenames: Configuration file paths, or ``None`` for default.
    :return: Configuration section or ``None``.
    """
    if config is None:
        return None
    if config_filenames is None:
        config_filenames = [
            ".nxt-python.conf",
            os.path.expanduser("~/.nxt-python.conf"),
        ]
    parser = configparser.ConfigParser()
    logger.debug("configuration files=%s", config_filenames)
    read_filenames = parser.read(config_filenames)
    logger.debug("configuration read from %s", read_filenames)
    if config not in parser:
        logger.debug("no section %s, using %s", config, configparser.DEFAULTSECT)
        return parser[configparser.DEFAULTSECT]
    return parser[config]


@overload
def find(
    *,
    find_all: Literal[False] = False,
    backends: Optional[Iterable[Union[str, object]]] = None,
    custom_match: Optional[Callable[[nxt.brick.Brick], bool]] = None,
    config: Optional[str] = "default",
    config_filenames: Optional[Iterable[Union[str, bytes, os.PathLike]]] = None,
    name: Optional[str] = None,
    host: Optional[str] = None,
    **filters: Union[str, int, None],
) -> nxt.brick.Brick:
    ...


@overload
def find(
    *,
    find_all: Literal[True],
    backends: Optional[Iterable[Union[str, object]]] = None,
    custom_match: Optional[Callable[[nxt.brick.Brick], bool]] = None,
    config: Optional[str] = "default",
    config_filenames: Optional[Iterable[Union[str, bytes, os.PathLike]]] = None,
    name: Optional[str] = None,
    host: Optional[str] = None,
    **filters: Union[str, int, None],
) -> Iterator[nxt.brick.Brick]:
    ...


def find(
    *,
    find_all: bool = False,
    backends: Optional[Iterable[Union[str, object]]] = None,
    custom_match: Optional[Callable[[nxt.brick.Brick], bool]] = None,
    config: Optional[str] = "default",
    config_filenames: Optional[Iterable[Union[str, bytes, os.PathLike]]] = None,
    name: Optional[str] = None,
    host: Optional[str] = None,
    **filters: Union[str, int, None],
) -> Union[nxt.brick.Brick, Iterator[nxt.brick.Brick]]:
    """Find a NXT brick and return it.

    :param find_all: ``True`` to return an iterator over all bricks found.
    :param backends: Specify backends to use, use ``None`` for default.
    :param custom_match: Function to filter bricks found.
    :param config: Name of the configuration file section to use, or ``None`` to disable
       configuration reading.
    :param config_filenames: Configuration file paths, or ``None`` for default.
    :param name: Brick name (example: ``"NXT"``).
    :param host: Bluetooth address (example: ``"00:16:53:01:02:03"``).
    :param filters: Additional filter keywords or backends parameters.
    :return: The found brick, or an iterator if `find_all` is ``True``
    :raises BrickNotFoundError: if no brick is found and `find_all` is ``False``.

    Use this function to find a NXT brick. You can pass arguments to match a specific
    brick, for example, this will return the brick with name "NXT":

    >>> import nxt.locator
    >>> b = nxt.locator.find(name="NXT")

    If there is more than one matching brick, the first one found will be returned. If
    no brick is found, :exc:`BrickNotFoundError` is raised.

    If you want to find all matching bricks, you can set the `find_all` parameter to
    ``True``. It will return an iterator on all found bricks. If no brick is found, an
    empty iterator is returned.

    You can also use a custom function to search for your brick:

    >>> def is_my_brick(brick):
    ...     name = brick.get_device_info()[0]
    ...     return name.startswith("NXT")
    ...
    >>> for b in nxt.locator.find(find_all=True, custom_match=is_my_brick):
    ...     b.play_tone(440, 1000)
    ...

    The `name` and `host` parameters are passed to the backends, and are also used to
    filter the result, so you can use the `host` parameter even when not using
    Bluetooth.

    Extra keywords arguments are given to the backends which can use them or not. See
    the :mod:`nxt.backend` documentation.

    The `backends` parameter allows overriding the default list of backends to use. Each
    element of the list is a backend object or a backend name. Again, see
    :mod:`nxt.backend` documentation for the list of available backends.

    Configuration is used to load default values for `backends` parameter and selection
    parameters. If the `config` parameter is not ``None``, a configuration will be read
    from files listed by the `config_filenames` parameter, or from a default list of
    files. The `config` parameter corresponds to the section to use for configuration.
    """
    config_section = _get_config(config, config_filenames)

    if config_section is not None:
        if backends is None:
            backends = config_section.get("backends", None)
            if backends is not None:
                backends = backends.split()
        if custom_match is None and name is None and host is None and not filters:
            name = config_section.get("name", None)
            host = config_section.get("host", None)
            for key, value in config_section.items():
                if key not in ("backends", "name", "host"):
                    filters[key] = value

    if backends is None:
        backends = _get_default_backends(**filters)

    def iter_bricks():
        for backend in _get_backends(backends):
            logger.info("using backend from %s", backend.__module__)
            for brick in backend.find(name=name, host=host, **filters):
                logger.debug("found brick %s", brick)
                if name is not None or host is not None:
                    bname, bhost, _, _ = brick.get_device_info()
                    logger.debug("found brick with name=%s and host=%s", bname, bhost)
                    if name is not None and name != bname:
                        logger.debug("brick name mismatch, %s != %s", bname, name)
                        brick.close()
                        continue
                    if host is not None and host != bhost:
                        logger.debug("brick host mismatch, %s != %s", bhost, host)
                        brick.close()
                        continue
                if custom_match is not None and not custom_match(brick):
                    logger.debug("brick rejected by custom_match")
                    brick.close()
                    continue
                yield brick

    if find_all:
        return iter_bricks()
    else:
        brick = next(iter_bricks(), None)
        if brick is None:
            raise BrickNotFoundError("no brick found")
        return brick


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add options to an :mod:`argparse` parser to allow configuration from the command
    line.

    :param parser: An :mod:`argparse` parser.

    This can be used to easily design a command line interface. Use it with
    :func:`find_with_options`.

    Example:

    >>> import argparse
    >>> import nxt.locator
    >>> p = argparse.ArgumentParser(description="My NXT-Python program")
    >>> nxt.locator.add_arguments(p)
    >>> p.add_argument("--hello", help="say hello (example)")
    >>> options = p.parse_args()
    >>> brick = nxt.locator.find_with_options(options)
    """
    parser.add_argument(
        "--backend",
        dest="backends",
        action="append",
        choices=("usb", "bluetooth", "socket", "devfile"),
        metavar="NAME",
        help="enable backend, can be given several times",
    )
    parser.add_argument(
        "--config", metavar="NAME", help="name of configuration file section to use"
    )
    parser.add_argument(
        "--config-filename",
        dest="config_filenames",
        action="append",
        metavar="PATH",
        help="configuration life path, can be given several times",
    )
    parser.add_argument("--name", help="NXT brick name (example: NXT)")
    parser.add_argument(
        "--host",
        metavar="ADDRESS",
        help="NXT brick Bluetooth address (example: 00:16:53:01:02:03)",
    )
    parser.add_argument(
        "--server-host",
        metavar="HOST",
        help="server address or name (example: localhost)",
    )
    parser.add_argument(
        "--server-port", type=int, metavar="PORT", help="server port (example: 2727)"
    )
    parser.add_argument("--filename", help="device file name (example: /dev/rfcomm0)")


@overload
def find_with_options(
    options: argparse.Namespace, *, find_all: Literal[False] = False
) -> nxt.brick.Brick:
    ...


@overload
def find_with_options(
    options: argparse.Namespace, *, find_all: Literal[True]
) -> Iterator[nxt.brick.Brick]:
    ...


def find_with_options(
    options: argparse.Namespace, *, find_all: bool = False
) -> Union[nxt.brick.Brick, Iterator[nxt.brick.Brick]]:
    """Find a NXT brick and return it, using options from command line.

    :param argparse.Namespace options: Options returned by
       :meth:`argparse.ArgumentParser.parse_args`
    :param bool find_all: ``True`` to return an iterator over all bricks found.
    :return: The found brick or ``None``, or an iterator if `find_all` is ``True``.
    :rtype: nxt.brick.Brick or None or Iterator[nxt.brick.Brick]

    This is to be used together with :func:`add_arguments`. It calls :func:`find` with
    options received on the command line.
    """
    kwargs = dict()
    for k in (
        "backends",
        "config",
        "config_filenames",
        "name",
        "host",
        "server_host",
        "server_port",
        "filename",
    ):
        v = getattr(options, k)
        if v is not None:
            kwargs[k] = v
    # Split to satisfy type checking.
    if find_all:
        return find(find_all=True, **kwargs)
    else:
        return find(find_all=False, **kwargs)
