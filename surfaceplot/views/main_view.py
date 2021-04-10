"""メイン画面のUIモジュール"""
from PyQt5 import QtCore, QtGui, QtWidgets

from surfaceplot.views import (graph_items as gi,
                               style)


class MainWindowUI:
    """メイン画面UIクラス"""

    def setup_ui(self, main_window: QtWidgets.QMainWindow) -> None:
        """UIをセットアップする"""

        main_window.setWindowTitle('Surface plot window')
        main_window.resize(-1, -1)
        font = QtGui.QFont()
        font.setPointSize(12)
        main_window.setFont(font)

        self.make_widgets(main_window)
        self.make_layout()
        self.add_widgets_to_layouts(main_window)
        self.set_toolbar(main_window)
        self.set_menus(main_window)

    def make_widgets(self, main_window: QtWidgets.QMainWindow) -> None:
        """ウィジット作成"""
        self.central_widget = QtWidgets.QWidget(main_window)

        self.surface_plot = gi.SurfacePlot()
        self.load_btn = QtWidgets.QPushButton('Load CSV')
        self.load_btn.setShortcut('Shift+L')
        self.load_btn.setToolTip('CSV読み込み<br>Shift+L')

        self.load_btn.setStyleSheet(style.load_btn())
        self.export_btn = QtWidgets.QPushButton('Export')
        self.export_btn.setShortcut('Shift+E')
        self.export_btn.setToolTip('CSV出力<br>Shift+E')

        self.intpola_num_widget = QtWidgets.QWidget()
        self.intpola_num_spin = QtWidgets.QSpinBox()
        self.intpola_num_spin.setRange(1, 100)
        self.intpola_num_spin.setToolTip('補間点数変更<br>1 ~ 100')

        self.method_widget = QtWidgets.QWidget()
        self.method_combo = QtWidgets.QComboBox()
        self.method_combo.setToolTip('補間方法変更')

        self.coord_widget = QtWidgets.QWidget()
        self.coord_check = QtWidgets.QCheckBox('Show measure coord')
        self.coord_check.setShortcut('Shift+S')
        self.coord_check.setToolTip('元データ座標の表示/非表示<br>Shift+S')

        self.reset_bar_widget = QtWidgets.QWidget()
        self.reset_bar_btn = QtWidgets.QPushButton('Reset')
        self.reset_bar_btn.setShortcut('Shift+R')
        self.reset_bar_btn.setToolTip('カラーバー範囲リセット<br>Shift+R')

    def make_layout(self) -> None:
        """レイアウト作成"""
        self.main_layout = QtWidgets.QVBoxLayout()
        self.top_layout = QtWidgets.QHBoxLayout()

        # ツールバー用レイアウト
        self.intpola_layout = QtWidgets.QVBoxLayout()
        self.method_layout = QtWidgets.QVBoxLayout()
        self.coord_layout = QtWidgets.QVBoxLayout()
        self.reset_bar_layout = QtWidgets.QVBoxLayout()

    def add_widgets_to_layouts(self, main_window: QtWidgets.QMainWindow) -> None:
        """レイアウトにウィジットを追加"""

        self.main_layout.addWidget(self.surface_plot)
        self.main_layout.addWidget(self.load_btn)
        self.main_layout.addWidget(self.export_btn)

        self.central_widget.setLayout(self.main_layout)
        main_window.setCentralWidget(self.central_widget)

        # ツールバーウィジットのレイアウト配置
        self.intpola_layout.addWidget(self.intpola_num_spin)
        self.intpola_layout.addWidget(QtWidgets.QLabel('Interpolate points'))
        self.intpola_num_widget.setLayout(self.intpola_layout)

        self.method_layout.addWidget(self.method_combo)
        self.method_layout.addWidget(QtWidgets.QLabel('Interpolate methods'))
        self.method_widget.setLayout(self.method_layout)

        self.coord_layout.addWidget(self.coord_check)
        self.coord_layout.addWidget(QtWidgets.QLabel('Measurement coordinate'))
        self.coord_widget.setLayout(self.coord_layout)

        self.reset_bar_layout.addWidget(self.reset_bar_btn)
        self.reset_bar_layout.addWidget(QtWidgets.QLabel('Colorbar'), alignment=QtCore.Qt.AlignCenter)
        self.reset_bar_widget.setLayout(self.reset_bar_layout)

    def set_toolbar(self, main_window: QtWidgets.QMainWindow) -> None:
        """ツールバー作成"""

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setWindowTitle('ToolBar')

        self.toolbar.addWidget(self.intpola_num_widget)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.method_widget)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.coord_widget)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.reset_bar_widget)
        self.toolbar.addSeparator()

        main_window.addToolBar(self.toolbar)

    def set_menus(self, main_window: QtWidgets.QMainWindow) -> None:
        """メニューバーセット"""
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setToolTip('ツールバーの表示/非表示変更<br>ショートカット：Ctrl V')
        main_window.setMenuBar(self.menubar)

        self.view_menu = self.menubar.addMenu('&View')
        self.view_menu.addAction(self.toolbar.toggleViewAction())
        self.toolbar.toggleViewAction().setShortcut('Ctrl+V')


if __name__ == '__main__':
    """"""
    import sys

    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()

    ui = MainWindowUI()
    ui.setup_ui(window)

    window.showMaximized()

    sys.exit(app.exec_())
