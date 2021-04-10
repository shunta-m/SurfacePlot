"""画面制御"""
from pathlib import Path

import numpy as np
from PyQt5 import QtCore, QtWidgets

from surfaceplot.controllers import dialog_ctrl as dc
from surfaceplot.models import (interpolate as ip,
                                export)
from surfaceplot.views import main_view

interpolate = ip.InterpolatedImage()
exporter = export.Export()


class MainWindow(QtWidgets.QMainWindow):
    """メイン画面

    Attributes
    ----------
    export_path: Path
        データを出力する時の保存ディレクトリ
    ui: main_view.MainWindowUI
        UI
    """

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(MainWindow, self).__init__(*args, **kwargs)

        self.ui = main_view.MainWindowUI()
        self.ui.setup_ui(self)

        self.init_ui()
        self.connect_slot()

    def init_ui(self) -> None:
        """UI初期化処理中"""

        num: int = interpolate.resolution
        self.ui.intpola_num_spin.setValue(num)

        self.ui.method_combo.addItems([m.value for m in ip.Methods])

    def connect_slot(self) -> None:
        """スロット接続"""

        self.ui.load_btn.clicked.connect(self.load_csv)
        self.ui.export_btn.clicked.connect(self.show_export_dialog)

        self.ui.intpola_num_spin.valueChanged.connect(self.change_interpolate_num)
        self.ui.method_combo.currentTextChanged.connect(self.change_interpolate_method)
        self.ui.coord_check.stateChanged.connect(self.show_origin_coord)
        self.ui.reset_bar_btn.clicked.connect(self.ui.surface_plot.colormap.color_bar.autoScaleFromImage)

        self.ui.surface_plot.colormap.getHCrossSection.connect(self.change_index_to_coord_h)
        self.ui.surface_plot.colormap.getVCrossSection.connect(self.change_index_to_coord_v)

    @QtCore.pyqtSlot(int)
    def change_interpolate_num(self, points: int) -> None:
        """画像補間点数を変更する

        Parameters
        ----------
        points: int
            補間点数
        """

        interpolate.resolution = points
        if self.ui.surface_plot.current_image is None:
            return

        # 補間画像際作成
        interpolate.make_xy_grid()
        method = self.ui.method_combo.currentText()
        image = interpolate.calc_griddata(method)
        self.ui.surface_plot.colormap.resize_image(image)

        # 座標点再表示
        self.show_origin_coord()

    @QtCore.pyqtSlot(str)
    def change_interpolate_method(self, method: str) -> None:
        """補間方法を変えた画像を表示する. method_comboが変わった時実行

        Parameters
        ----------
        method: str
            補間方法
        """

        if interpolate.original_data is None:
            return

        image = interpolate.calc_griddata(method)
        self.ui.surface_plot.set_image(image)

    @QtCore.pyqtSlot(np.ndarray, int)
    def change_index_to_coord_h(self, _, pos: int) -> None:
        """self.ui.surface_plot.colormap.hcs_lineが動いた時実行
        画像の断面表示場所のインデックスを実際の座標値に変換する

        Parameters
        ----------
        _: np.ndarray
            断面データ. 使わないので捨てる
        pos: int
            画像の断面表示個所インデックス
        """

        y = interpolate.interpolated_y_coord
        coord = y[pos]
        self.ui.surface_plot.title_label.set_text(f"{coord:.3f}", 'h')

    @QtCore.pyqtSlot(np.ndarray, int)
    def change_index_to_coord_v(self, _, pos: int) -> None:
        """self.ui.surface_plot.colormap.vcs_lineが動いた時実行
        画像の断面表示場所のインデックスを実際の座標値に変換する

        Parameters
        ----------
        _: np.ndarray
            断面データ. 使わないので捨てる
        pos: int
            画像の断面表示個所インデックス
        """

        x = interpolate.interpolated_x_coord
        coord = x[pos]
        self.ui.surface_plot.title_label.set_text(f"{coord:.3f}", 'v')

    @QtCore.pyqtSlot(tuple)
    def export(self, selected: tuple) -> None:
        """データを出力する

        Parameters
        ----------
        selected: tuple
            出力するデータを選択したタプル. 中身はbool
            (image, image(coord), hori, vert)の4つの順で、出力する時True
        """

        image = self.ui.surface_plot.current_image
        x = interpolate.interpolated_x_coord
        y = interpolate.interpolated_y_coord

        method = self.ui.method_combo.currentText()

        if selected[0]:
            exporter.export_ndarray(image, fr"_image_{method}")

        if selected[1]:
            df = ip.make_intpola_image_at_coord(image, x, y)
            exporter.export_dataframe(df, rf"_image_coord_{method}")

        if selected[2]:
            curve = self.ui.surface_plot.hcs_plot.curve.yData
            hcs_data = export.to_df(np.c_[x, curve],
                                    ('x', 'value'))

            pos = int(self.ui.surface_plot.colormap.hcs_line.getYPos())
            coord = y[pos]

            suffix = fr"_hcs_{coord:.3f}_{method}"
            exporter.export_dataframe(hcs_data, suffix)

        if selected[3]:
            curve = self.ui.surface_plot.vcs_plot.curve.xData
            vcs_data = export.to_df(np.c_[y, curve],
                                    ('y', 'value'))

            pos = int(self.ui.surface_plot.colormap.vcs_line.getXPos())
            coord = x[pos]

            suffix = fr"_vcs_{coord:.3f}_{method}"
            exporter.export_dataframe(vcs_data, suffix)

    @QtCore.pyqtSlot()
    def load_csv(self) -> None:
        """csvファイルを探す. load_btnが押されたとき実行"""

        filepath, extension = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                    'Open csv file',
                                                                    '',
                                                                    '*csv;;All Files(*)')
        if extension != '*csv':
            return

        try:
            interpolate.set_filepath(filepath)
        except (ip.NotCsvError, IndexError) as ex:
            self.show_error_message(ex)
            return

        filename: str = Path(filepath).stem
        self.ui.surface_plot.set_title(filename)
        exporter.filename = filename

        method = self.ui.method_combo.currentText()
        try:
            image = interpolate.calc_griddata(method)
        except ValueError as ex:
            self.show_error_message(ex)
            return

        xrange = interpolate.get_coord_range('x')
        yrange = interpolate.get_coord_range('y')

        self.ui.surface_plot.set_image(image, xrange, yrange)

        # 画像読み込み時は十字線を0に戻す
        self.ui.surface_plot.colormap.hcs_line.setPos(0)
        self.ui.surface_plot.colormap.vcs_line.setPos(0)

        self.show_origin_coord()

    @QtCore.pyqtSlot()
    def show_export_dialog(self) -> None:
        """ダイアログ表示"""

        image = self.ui.surface_plot.current_image
        if image is None:
            QtWidgets.QMessageBox.critical(self,
                                           'Error',
                                           'データを読み込んでいません')
            return

        dialog = dc.ExDialog(self)
        dialog.exportSelected.connect(self.export)
        dialog.show()

    @QtCore.pyqtSlot()
    def show_origin_coord(self) -> None:
        """チェックボックスがついた時, 元座標の点を表示する"""

        image = self.ui.surface_plot.current_image
        if image is None:
            return

        if not self.ui.coord_check.isChecked():
            self.ui.surface_plot.colormap.coord.clear()
            self.update()
            return

        xcoord = interpolate.original_x_coord
        ycoord = interpolate.original_y_coord

        self.ui.surface_plot.colormap.coord.set_data(xcoord, ycoord, image.shape)

    def show_error_message(self, ex: Exception) -> None:
        """エラー内容を表示する

        Parameters
        ----------
        ex: Exception
            例外
        """

        QtWidgets.QMessageBox.critical(self, 'Error', f"{ex}")


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(Path(r''))
    window.showMaximized()
    sys.exit(app.exec_())
