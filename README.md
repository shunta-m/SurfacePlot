# SurfacePlot

X, Y, Z列を持つcsvから表面プロットを作成します。

| **X** | **Y** | **Z** |
| ----- | ----- | ----- |
| 0.0   | 0.0   | 4.0   |
| 1.0   | 0.0   | 5.0   |
| 2.0   | 0.0   | 7.0   |
| ...   | ...   | ...   |

![screenshot1](/screenshot/screenshot1.png)

# Description

以下の動作が可能です

- 最大100点までの座標間補間
- 補間方法の選択
  - nearest
  - linear
  - cubic
- 表面形状画像に元データ座標点の表示
- カラーバーの操作
- 縦横の断面データ取得
- 表面データ、断面データのcsv出力



# Demo
![demo](/demo/demo.gif)



# Requirements

- Python 3.8.8
- colorcet==2.0.6
- numpy==1.20.1
- pandas==1.2.3
- pgcolorbar==1.1.0
- PyQt5==5.15.4
- pyqtgraph==0.11.1
- scipy==1.6.1



# Install

ダウンロードして環境を整えた後、 `main.py`を実行してください。



# Note

- csvが３列以上ある場合、最後の3列をX, Y, Zと判別します。
- requirements.txtでインストールしてうまくいかない場合、 一度PyQt5をアンインストールして入れ直してください。
- デフォルトの座標間補間点数は10点です。元データを表示したい場合点数を１にして補間方法をnearestにしてください。

