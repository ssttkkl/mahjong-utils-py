from abc import ABC, abstractmethod
from typing import Set, Dict, Optional

from pydantic import BaseModel

from mahjong_utils.models.tile import Tile


class Shanten(BaseModel, ABC):
    shanten: int

    @abstractmethod
    def __encode__(self) -> dict:
        raise NotImplementedError()

    @classmethod
    def __decode__(cls, data: dict) -> "Shanten":
        if data['type'] == 'ShantenWithoutGot':
            return ShantenWithoutGot.__decode__(data)
        elif data['type'] == 'ShantenWithGot':
            return ShantenWithGot.__decode__(data)
        else:
            raise ValueError("invalid type: " + data['type'])


class ShantenWithoutGot(Shanten):
    advance: Set[Tile]
    advance_num: Optional[int]
    good_shape_advance: Optional[Set[Tile]]
    good_shape_advance_num: Optional[int]

    def __encode__(self) -> dict:
        return dict(
            type="ShantenWithoutGot",
            shantenNum=self.shanten,
            advance=[t.__encode__() for t in self.advance],
            advanceNum=self.advance_num,
            goodShapeAdvance=[t.__encode__() for t in good_shape_advance]
            if (good_shape_advance := self.good_shape_advance) is not None else None,
            goodShapeAdvanceNum=self.good_shape_advance_num
        )

    @classmethod
    def __decode__(cls, data: dict) -> "ShantenWithoutGot":
        return ShantenWithoutGot(
            shanten=data["shantenNum"],
            advance=set(Tile.__decode__(x) for x in data["advance"]),
            advance_num=advance_num
            if (advance_num := data["advanceNum"]) is not None else None,
            good_shape_advance=set(Tile.__decode__(x) for x in good_shape_advance)
            if (good_shape_advance := data["goodShapeAdvance"]) is not None else None,
            good_shape_advance_num=good_shape_advance_num
            if (good_shape_advance_num := data["goodShapeAdvanceNum"]) is not None else None,
        )


class ShantenWithGot(Shanten):
    discard_to_advance: Dict[Tile, ShantenWithoutGot]

    def __encode__(self) -> dict:
        return dict(
            type="ShantenWithGot",
            shantenNum=self.shanten,
            discardToAdvance=dict((k.__encode__(), v.__encode__()) for (k, v) in self.discard_to_advance.items())
        )

    @classmethod
    def __decode__(cls, data: dict) -> "ShantenWithGot":
        return ShantenWithGot(
            shanten=data["shantenNum"],
            discard_to_advance=dict(
                (Tile.__decode__(k), ShantenWithoutGot.__decode__(v))
                for (k, v) in data["discardToAdvance"].items())
        )
