from typing import Optional, cast
from uuid import uuid4

import fmf

from tmt.utils import is_key_origin, log

# Name of the key holding the unique identifier
ID_KEY = "id"


class IdError(Exception):
    """ General Identifier Error """


class IdLeafError(IdError):
    """ Identifier not stored in a leaf """


def get_id(node: fmf.Tree, leaf_only: bool = True) -> Optional[str]:
    """
    Get identifier if defined, optionally ensure leaf node

    Return identifier for provided node. If 'leaf_only' is True,
    an additional check is performed to ensure that the identifier
    is defined in the node itself. The 'IdLeafError' exception is
    raised when the key is inherited from parent.
    """
    if node.get(ID_KEY) is None:
        return None
    if leaf_only and not is_key_origin(node, ID_KEY):
        raise IdLeafError(
            f"Key '{ID_KEY}' not defined in leaf '{node.name}'.")
    # FIXME: cast() - typeless "dispatcher" method
    return cast(Optional[str], node.get(ID_KEY))


def add_uuid_if_not_defined(node: fmf.Tree, dry: bool) -> Optional[str]:
    """ Add UUID into node and return it unless already defined """

    # Already defined
    if is_key_origin(node, ID_KEY):
        log.debug(
            f"Id '{node.data[ID_KEY]}' already defined for '{node.name}'.")
        return None

    # Generate a new one
    gen_uuid = str(uuid4())
    if not dry:
        with node as data:
            data[ID_KEY] = gen_uuid
            log.debug(f"Generating UUID '{gen_uuid}' for '{node.name}'.")
    return gen_uuid


def id_command(node: fmf.Tree, node_type: str, dry: bool) -> None:
    """
    Command line interfacing with output to terminal

    Show a brief summary when adding UUIDs to nodes.
    """
    generated = add_uuid_if_not_defined(node, dry=dry)
    if generated:
        print(
            f"New id '{generated}' added to {node_type} '{node.name}'.")
    else:
        print(
            f"Existing id '{node.get(ID_KEY)}' "
            f"found in {node_type} '{node.name}'.")
