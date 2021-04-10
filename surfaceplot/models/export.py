"""データ出力用"""
import datetime as dt
from pathlib import Path
import re
from typing import Optional

import numpy as np
import pandas as pd

NOT_USED_STRING = r'[\\/:*?"<>|]+'
REPLACE_STRING = r'-'


def replace_string(filename: str) -> str:
    """ファイル名で使用できない文字を置き換える

    Parameters
    ----------
    filename: str
        ファイル名
    """

    return re.sub(NOT_USED_STRING, REPLACE_STRING, filename)


def to_df(data: np.ndarray, col: tuple) -> pd.DataFrame:
    """numpy配列をデータフレームに変換"""

    df = pd.DataFrame(data=data, columns=col)
    return df.set_index(col[0])


class Export:
    """ファイル出力クラス

    Attributes
    ----------
    _filename: Optional[str]
        出力するファイル名. 表示中のデータのファイル名
    _root_dir: Optional[Path]
        出力ファイル保存先ディレクトリパス
    """

    def __init__(self, root_dir: str = None) -> None:
        """初期化処理

        Parameters
        ----------
        root_dir: str
            出力ファイルを保存するディレクトリパス
        """

        self._filename = None

        if root_dir is None:
            self._root_dir = root_dir
            return

        root_dir = repr(root_dir).replace("'", "")
        self._root_dir = Path(root_dir)
        if not self._root_dir.exists():
            self._root_dir.mkdir()

    @property
    def filename(self) -> Optional[str]:
        """self.filename getter"""

        return self._filename

    @filename.setter
    def filename(self, name: str) -> None:
        """self.filename setter"""

        self._filename = replace_string(name)

    @property
    def root_dir(self) -> Optional[Path]:
        """self.root_dir getter"""

        return self._root_dir

    @root_dir.setter
    def root_dir(self, dir_: str) -> None:
        """self.root_dir setter"""

        root_dir = repr(dir_).replace("'", "")
        self._root_dir = Path(root_dir)

        self.check_root_dir_exists()

    def check_root_dir_exists(self) -> None:
        """ルートディレクトリが存在しているか確かめる.
        なければ作成する"""

        if not self._root_dir.exists():
            self._root_dir.mkdir()

    def export_dataframe(self, data: pd.DataFrame, suffix: str) -> None:
        """pandasデータフレームを出力する

        Parameters
        ----------
        data: pd.DataFrame
            出力データ
        suffix: str
            末尾に追加する文字
        """

        if None in (self._root_dir, self._filename):
            return

        self.check_root_dir_exists()

        now = dt.datetime.now().strftime(r'%y%m%d%H%M%S_')
        filename = now + self._filename + suffix + r'.csv'
        filepath = self._root_dir / filename
        data.to_csv(filepath)

    def export_ndarray(self, data: np.ndarray, suffix: str) -> None:
        """numpy配列を出力する

        Parameters
        ----------
        data: np.ndarray
            出力データ
        suffix: str
            末尾に追加する文字
        """

        if None in (self._root_dir, self._filename):
            return

        self.check_root_dir_exists()

        now = dt.datetime.now().strftime(r'%y%m%d%H%M%S_')
        filename = now + self._filename + suffix + r'.csv'
        filepath = self._root_dir / filename
        np.savetxt(filepath, data, delimiter=',')

    @filename.setter
    def filename(self, name: str) -> None:
        """正規表現でファイル名に使えない文字を置換してself.filenameにセット

        Parameters
        ----------
        name: str
            新しくファイル名にしたい文字列
        """

        self._filename = replace_string(name)

    def set_root_dir(self, filename: str) -> None:
        """正規表現でファイル名に使えない文字を置換してself.filenameにセット

        Parameters
        ----------
        filename: str
            新しくファイル名にしたい文字列
        """

        self._filename = replace_string(filename)
