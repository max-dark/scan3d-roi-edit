# -*- coding: utf-8 -*-
from typing import Dict, List
from PyQt5.QtCore import QPointF, QRectF, QJsonDocument, QJsonValue
from PyQt5.QtGui import QPolygonF


class SideRoi:
    detect: List[QRectF]
    polygon: QPolygonF


class Roi:
    side: Dict[str, SideRoi]