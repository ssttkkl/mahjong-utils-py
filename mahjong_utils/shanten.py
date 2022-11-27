from enum import Enum
from typing import Optional, Sequence, Set, Dict

from pydantic import BaseModel
from stringcase import snakecase, pascalcase

from mahjong_utils.lib import libmahjongutils
from mahjong_utils.models.furo import Furo
from mahjong_utils.models.hand import Hand
from mahjong_utils.models.shanten import Shanten, ShantenWithoutGot
from mahjong_utils.models.tile import Tile


class ShantenResultType(str, Enum):
    regular = "Regular"
    chitoi = "Chitoi"
    kokushi = "Kokushi"
    union = "Union"


class ShantenResult(BaseModel):
    type: ShantenResultType
    hand: Hand
    shanten_info: Shanten
    regular: Optional["ShantenResult"]
    chitoi: Optional["ShantenResult"]
    kokushi: Optional["ShantenResult"]

    def __encode__(self) -> dict:
        return dict(
            type=pascalcase(self.type.name),
            hand=self.hand.__encode__(),
            shantenInfo=self.shanten_info.__encode__(),
            regular=regular.__encode__() if (regular := self.regular) is not None else None,
            chitoi=chitoi.__encode__() if (chitoi := self.chitoi) is not None else None,
            kokushi=kokushi.__encode__() if (kokushi := self.kokushi) is not None else None,
        )

    @classmethod
    def __decode__(cls, data: dict) -> "ShantenResult":
        return ShantenResult(
            type=ShantenResultType[snakecase(data["type"])],
            hand=Hand.__decode__(data["hand"]),
            shanten_info=Shanten.__decode__(data["shantenInfo"]),
            regular=ShantenResult.__decode__(regular) if (regular := data["regular"]) is not None else None,
            chitoi=ShantenResult.__decode__(chitoi) if (chitoi := data["chitoi"]) is not None else None,
            kokushi=ShantenResult.__decode__(kokushi) if (kokushi := data["kokushi"]) is not None else None,
        )

    @property
    def shanten(self) -> Optional[int]:
        return getattr(self.shanten_info, "shanten", None)

    @property
    def advance(self) -> Optional[Set[Tile]]:
        return getattr(self.shanten_info, "advance", None)

    @property
    def advance_num(self) -> Optional[int]:
        return getattr(self.shanten_info, "advance_num", None)

    @property
    def good_shape_advance(self) -> Optional[Set[Tile]]:
        return getattr(self.shanten_info, "good_shape_advance", None)

    @property
    def good_shape_advance_num(self) -> Optional[int]:
        return getattr(self.shanten_info, "good_shape_advance_num", None)

    @property
    def discard_to_advance(self) -> Optional[Dict[Tile, ShantenWithoutGot]]:
        return getattr(self.shanten_info, "discard_to_advance", None)

    @property
    def with_got(self) -> bool:
        return self.discard_to_advance is not None


def regular_shanten(
        tiles: Sequence[Tile],
        furo: Optional[Sequence[Furo]] = None,
        calc_advance_num: bool = True
) -> ShantenResult:
    result = libmahjongutils.call("regularShanten", {
        "tiles": [str(t) for t in tiles],
        "furo": [Furo.__encode__(fr) for fr in furo] if furo is not None else [],
        "calcAdvanceNum": calc_advance_num
    })

    return ShantenResult.__decode__(result)


def chitoi_shanten(
        tiles: Sequence[Tile],
        calc_advance_num: bool = True
) -> ShantenResult:
    result = libmahjongutils.call("chitoiShanten", {
        "tiles": [str(t) for t in tiles],
        "calcAdvanceNum": calc_advance_num
    })

    return ShantenResult.__decode__(result)


def kokushi_shanten(
        tiles: Sequence[Tile],
        calc_advance_num: bool = True
) -> ShantenResult:
    result = libmahjongutils.call("kokushiShanten", {
        "tiles": [str(t) for t in tiles],
        "calcAdvanceNum": calc_advance_num
    })

    return ShantenResult.__decode__(result)


def shanten(
        tiles: Sequence[Tile],
        furo: Optional[Sequence[Furo]] = None,
        calc_advance_num: bool = True
) -> ShantenResult:
    result = libmahjongutils.call("shanten", {
        "tiles": [str(t) for t in tiles],
        "furo": [Furo.__encode__(fr) for fr in furo] if furo is not None else [],
        "calcAdvanceNum": calc_advance_num
    })

    return ShantenResult.__decode__(result)


__all__ = ("regular_shanten",
           "chitoi_shanten",
           "kokushi_shanten",
           "shanten",
           "ShantenResult",)
