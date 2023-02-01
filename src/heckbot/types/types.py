from typing import Mapping, Union, Set, Sequence, Any

from _decimal import Decimal

JsonObject = Mapping[str, Union[bytes, bytearray, str, int, Decimal, bool,
                     Set[int], Set[Decimal], Set[str], Set[bytes],
                     Set[bytearray], Sequence[Any], Mapping[str, Any], None]]
