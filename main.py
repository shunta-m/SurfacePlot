"""メインファイル"""
import sys

from PyQt5 import QtWidgets

from surfaceplot.controllers import main_ctrl


def main() -> None:
    """メイン関数"""

    main_ctrl.exporter.root_dir = r'./export'

    app = QtWidgets.QApplication(sys.argv)

    window = main_ctrl.MainWindow()
    window.showMaximized()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
