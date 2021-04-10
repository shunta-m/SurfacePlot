"""補間画像を作成する"""
import enum
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import scipy
from scipy import interpolate


class NotCsvError(Exception):
    """ファイルがcsvではなかった時の例外"""


class Methods(enum.Enum):
    """補間方法の列挙型"""

    LINEAR = 'linear'
    CUBIC = 'cubic'
    NEAREST = 'nearest'


class InterpolatedImage:
    """補間画像クラス

    Attributes
    ----------
    original_data: pd.DataFrame
        csv元データ
    x_grid: np.ndarray
        xのグリッド配列
    y_grid: np.ndarray
        yのグリッド配列
    resolution: int
        画像補間の分解能
    """

    def __init__(self, filepath: str = None, resolution: int = 10) -> None:
        """初期化

        Parameters
        ----------
        filepath: str default=''
            csvファイルパス
        resolution: int default = 10
            分解能. デフォルトは座標間を10分割で補間する
        """

        self.resolution = resolution

        if filepath is None:
            self.original_data = None
            self.x_grid, self.y_grid = None, None

            return

        self.set_filepath(filepath)

    @property
    def interpolated_x_coord(self) -> np.ndarray:
        """補間画像のX座標を返す"""

        return self.x_grid[0]

    @property
    def interpolated_y_coord(self) -> np.ndarray:
        """補間画像のY座標を返す"""

        return self.y_grid[:, 0]

    @property
    def original_x_coord(self) -> np.ndarray:
        """元データのX座標を返す"""

        return np.array(self.original_data.iloc[:, 0])

    @property
    def original_y_coord(self) -> np.ndarray:
        """元データのY座標を返す"""

        return np.array(self.original_data.iloc[:, 1])

    def calc_griddata(self, method: str) -> np.ndarray:
        """空白箇所のvaluesを補間した２次元配列計算
        補間関数はscipy.interpolate.griddata

        Parameters
        ----------
        method: str
            補間方法. 'nearest', 'linear', 'cubic' のどれか

        Returns
        ----------
        interpolated: np.ndarray
            scipy.interpolate.griddataで補間した2次元配列
        """

        knew_points = np.array(self.original_data.iloc[:, :-1])
        knew_values = np.array(self.original_data.iloc[:, -1])
        xi = (self.x_grid, self.y_grid)

        try:
            interpolated = interpolate.griddata(knew_points,
                                                knew_values,
                                                xi,
                                                method=method)
        except scipy.spatial.qhull.QhullError as ex:
            raise ValueError('補間画像を作成できません.') from ex

        return interpolated

    def get_coord_range(self, axis: str) -> Tuple[float, float]:
        """座標範囲を返す

        Parameters
        ----------
        axis: str
            'x' or 'y'
        """

        if axis not in ('x', 'y'):
            raise ValueError

        if axis == 'x':
            min_ = np.min(self.original_data.iloc[:, 0])
            max_ = np.max(self.original_data.iloc[:, 0])
        else:
            min_ = np.min(self.original_data.iloc[:, 1])
            max_ = np.max(self.original_data.iloc[:, 1])

        return min_, max_

    def make_xy_grid(self) -> None:
        """x, yのグリッド配列を作成する"""

        x = np.array(self.original_data.iloc[:, 0])
        x_min, x_max = np.min(x), np.max(x)

        y = np.array(self.original_data.iloc[:, 1])
        y_min, y_max = np.min(y), np.max(y)

        resolved_x = np.linspace(x_min, x_max, len(set(x)) * self.resolution)
        resolved_y = np.linspace(y_min, y_max, len(set(y)) * self.resolution)

        self.x_grid, self.y_grid = np.meshgrid(resolved_x, resolved_y)

    def set_filepath(self, filepath: str) -> None:
        """csvファイルを読み込んでデータを作成する

        Parameters
        ----------
        filepath: str
            csvファイルパス
        """

        filepath = repr(filepath).replace("'", "")
        filepath = Path(filepath)
        if filepath.suffix != '.csv':
            raise NotCsvError('csvファイルではありません')

        original_data = pd.read_csv(filepath)
        # 最後の3列をx, y, zと判断する
        self.original_data = original_data.iloc[:, -3:]
        self.make_xy_grid()


def make_intpola_image_at_coord(image: np.ndarray,
                                cols: np.ndarray, idx: np.ndarray) -> pd.DataFrame:
    """補間画像の座標付きcsvを作成する"""

    return pd.DataFrame(data=image, columns=cols, index=idx)
