# -*- coding: utf-8 -*-

from view.main import MainWindow
from PyQt5.QtWidgets import QApplication
from typing import List
import sys


def main(args: List[str]) -> int:
    app = QApplication(args)

    view = MainWindow()
    view.show()

    return app.exec_()


exit_code = main(sys.argv)
sys.exit(exit_code)
