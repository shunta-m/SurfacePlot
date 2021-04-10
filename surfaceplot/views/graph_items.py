"""グラフ"""
from typing import Optional, Tuple

import colorcet as cc
import numpy as np
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
from pgcolorbar.colorlegend import ColorLegendItem

from surfaceplot.views import style


class XImageAxis(pg.AxisItem):
    """pg.PlotItemのX軸をデータの座標に変える

    PlotItem内に表示した画像の軸値は画像サイズになってしまうのでそれを座標値に直す
    (見た目上座標値になるだけで数値までは変わっていない).

    例) 画像サイズが(1000, 500), 座標データ範囲が最小：最大 = 0:100の時
    ※ X軸の値を変えるので画像サイズで使用するのは1000の方

    coe = (100 - 0) / 1000 = 0.1
    式は
    座標データ換算値 = coe * 画像ピクセル値 = 0.1 * 画像ピクセル値


    Attributes
    ----------
    points: int
        画像横(x軸)方向のピクセル数 (画像横サイズ)
    range: Tuple[float, float]
        x座標データの最小、最大値
    coe: int
        points, rangeから計算した座標換算係数
    """

    points = 1
    range_ = (0.0, 1.0)
    coe = 1

    def __init__(self, *args, **kwargs) -> None:
        super(XImageAxis, self).__init__(orientation='bottom', *args, **kwargs)

    def tickStrings(self, values, scale, spacing) -> list:
        """tick表記変更"""

        return [f"{self.coe * value + self.range_[0]:.3f}" for value in values]

    @classmethod
    def change_data_range(cls, range_: tuple) -> None:
        """データの最大値, 最小値が変わった時, 座標換算係数を再計算する

        Parameters
        ----------
        range_: tuple
            データの最小値, 最大値. (min, max)
        """

        cls.range_ = range_
        cls.coe = (cls.range_[1] - cls.range_[0]) / cls.points

    @classmethod
    def change_x_size(cls, points: int) -> None:
        """画像サイズが変わった時, 座標換算係数を再計算する

        Parameters
        ----------
        points: int
            X軸の画像サイズ
        """

        cls.points = points
        cls.coe = (cls.range_[1] - cls.range_[0]) / cls.points


class YImageAxis(pg.AxisItem):
    """pg.PlotItemのY軸をデータの座標に変える

    PlotItem内に表示した画像の軸値は画像サイズになってしまうのでそれを座標値に直す
    (見た目上座標値になるだけで数値までは変わっていない).

    例) 画像サイズが(1000, 500), 座標データ範囲が最小：最大 = 0:100の時
    ※ Y軸の値を変えるので画像サイズで使用するのは500の方

    coe = (100 - 0) / 500 = 0.2
    式は
    座標データ換算値 = coe * 画像ピクセル値 = 0.2 * 画像ピクセル値

    Attributes
    ----------
    points: int
        画像横(x軸)方向のピクセル数 (画像縦サイズ)
    range: Tuple[float, float]
        y座標データの最小、最大値
    coe: int
        points, rangeから計算した座標換算係数
    """

    points = 1
    range_ = (0.0, 1.0)
    coe = 1

    def __init__(self, orientation: str = 'left', *args, **kwargs) -> None:
        super(YImageAxis, self).__init__(orientation=orientation, *args, **kwargs)

    def tickStrings(self, values, scale, spacing) -> list:
        """tick表記変更"""

        return [f"{self.coe * value + self.range_[0]:.3f}" for value in values]

    @classmethod
    def change_data_range(cls, range_: tuple) -> None:
        """データの最大値, 最小値が変わった時, 座標換算係数を再計算する

        Parameters
        ----------
        range_: tuple
            データの最小値, 最大値. (min, max)
        """

        cls.range_ = range_
        cls.coe = (cls.range_[1] - cls.range_[0]) / cls.points

    @classmethod
    def change_y_size(cls, points: int) -> None:
        """画像サイズが変わった時, 座標換算係数を再計算する

        Parameters
        ----------
        points: int
            Y軸の画像サイズ
        """

        cls.points = points
        cls.coe = (cls.range_[1] - cls.range_[0]) / cls.points


