# -*- coding: utf-8 -*-
import typing
from PyQt5.QtCore import QObject, Qt, \
    QRectF, QPointF, QSizeF, \
    pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtWidgets import \
    QGraphicsScene, QGraphicsView, \
    QWidget, QGraphicsRectItem, QGraphicsItem
from PyQt5.QtGui import QMouseEvent


class View(QGraphicsView):
    mousePressed = Signal([str, QPointF])
    mouseReleased = Signal([str, QPointF])

    side: str

    def __init__(self, side: str, parent: QWidget = None):
        super().__init__(parent=parent)
        self.side = side

    # @override
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            point = self.mapToScene(event.pos())
            self.mousePressed.emit(self.side, QPointF(point))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            point = self.mapToScene(event.pos())
            self.mouseReleased.emit(self.side, QPointF(point))
        super().mouseReleaseEvent(event)


class Scene(QGraphicsScene):
    def __init__(self, parent: QObject = None):
        super().__init__(parent=parent)


class PointEvent(QObject):
    positionChanged = Signal([str, QPointF])

    def __init__(self):
        super().__init__(parent=None)


class Point(QGraphicsRectItem):
    side: str
    event: PointEvent

    def __init__(self, x: float, y: float, size: float = 5.0, parent: QGraphicsItem = None):
        center = QPointF(x, y)
        sz = QSizeF(size, size)
        r = QRectF()
        r.setSize(sz)
        r.moveCenter(center)
        super().__init__( r, parent=parent)
        self.event = PointEvent()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def setPosition(self, x: float, y: float):
        r = self.rect()
        r.moveCenter(QPointF(x, y))
        self.setRect(r)

    def position(self) -> QPointF:
        return self.mapToScene(self.rect().center())

    def setSize(self, size: float):
        r = self.rect()
        c = r.center()
        s = QSizeF(size, size)
        r.setSize(s)
        r.moveCenter(c)
        self.setRect(r)

    def size(self):
        r = self.rect()
        sz = (r.width() + r.height()) / 2.0
        return sz

    def itemChange(self, change: 'QGraphicsItem.GraphicsItemChange', value: typing.Any) -> typing.Any:
        if change == QGraphicsItem.ItemPositionHasChanged:
            p = self.position()
            # print('pos changed', p)
            self.event.positionChanged.emit(self.side, p)

        return super().itemChange(change, value)
