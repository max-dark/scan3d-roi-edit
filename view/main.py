# -*- coding: utf-8 -*-
from typing import Dict, List
from functools import cmp_to_key

from PyQt5.QtCore import QRectF, QSizeF, QPointF, \
    Qt, QSignalBlocker, pyqtSlot as Slot
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QAction, QMainWindow, \
    QMenuBar, QToolBar, QSlider, QStatusBar, \
    QGraphicsPolygonItem
from PyQt5.QtGui import QPen, QPolygonF

from scan.types import Scan, Side, NUM_FILES, NUM_SCANS
from scan.roi import Roi
from view.gfx import View, Scene, Point

ROI_EXT = '.roi.json'
ROI_JSON = f'ROI(*{ROI_EXT})'


class Ui:
    a_load: QAction
    a_load_roi: QAction
    a_save_roi: QAction
    a_add: QAction
    slide_file: QSlider
    slide_line: QSlider
    tab_list: QTabWidget
    gfx: Dict[Side, View]
    scene: Dict[Side, Scene]
    SIDES: List[Side] = [Scan.SIDE_LEFT, Scan.SIDE_TOP, Scan.SIDE_RIGHT]

    def build_ui(self, window: QMainWindow):
        container = QWidget()
        box = QVBoxLayout()

        self.tab_list = QTabWidget()
        self.gfx = dict()
        self.scene = dict()
        self.gfx[Scan.SIDE_LEFT] = self.__create_tab(Scan.SIDE_LEFT, "left")
        self.gfx[Scan.SIDE_TOP] = self.__create_tab(Scan.SIDE_TOP, "top")
        self.gfx[Scan.SIDE_RIGHT] = self.__create_tab(Scan.SIDE_RIGHT, "right")

        for side in Scan.SIDES:
            self.scene[side] = Scene()
            self.scene[side].addRect(0, 0, 2054, 2054)
            self.gfx[side].setScene(self.scene[side])

        box.addWidget(self.tab_list)

        container.setLayout(box)
        window.setCentralWidget(container)

        menu_bar = QMenuBar()
        file_menu: QMenu = menu_bar.addMenu("File")

        self.a_load: QAction = file_menu.addAction("Load Scans")
        file_menu.addSeparator()
        self.a_load_roi: QAction = file_menu.addAction("Load ROI")
        self.a_save_roi: QAction = file_menu.addAction("Save ROI")
        file_menu.addSeparator()
        a_exit: QAction = file_menu.addAction("Exit")
        a_exit.triggered.connect(window.close)

        edit_menu: QMenu = menu_bar.addMenu("Edit")
        self.a_add: QAction = edit_menu.addAction("Add point")

        window.setMenuBar(menu_bar)

        file_bar = QToolBar()
        self.slide_file = QSlider(orientation=Qt.Horizontal)
        self.slide_file.setRange(0, NUM_FILES - 1)
        self.slide_file.setSingleStep(1)
        self.slide_file.setPageStep(1)
        file_bar.addWidget(self.slide_file)

        self.slide_line = QSlider(orientation=Qt.Horizontal)
        self.slide_line.setRange(0, NUM_SCANS - 1)
        self.slide_line.setSingleStep(1)
        self.slide_line.setPageStep(16)
        file_bar.addWidget(self.slide_line)

        window.addToolBar(file_bar)
        window.setStatusBar(QStatusBar())

        window.setWindowTitle("Ruler")
        window.resize(1200, 700)

    def __create_tab(self, side: str, title: str):
        tab = View(side)
        self.tab_list.addTab(tab, title)
        return tab


def cmp(a: Point, b: Point) -> int:
    aa = a.position()
    bb = b.position()
    dx = int(aa.x()) - int(bb.x())
    dy = int(aa.y()) - int(bb.y())
    if dx == 0:
        return dy
    return dx


