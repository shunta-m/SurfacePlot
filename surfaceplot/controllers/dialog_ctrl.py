"""export ダイアログ制御"""
from PyQt5 import QtCore, QtWidgets

from surfaceplot.views import export_dialog_view


class ExDialog(QtWidgets.QDialog):
    """出力ダイアログ画面制御

    Attributes
    ----------
    ui: export_dialog_view.ExDialogUI
        ダイアログUI
    """

    exportSelected = QtCore.pyqtSignal(tuple)

    def __init__(self, *args, **kwargs) -> None:
        """初期化処理"""

        super(ExDialog, self).__init__(*args, **kwargs)
        self.setModal(True)

        self.ui = export_dialog_view.ExDialogUI()
        self.ui.setup_ui(self)

        self.connect_slot()

    def connect_slot(self) -> None:
        """スロット接続"""

        self.ui.ok_btn.clicked.connect(self.clicked_ok)
        self.ui.cancel_btn.clicked.connect(self.close)

    def clicked_ok(self) -> None:
        """ok_btnが押された時の動作"""

        result = (self.ui.image_check.isChecked(),
                  self.ui.image_coord_check.isChecked(),
                  self.ui.hcs_check.isChecked(),
                  self.ui.vcs_check.isChecked(),)

        self.exportSelected.emit(result)
        self.exportSelected.disconnect()

        self.close()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = ExDialog()
    window.show()

    sys.exit(app.exec_())
