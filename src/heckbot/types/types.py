from __future__ import annotations

from _decimal import Decimal
from typing import Any
from typing import Mapping
from typing import Sequence
from typing import Set
from typing import Union

JsonObject = Mapping[
    str, Union[
        bytes, bytearray, str, int, Decimal, bool,
        Set[int], Set[Decimal], Set[str], Set[bytes],
        Set[bytearray], Sequence[Any], Mapping[str, Any], None,
    ],
]