class MainWindow(QMainWindow):
    scan: Scan
    roi_model: Roi
    current_dir: str
    current_index: int
    current_line: int
    do_add_point: bool
    roi: Dict[Side, List[Point]]
    poly: Dict[Side, QGraphicsPolygonItem]

    def __init__(self):
        super().__init__(parent=None)
        self.roi_model = Roi()
        self.ui = Ui()
        self.ui.build_ui(self)
        self.__bind_ui()
        self.current_index = 0
        self.do_add_point = False

    def __bind_ui(self):
        self.ui.a_load.triggered.connect(self.__action_load)

        self.ui.a_load_roi.triggered.connect(self.__action_roi_load)
        self.ui.a_save_roi.triggered.connect(self.__action_roi_save)

        self.ui.a_add.triggered.connect(self.__action_add)

        self.ui.slide_file.valueChanged.connect(self.__slide_file)
        self.ui.slide_line.valueChanged.connect(self.__slide_line)

        self.roi = dict()
        self.poly = dict()
        for side in Scan.SIDES:
            self.roi[side] = list()
            self.poly[side] = QGraphicsPolygonItem()
            self.poly[side].setPen(QPen(Qt.green))
            self.poly[side].setFlag(QGraphicsItem.ItemSendsGeometryChanges)
            gfx = self.ui.gfx[side]
            gfx.mousePressed.connect(self.__pressed)

    def __make_base_name(self) -> str:
        name = f"{self.current_dir}/scan_{self.current_index}"
        return name

    def __sort_polygon(self, side: Side):
        self.roi[side].sort(key=cmp_to_key(cmp))

    def __update_polygon(self, side: Side):
        poly = QPolygonF()
        for p in self.roi[side]:
            poly.append(p.position())
        self.poly[side].setPolygon(poly)

    def __new_point(self, point: QPointF, side: Side) -> Point:
        pt = Point(point.x(), point.y(), 10)
        pt.setPen(QPen(Qt.green))
        pt.side = side
        pt.event.positionChanged.connect(self.__roi_changed)
        return pt

    @Slot(str, QPointF)
    def __pressed(self, side: str, point: QPointF):

        print("pressed", side, point.x(), point.y())
        if self.do_add_point:
            pt = self.__new_point(point, side)
            self.roi[side].append(pt)
            self.__sort_polygon(side)
            self.__update_polygon(side)
            if self.poly[side].polygon().size() == 3:
                self.ui.scene[side].addItem(self.poly[side])
            self.ui.scene[side].addItem(pt)
            self.do_add_point = False

    @Slot(str, QPointF)
    def __roi_changed(self, side: str, _: QPointF):
        self.__sort_polygon(side)
        self.__update_polygon(side)

    @Slot()
    def __action_add(self):
        self.do_add_point = True

    @Slot()
    def __action_load(self) -> None:
        scan_dir = QFileDialog.getExistingDirectory(
            parent=self, caption="select dir"
        )
        if scan_dir:
            self.__set_current_directory(scan_dir)
        else:
            print("cancel")

    def __points_to_model(self):
        for side in Scan.SIDES:
            roi_side = self.roi_model.side(side)
            roi_side.polygon.clear()
            for point in self.roi[side]:
                roi_side.polygon.append(point.position())

    def __model_to_points(self):
        for side in Scan.SIDES:
            roi_side = self.roi_model.side(side)
            self.__hide_roi_points(side)
            gfx = self.ui.scene[side]

            self.roi[side] = list()
            for point in roi_side.polygon:
                pt = self.__new_point(point, side)
                self.roi[side].append(pt)
                gfx.addItem(pt)

            self.__update_polygon(side)

        self.__update_views()

    @Slot()
    def __action_roi_load(self):
        name, ext = QFileDialog.getOpenFileName(
            parent=self, caption='Select ROI', filter=ROI_JSON
        )
        if name:
            with open(name) as json:
                content = json.read()
                self.roi_model.from_json(content)
                self.__model_to_points()

    @Slot()
    def __action_roi_save(self):
        name: str
        name, ext = QFileDialog.getSaveFileName(
            parent=self, caption='Enter file name', filter=ROI_JSON
        )
        if name:
            if not name.endswith(ROI_EXT):
                name += ROI_EXT
            self.__points_to_model()
            content = self.roi_model.to_json()
            with open(name, 'w') as json:
                json.write(content)

    @Slot(int)
    def __slide_file(self, value: int):
        self.__set_current_scan(value)

    @Slot(int)
    def __slide_line(self, value: int):
        self.__set_current_line(value)

    def __set_current_directory(self, directory):
        _ = QSignalBlocker(self)
        self.current_dir = directory
        self.ui.slide_file.setValue(0)
        self.__set_current_scan(0)

    def __set_current_scan(self, index: int):
        _ = QSignalBlocker(self)
        self.current_index = index

        name = self.__make_base_name()
        scan = Scan()
        scan.load_from(name)
        self.scan = scan
        self.ui.slide_line.setValue(0)
        self.__set_current_line(0)

    def __set_current_line(self, index: int):
        self.current_line = index
        self.statusBar().showMessage(
            f"{self.current_dir} / {self.current_index} / {self.current_line}"
        )
        self.__update_views()

    def __hide_roi_points(self, side: Side):
        gfx = self.ui.scene[side]
        for pt in self.roi[side]:
            gfx.removeItem(pt)
        gfx.removeItem(self.poly[side])

    def __show_roi_points(self, side: Side):
        gfx = self.ui.scene[side]
        for pt in self.roi[side]:
            gfx.addItem(pt)
        if self.poly[side].polygon().size() >= 3:
            gfx.addItem(self.poly[side])

    def __update_views(self):
        points = self.scan.get_points(self.current_line)
        p0 = QPen(Qt.darkGreen)
        p1 = QPen(Qt.darkGray)

        for side in Scan.SIDES:
            self.__hide_roi_points(side)
            gfx = self.ui.scene[side]
            gfx.clear()
            gfx.addRect(0, 0, 2054, 2054)

            roi = self.poly[side].polygon()

            for point in points[side]:
                r = QRectF()
                r.setSize(QSizeF(3, 3))
                r.moveCenter(point)
                pt: QGraphicsRectItem = gfx.addRect(r)
                if (roi.size() >= 3) and roi.containsPoint(point, Qt.OddEvenFill):
                    pt.setPen(p0)
                else:
                    pt.setPen(p1)
                pt.setToolTip(f"{point.x():0.2f}x{point.y():0.2f}")

            self.__show_roi_points(side)