class CoordScatter(pg.ScatterPlotItem):
    """座標点"""

    def __init__(self, *args, **kwargs):
        super(CoordScatter, self).__init__(*args, **kwargs)

        self.setSize(6)
        self.setPen(pg.mkPen('#fff', width=2))
        self.setBrush(pg.mkBrush('#000'))

    def set_data(self, xpoints: np.ndarray, ypoints: np.ndarray, shape: tuple) -> None:
        """座標点に黒丸を置く

        Parameters
        ----------
        xpoints: np.ndarray
            x座標データ
        ypoints: np.ndarray
            y座標データ
        shape: tuple
            画像サイズ. (height, width)
        """

        xmin, xmax = np.min(xpoints), np.max(xpoints)
        ymin, ymax = np.min(ypoints), np.max(ypoints)

        x = (xpoints - xmin) / (xmax - xmin) * shape[1]
        y = (ypoints - ymin) / (ymax - ymin) * shape[0]

        self.setData(x, y)


class ColormapWidget(QtWidgets.QGraphicsWidget):
    """カラーマップウィジット

    getHCrossSection
        self.hcs_lineが動いた時発光するシグナル
    getVCrossSection
        self.vcs_lineが動いた時発光するシグナル
    getDataRange
        データが更新された時発光するシグナル
        最小、最大、差分（最大 - 最小）を送信する

    Attributes
    ----------
    image: pg.ImageItem
        ヒートマップで表示する画像
    view_box: pg.ViewBox
        画像表示用ボックス
    plot: pg.PlotItem
        imageの画像サイズを表示するプロット
    horizontal_line: pg.pg.InfiniteLine
        長手方向断面グラフ用直線
    color_bar: ColorLegendItem
        カラーバー
    layout: QtWidgets.QGraphicsGridLayout
        plotとcolor_barを設置するレイアウト
    """

    getHCrossSection = QtCore.pyqtSignal(np.ndarray, int)
    getVCrossSection = QtCore.pyqtSignal(np.ndarray, int)
    getDataRange = QtCore.pyqtSignal(float, float, float)

    def __init__(self, title: str = '', bar_label: str = '',
                 *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        title: str default=''
            グラフタイトル
        bar_label: str default=''
            カラーバーラベル
        """

        super(ColormapWidget, self).__init__(*args, **kwargs)

        self.image = pg.ImageItem(axisOrder='row-major')
        self.image.setLookupTable(self.make_lookup_table())

        self.view_box = pg.ViewBox(lockAspect=True)
        self.view_box.addItem(self.image)

        self.xaxis = XImageAxis()
        self.yaxis = YImageAxis()

        self.plot = pg.PlotItem(viewBox=self.view_box,
                                axisItems={'bottom': self.xaxis,
                                           'left': self.yaxis, })
        self.plot.setTitle(title)
        self.plot.setLabels(bottom='X', left='Y')

        self.coord = CoordScatter()
        self.coord.setZValue(10)
        self.plot.addItem(self.coord)

        self.hcs_line = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('#fff'))
        self.vcs_line = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('#fff'))
        self.plot.addItem(self.hcs_line, ignoreBounds=True)
        self.plot.addItem(self.vcs_line, ignoreBounds=True)
        self.hcs_line.setZValue(20)
        self.vcs_line.setZValue(20)

        self.color_bar = ColorLegendItem(imageItem=self.image,
                                         label=bar_label)

        self.layout = QtWidgets.QGraphicsGridLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)
        self.layout.addItem(self.plot, 0, 0)
        self.layout.addItem(self.color_bar, 0, 2)
        self.setLayout(self.layout)

        self.hcs_line.sigPositionChanged.connect(self.get_hcross_section)
        self.vcs_line.sigPositionChanged.connect(self.get_vcross_section)

    def change_line_pos(self, ratio: float) -> None:
        """画像サイズが変わった時に十字線を同じ場所に表示するよう移動する

        Parameters
        ----------
        ratio: float
            画像サイズの変化比率
        """

        hcs_pos = self.hcs_line.getYPos()
        vcs_pos = self.vcs_line.getXPos()

        self.hcs_line.setPos(int(ratio * hcs_pos))
        self.vcs_line.setPos(int(ratio * vcs_pos))

    def get_data_range(self) -> None:
        """データが更新されてた時、最小、最大、差分（最大 - 最小）を計算する"""

        image: np.ndarray = self.image.image
        if image is None:
            return

        maximum, minimum = float(np.nanmax(image)), float(np.nanmin(image)),
        delta = maximum - minimum
        self.getDataRange.emit(maximum, minimum, delta)

    def get_hcross_section(self) -> None:
        """x軸と平行方向の断面データを取得する. 画像がなければ何もしない"""

        image: np.ndarray = self.image.image
        if image is None:
            return

        line_pos = int(self.hcs_line.getYPos())
        if 0 <= line_pos < image.shape[0]:
            self.getHCrossSection.emit(image[line_pos], line_pos)

    def get_vcross_section(self) -> None:
        """y軸と平行方向の断面データを取得する. 画像がなければ何もしない"""

        image: np.ndarray = self.image.image
        if image is None:
            return

        line_pos = int(self.vcs_line.getXPos())
        if 0 <= line_pos < image.shape[1]:
            self.getVCrossSection.emit(image[:, line_pos], line_pos)

    def reset_color_levels(self) -> None:
        """カラーバーの表示値範囲を画像データと合わせる.
        カラーバーの操作は有効に戻す.

        See Also
        ----------
        set_mouse_enabled_bar
        """

        self.color_bar.resetColorLevels()

    def resize_image(self, image: np.ndarray) -> None:
        """画像サイズ変更する時, 十時線の位置調整を行った後画像入れ替え

        Parameters
        ----------
        image: np.ndarray
            新しい画像
        """

        old_image = self.image.image
        ratio: float = len(image) / len(old_image)

        self.set_image(image)
        self.change_line_pos(ratio)

    def set_image(self, image: np.ndarray) -> None:
        """画像を挿入する.

         1回目の挿入を想定している為,

         - 画像サイズの最適化
         - カラーバーの範囲を画像データに合わせる

        Parameters
        ----------
        image: np.ndarray
            表示したい画像配列
        """

        self.image.setImage(image)

        self.plot.autoBtnClicked()
        self.color_bar.autoScaleFromImage()

        shape = image.shape
        self.xaxis.change_x_size(shape[1])
        self.yaxis.change_y_size(shape[0])

        self.get_data_range()
        self.get_hcross_section()
        self.get_vcross_section()

    @staticmethod
    def make_lookup_table() -> np.ndarray:
        """colorcet.b_***を使用してlookup table作成"""

        def hex_to_rgb(hex_: str) -> list:
            h = hex_.lstrip('#')
            return [int(h[i:i + 2], 16) for i in (0, 2, 4)]

        color_palette = cc.b_rainbow_bgyrm_35_85_c71
        rgb = list(map(hex_to_rgb, color_palette))

        return np.array(rgb, dtype=np.uint8)


class GraphTitleLabel(QtWidgets.QGraphicsWidget):
    """グラフタイトルラベル

    Attributes
    ----------
    title: pg.LabelItem()
        メインタイトル
    hcs: pg.LabelItem()
        横方向断面位置表示
    vcs: pg.LabelItem()
        縦方向断面位置表示
    """

    def __init__(self, *args, **kwargs) -> None:
        super(GraphTitleLabel, self).__init__(*args, **kwargs)

        title_prefix = pg.LabelItem(style.graph_title('Image Title:'), justify='left')
        cross_section = pg.LabelItem(style.graph_title('Cross section'), justify='left')
        hcs_prefix = pg.LabelItem(style.graph_title('Y:'), justify='left')
        vcs_prefix = pg.LabelItem(style.graph_title('X:'), justify='left')

        self.title = pg.LabelItem(justify='left')
        self.hcs = pg.LabelItem(justify='left')
        self.vcs = pg.LabelItem(justify='left')

        self.layout = QtWidgets.QGraphicsGridLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)
        self.layout.addItem(title_prefix, 0, 0)
        self.layout.addItem(self.title, 0, 1)
        self.layout.addItem(cross_section, 0, 2)
        self.layout.addItem(vcs_prefix, 0, 3)
        self.layout.addItem(self.vcs, 0, 4)
        self.layout.addItem(hcs_prefix, 0, 5)
        self.layout.addItem(self.hcs, 0, 6)

        self.setLayout(self.layout)

        self.layout.setColumnStretchFactor(1, 4)
        self.layout.setColumnStretchFactor(4, 1)
        self.layout.setColumnStretchFactor(6, 1)

    def set_text(self, text: str, hv: str) -> None:
        """self.hcs or vcsにテキストをいれる

        Parameters
        ----------
        text: str
            テキスト
        hv: str
            hcs, vcsのどちらにいれるか指定
            'h'ならhcs
            'v'ならvcs
        """

        if hv == 'h':
            self.hcs.setText(style.graph_title(text))
        elif hv == 'v':
            self.vcs.setText(style.graph_title(text))
        else:
            return


class DataLabel(QtWidgets.QGraphicsWidget):
    """グラフの最大・最小範囲を表示するラベル"""

    def __init__(self, *args, **kwargs) -> None:
        super(DataLabel, self).__init__(*args, **kwargs)

        header = pg.LabelItem(style.data_label('Data range'))
        max_prefix = pg.LabelItem(style.data_label('Max:'), justify='left')
        min_prefix = pg.LabelItem(style.data_label('Min:'), justify='left')
        range_prefix = pg.LabelItem(style.data_label('Max - Min:'), justify='left')

        self.max_label = pg.LabelItem(style.data_label(str(0)), justify='left')
        self.min_label = pg.LabelItem(style.data_label(str(0)), justify='left')
        self.delta_label = pg.LabelItem(style.data_label(str(0)), justify='left')

        self.layout = QtWidgets.QGraphicsGridLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)
        self.layout.addItem(header, 0, 0, 1, 2)
        self.layout.addItem(max_prefix, 1, 0)
        self.layout.addItem(self.max_label, 1, 1)
        self.layout.addItem(min_prefix, 2, 0)
        self.layout.addItem(self.min_label, 2, 1)
        self.layout.addItem(range_prefix, 3, 0)
        self.layout.addItem(self.delta_label, 3, 1)

        self.layout.setColumnStretchFactor(0, 2)
        self.layout.setColumnStretchFactor(1, 1)

        self.setLayout(self.layout)

        self.setToolTip('データ範囲表示')

    @QtCore.pyqtSlot(float, float, float)
    def set_text(self, maximum: float, minimum: float, delta: float) -> None:
        """テキスト入力

        Parameters
        ----------
        maximum: float
            データの最大値
        minimum: float
            データの最小値
        delta: float
            データ範囲（差分）
        """

        self.max_label.setText(style.data_label(f"{maximum:.3f}"))
        self.min_label.setText(style.data_label(f"{minimum:.3f}"))
        self.delta_label.setText(style.data_label(f"{delta:.3f}"))


class CrossSectionPlot(pg.PlotItem):
    """断面グラフの親

    rangeをクラス変数で共有したかったので作成
    PlotItem.autoBtnClickedをした時に使用

    Attributes
    ----------
    range: tuple
        表示中画像の最小、最大値
    curve: pg.PlotCurveItem()
        断面を表示する線
    cursor_point: pg.ScatterPlotItem
        マウスカーソルが置かれている個所のデータを表示する点

    See Also
    ----------
    HCrossSectionPlot
        横方向(x軸と並行)の断面グラフ
    VCrossSectionPlot
        縦方向(y軸と並行)の断面グラフ
    """

    range = (0, 1)

    def __init__(self, direction: str, *args, **kwargs) -> None:
        """初期化処理

        Parameters
        ----------
        direction: str
            断面グラフの方向, V or H
        """

        super(CrossSectionPlot, self).__init__(*args, **kwargs)

        self.showGrid(True, True, alpha=0.5)

        self.curve = pg.PlotCurveItem()
        self.cursor_point = pg.ScatterPlotItem(pen=pg.mkPen('#fff'),
                                               brush=pg.mkBrush('#f00'))

        self.curve.setZValue(20)
        self.cursor_point.setZValue(10)

        self.addItem(self.curve, ignoreBounds=False)
        self.addItem(self.cursor_point, ignoreBounds=True)

        if direction.upper() == 'H':
            self.setToolTip('横方向断面グラフ<br>Horizontal cross section graph')
        elif direction.upper() == 'V':
            self.setToolTip('縦方向断面グラフ<br>Vertical cross section graph')

    @classmethod
    def set_range(cls, range_: tuple) -> None:
        """グラフの最小、最大値を変える

        Parameters
        ----------
        range_: tuple
            グラフ表示範囲. (min, max)
        """

        cls.range = range_


class HCrossSectionPlot(CrossSectionPlot):
    """横方向(x軸と並行)の断面グラフ

    PlotItem.autoBtnClickedをオーバーライドしている

    動作を以下に変更
    変更前: x, y軸ともにオートスケールに戻す
    変更後: xはオートスケールに, y軸は表示画像データの最小、最大範囲に合わせる
    """

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(HCrossSectionPlot, self).__init__(*args, **kwargs)

    @QtCore.pyqtSlot()
    def autoBtnClicked(self) -> None:
        """オートボタンを押した時の関数をオーバーライド

        x軸はオートスケールで戻す
        y軸は表示画像の最大、最小範囲に戻す
        """

        self.enableAutoRange(self.vb.XAxis, True)
        self.setYRange(*self.range)
        self.autoBtn.hide()

    def set_cursor_point(self, point: float, data: float) -> None:
        """カーソルが動いた時実行.
        グラフ内にカーソルが置かれてある箇所のデータを表示

        Parameters
        ----------
        point: float
            カーソルの位置
        data: float
            point箇所のデータ
        """

        self.cursor_point.setData([point], [data])


class VCrossSectionPlot(CrossSectionPlot):
    """縦方向(y軸と並行)の断面グラフ

    PlotItem.autoBtnClickedをオーバーライドしている

    動作を以下に変更
    変更前: x, y軸ともにオートスケールに戻す
    変更後: yはオートスケールに, x軸は表示画像データの最小、最大範囲に合わせる
    """

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(VCrossSectionPlot, self).__init__(*args, **kwargs)

        self.hideAxis('left')
        self.vb.invertX(True)

    @QtCore.pyqtSlot()
    def autoBtnClicked(self) -> None:
        """オートボタンを押した時の関数をオーバーライド

        y軸はオートスケールで戻す
        x軸は表示画像の最大、最小範囲に戻す
        """

        self.enableAutoRange(self.vb.YAxis, True)
        self.setXRange(*self.range)
        self.autoBtn.hide()

    def set_cursor_point(self, point: float, data: float) -> None:
        """カーソルが動いた時実行.
        グラフ内にカーソルが置かれてある箇所のデータを表示

        Parameters
        ----------
        point: float
            カーソルの位置
        data: float
            point箇所のデータ
        """

        self.cursor_point.setData([data], [point])


class SurfacePlot(pg.GraphicsLayoutWidget):
    """断面データ表示付きカラーマップ

    Attributes
    ----------
    colormap: ColormapWidget
        カラーマップ
    cs_curve: pg.PlotCurveItem
        断面データ曲線. csは cross section
    cs_plot: pg.PlotItem
        断面データグラフ. csは cross section
    """

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(SurfacePlot, self).__init__(*args, **kwargs)

        self.title_label = GraphTitleLabel()
        self.data_label = DataLabel()

        self.colormap = ColormapWidget()

        self.xaxis = XImageAxis()
        self.yaxis = YImageAxis(orientation='right')

        self.hcs_plot = HCrossSectionPlot('H', axisItems={'bottom': self.xaxis})
        self.vcs_plot = VCrossSectionPlot('V', axisItems={'right': self.yaxis})

        self.addItem(self.title_label, 0, 0, 1, 2)
        self.addItem(self.colormap, 1, 0)
        self.addItem(self.vcs_plot, 1, 1)
        self.addItem(self.hcs_plot, 2, 0)
        self.addItem(self.data_label, 2, 1)

        self.ci.layout.setRowStretchFactor(0, 1)
        self.ci.layout.setRowStretchFactor(1, 12)
        self.ci.layout.setRowStretchFactor(2, 6)

        self.ci.layout.setColumnStretchFactor(0, 4)
        self.ci.layout.setColumnStretchFactor(1, 1)

        self.colormap.getDataRange.connect(self.data_label.set_text)
        self.colormap.getHCrossSection.connect(self.plot_hcross_section)
        self.colormap.getVCrossSection.connect(self.plot_vcross_section)

        self.proxy = pg.SignalProxy(self.colormap.scene().sigMouseMoved,
                                    rateLimit=60,
                                    slot=self.get_cursor_data)

    @property
    def current_image(self) -> Optional[np.ndarray]:
        """現在表示中の画像を返す
        何も表示していない時Noneを返す
        """

        return self.colormap.image.image

    @QtCore.pyqtSlot(tuple)
    def get_cursor_data(self, evt) -> None:
        """マウスカーソルが動いた時実行.
        カーソルが置かれてある箇所の座標とデータを取得

        Parameters
        ----------
        evt: tuple
            画面のピクセル単位の座標
            ex) (PyQt5.QtCore.QPointF(2.0, 44.0),)
        """

        image = self.colormap.image.image
        if image is None:
            return

        image_y, image_x = image.shape
        # 画面のピクセル座標取得 ex) pos=PyQt5.QtCore.QPointF(2.0, 44.0)
        pos = evt[0]
        # posがcolormap内の座標だったら
        if not self.colormap.sceneBoundingRect().contains(pos):
            return

        # グラフの座標取得
        # ex) mousePoint=PyQt5.QtCore.QPointF(141.6549821809388, 4.725564511858496)
        cursor_point = self.colormap.view_box.mapSceneToView(pos)
        x_point = cursor_point.x()
        y_point = cursor_point.y()

        if 0 <= x_point < image_x and 0 <= y_point < image_y:
            data = image[int(y_point), int(x_point)]
            self.hcs_plot.set_cursor_point(x_point, data)
            self.vcs_plot.set_cursor_point(y_point, data)

    @QtCore.pyqtSlot(np.ndarray, int)
    def plot_hcross_section(self, data: np.ndarray, _: int) -> None:
        """断面データをプロットする
        _は使用しないので捨てる

        Parameters
        ----------
        data: np.ndarray
            断面データ
        _: int
            断面位置情報
        """

        self.hcs_plot.curve.setData(data)
        # self.label.hcs.setText(style.graph_title(f"{pos}"))

    @QtCore.pyqtSlot(np.ndarray, int)
    def plot_vcross_section(self, data: np.ndarray, _: int) -> None:
        """断面データをプロットする
        _は使用しないので捨てる

        Parameters
        ----------
        data: np.ndarray
            断面データ
        _: int
            断面位置情報
        """

        y = np.arange(len(data))
        self.vcs_plot.curve.setData(data, y)
        # self.label.vcs.setText(style.graph_title(f"{pos}"))

    def set_image(self, image: np.ndarray, xrange: tuple = None, yrange: tuple = None) -> None:
        """画像を挿入する. 断面グラフのx軸を画像座標に合わせる

        Parameters
        ----------
        image: np.ndarray
            画像配列
        xrange: tuple default=None
            x軸の座標範囲. (min, max)
        yrange: tuple default=None
            y軸の座標範囲. (min, max)
        """

        self.colormap.set_image(image)

        height, width = image.shape
        XImageAxis.change_x_size(width)
        YImageAxis.change_y_size(height)

        image_range = np.nanmin(image), np.nanmax(image)
        CrossSectionPlot.set_range(image_range)

        self.vcs_plot.setXRange(*image_range)
        self.hcs_plot.setYRange(*image_range)

        self.hcs_plot.autoBtnClicked()
        self.vcs_plot.autoBtnClicked()

        if xrange is not None:
            XImageAxis.change_data_range(xrange)
        if yrange is not None:
            YImageAxis.change_data_range(yrange)

    def set_title(self, title: str) -> None:
        """グラフタイトルを設定する

        Parameters
        ----------
        title: str
            グラフタイトル
        """

        self.title_label.title.setText(style.graph_title(title))


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    window = SurfacePlot()
    window.show()

    sys.exit(app.exec_())
