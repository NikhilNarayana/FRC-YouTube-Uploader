# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'selectorUI.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ui_selector(object):
    def setupUi(self, ui_selector):
        ui_selector.setObjectName("ui_selector")
        ui_selector.resize(584, 138)
        self.verticalLayout = QtWidgets.QVBoxLayout(ui_selector)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ui_selector_label = QtWidgets.QLabel(ui_selector)
        self.ui_selector_label.setObjectName("ui_selector_label")
        self.verticalLayout.addWidget(self.ui_selector_label)
        self.select_web_ui = QtWidgets.QPushButton(ui_selector)
        self.select_web_ui.setObjectName("select_web_ui")
        self.verticalLayout.addWidget(self.select_web_ui)
        self.select_sys_ui = QtWidgets.QPushButton(ui_selector)
        self.select_sys_ui.setObjectName("select_sys_ui")
        self.verticalLayout.addWidget(self.select_sys_ui)

        self.retranslateUi(ui_selector)
        QtCore.QMetaObject.connectSlotsByName(ui_selector)

    def retranslateUi(self, ui_selector):
        _translate = QtCore.QCoreApplication.translate
        ui_selector.setWindowTitle(_translate("ui_selector", "Form"))
        self.ui_selector_label.setText(_translate("ui_selector", "<html><head/><body><p><span style=\" font-size:12pt;\">Select web interface (http://localhost:8080) or the system GUI</span></p></body></html>"))
        self.select_web_ui.setText(_translate("ui_selector", "Web Interface"))
        self.select_sys_ui.setText(_translate("ui_selector", "System Interface"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui_selector = QtWidgets.QWidget()
    ui = Ui_ui_selector()
    ui.setupUi(ui_selector)
    ui_selector.show()
    sys.exit(app.exec_())

