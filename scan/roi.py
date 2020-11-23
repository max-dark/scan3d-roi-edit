# -*- coding: utf-8 -*-
from typing import Dict, List
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPolygonF

import json

from scan.types import Scan, Side


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
        return (self.polygon.size() >= 3) and \
            self.polygon.containsPoint(point, Qt.OddEvenFill)

    def to_dict(self):
        o = dict()
        o['support'] = list()

        for s in self.support:
            r = dict()
            r['x'] = s.x()
            r['y'] = s.y()
            r['width'] = s.width()
            r['height'] = s.height()
            o['support'].append(r)

        o['polygon'] = list()
        for point in self.polygon:
            p = dict()
            p['x'] = point.x()
            p['y'] = point.y()
            o['polygon'].append(p)

        return o

    def from_dict(self, o: dict):
        self.support = list()
        self.polygon = QPolygonF()

        for r in o['support']:
            x = r['x']
            y = r['y']
            w = r['width']
            h = r['height']
            s = QRectF(x, y, w, h)
            self.support.append(s)

        for p in o['polygon']:
            x = p['x']
            y = p['y']
            point = QPointF(x, y)
            self.polygon.append(point)

        return self


class Roi:
    __side: Dict[Side, SideRoi]

    def __init__(self):
        self.__side = dict()
        for side in Scan.SIDES:
            self.__side[side] = SideRoi()

    def side(self, side: Side):
        return self.__side[side]

    def left(self) -> SideRoi:
        return self.__side[Scan.SIDE_LEFT]

    def top(self) -> SideRoi:
        return self.__side[Scan.SIDE_TOP]

    def right(self) -> SideRoi:
        return self.__side[Scan.SIDE_RIGHT]

    def to_json(self) -> str:
        o = dict()

        for side in Scan.SIDES:
            o[side] = self.__side[side].to_dict()

        return json.dumps(o, indent=2)

    def from_json(self, s: str):
        o = json.loads(s)

        for side in Scan.SIDES:
            if side in o:
                self.__side[side].from_dict(o[side])

        return self
