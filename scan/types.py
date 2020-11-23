# -*- coding: utf-8 -*-
from PyQt5.QtCore import QPointF
from typing import Dict, List

import numpy as np

NUM_FILES = 30

# num of scan lines per file
NUM_SCANS = 512
# num of points per line
DOTS_PER_SCAN = 1024
# total points per file
TOTAL_DOTS = NUM_SCANS * DOTS_PER_SCAN

SCAN_SHAPE = (NUM_SCANS, DOTS_PER_SCAN)
MARK_SHAPE = (NUM_SCANS, 5)

# ## define types

# point coords [X, R] относительно камеры(чем меньше R тем дальше от камеры)
# Camera position in coord system (Xcam, Ycam) = (1000.0, 2054.0)
coord_t = np.dtype((np.float32, SCAN_SHAPE))
# line status
mark_t = np.dtype((np.uint32, MARK_SHAPE))
# intensity
intensity_t = np.dtype((np.uint8, SCAN_SHAPE))

# struct data_t
# {
#   float32 X[NUM_SCANS][DOTS_PER_SCAN];
#   float32 Y[NUM_SCANS][DOTS_PER_SCAN];
#   uint32_t Mark[NUM_SCANS][5]; // line scan status, encoder position and sensors state
#   uint8_t intensity[NUM_SCANS][DOTS_PER_SCAN];
# };
data_t = np.dtype([
    ('X', coord_t),
    ('Y', coord_t),
    ('Mark', mark_t),
    ('Intensity', intensity_t)
])


Side = str
PointList = List[QPointF]


class Scan:
    SIDE_LEFT = 'left'
    SIDE_TOP = 'top'
    SIDE_RIGHT = 'right'
    SIDES: List[Side] = [SIDE_RIGHT, SIDE_TOP, SIDE_LEFT]
    side: Dict[str, np.dtype]

    def load_from(self, base_name: str, ext: str = '.dat') -> None:
        self.side = dict()
        for side in Scan.SIDES:
            self.__load_side(base_name, side, ext)

    def __load_side(self, base_name: str, side: str, ext: str):
        name = format_name(base_name, side, ext)
        self.side[side] = load_file(name)

    def get_line(self, index: int):
        line = dict()
        for side in Scan.SIDES:
            line[side] = self.__get_line(side, index)
        return line

    def get_points(self, index) -> Dict[Side, PointList]:
        points: Dict[Side, PointList] = dict()

        side: Side
        for side in Scan.SIDES:
            x, y = self.__get_line(side, index)
            points[side] = list()
            for i in range(0, DOTS_PER_SCAN):
                xx = x[i]
                yy = y[i]
                if (xx > 0.0) and (yy > 0.0):
                    points[side].append(QPointF(xx, yy))

        return points

    def __get_line(self, side: str, index: int):
        data: data_t = self.side[side]
        return data['X'][index], data['Y'][index]


def load_file(file_name) -> data_t:
    data = np.fromfile(file_name, dtype=data_t)
    scan = data[0]
    return scan


def format_name(base: str, side:str, ext: str) -> str:
    return f"{base}_{side}{ext}"
