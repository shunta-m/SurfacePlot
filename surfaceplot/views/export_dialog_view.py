"""export_btnを押した時表示されるダイアログのUI"""

from PyQt5 import QtGui, QtWidgets


class ExDialogUI:
    """export_dialogUIクラス"""

    def setup_ui(self, dialog: QtWidgets.QDialog) -> None:
        """UIをセットアップする"""
        dialog.resize(-1, -1)
        font = QtGui.QFont()
        font.setPointSize(12)
        dialog.setFont(font)

        self.make_widgets()
        self.make_layout()
        self.add_widgets_to_layouts(dialog)

    def make_widgets(self) -> None:
        """ウィジット作成"""

        self.image_check = QtWidgets.QCheckBox('Image (none coord)')
        self.image_coord_check = QtWidgets.QCheckBox('Image (coord)')
        self.hcs_check = QtWidgets.QCheckBox('Horizontal cross section')
        self.vcs_check = QtWidgets.QCheckBox('Vertical cross section')

        self.ok_btn = QtWidgets.QPushButton('OK')
        self.cancel_btn = QtWidgets.QPushButton('Cancel')

    def make_layout(self) -> None:
        """レイアウト作成"""
        self.main_layout = QtWidgets.QVBoxLayout()
        self.image_layout = QtWidgets.QHBoxLayout()
        self.btn_layout = QtWidgets.QHBoxLayout()

    def add_widgets_to_layouts(self, dialog: QtWidgets.QDialog) -> None:
        """レイアウトにウィジットを追加"""

        self.main_layout.addWidget(QtWidgets.QLabel('Select export data'))
        self.main_layout.addLayout(self.image_layout)
        self.main_layout.addWidget(self.hcs_check)
        self.main_layout.addWidget(self.vcs_check)
        self.main_layout.addSpacing(10)
        self.main_layout.addLayout(self.btn_layout)

        dialog.setLayout(self.main_layout)

        self.image_layout.addWidget(self.image_check)
        self.image_layout.addSpacing(10)
        self.image_layout.addWidget(self.image_coord_check)

        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.ok_btn)
        self.btn_layout.addWidget(self.cancel_btn)


if __name__ == '__main__':
    """テスト"""
    import sys

    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QDialog()

    ui = ExDialogUI()
    ui.setup_ui(window)

    window.show()

    sys.exit(app.exec_())
