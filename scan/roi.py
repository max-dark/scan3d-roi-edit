# -*- coding: utf-8 -*-
from typing import Dict, List
from PyQt5.QtCore import QPointF, QRectF, QJsonDocument, QJsonValue, Qt
from PyQt5.QtGui import QPolygonF

from scan.types import Scan


class SideRoi:
    support: List[QRectF]
    polygon: QPolygonF

    def __init__(self):
        self.support = list()
        self.polygon = QPolygonF()

    def in_support(self, point: QPointF) -> bool:
        for s in self.support:
            if s.contains(point):
                return True

        return False

    def contains(self, point: QPointF) -> bool:
        return self.polygon.containsPoint(point, Qt.OddEvenFill)

    def to_json(self):
        pass

    def from_json(self):
        return self


class Roi:
    side: Dict[str, SideRoi]

    def __init__(self):
        self.side = dict()
        for side in Scan.SIDES:
            self.side[side] = SideRoi()

    def left(self) -> SideRoi:
        return self.side[Scan.SIDE_LEFT]

    def top(self) -> SideRoi:
        return self.side[Scan.SIDE_TOP]

    def right(self) -> SideRoi:
        return self.side[Scan.SIDE_RIGHT]

    def to_json(self):
        pass

    def from_json(self):
        return self
