import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QComboBox, QApplication, QLabel, QGridLayout, QDoubleSpinBox, QMessageBox
from forex_python.converter import convert as convert_currency, RatesNotAvailableError
import json
from typing import TypedDict
from PyQt6.QtGui import QFont


class CurrencyData(TypedDict):
    cc: str
    symbol: str
    name: str


with open('currencies.json') as f:
    data: list[CurrencyData] = json.load(f)

font = QFont('Arial', 12)


class CurrencyComboBox(QComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super(CurrencyComboBox, self).__init__(parent)
        items = [f'{currency["cc"]} ({currency["name"]})' for currency in data]
        self.addItems(items)
        self.setFont(font)
        self.setFixedWidth(300)


class CurrencySpinbox(QDoubleSpinBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setRange(0, float('inf'))
        self.setFont(font)



class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setWindowTitle('Currency Converter')

        layout = QGridLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        label = QLabel('Convert:', w)
        label.setFont(font)

        layout.addWidget(label, 0, 0)

        self.currency_from_amount = CurrencySpinbox()
        self.currency_from_amount.valueChanged.connect(self.on_change)

        layout.addWidget(self.currency_from_amount, 0, 1)

        self.currency_from = CurrencyComboBox()
        self.currency_to = CurrencyComboBox()

        self.currency_to.currentTextChanged.connect(self.on_change)
        self.currency_from.currentTextChanged.connect(self.on_change)

        layout.addWidget(self.currency_from, 0, 2)
        layout.addWidget(self.currency_to, 1, 2)

        label2 = QLabel('To:')
        label2.setFont(font)
        layout.addWidget(label2, 1, 0)

        self.result_label = QLabel()
        self.result_label.setFont(font)
        layout.addWidget(self.result_label, 2, 0, 3, 1)

        self.setGeometry(30, 30, 700, 200)
    
    def on_change(self):
        currency_from = self.currency_from.currentText()[:3]
        currency_from_amount = self.currency_from_amount.value()
        currency_to = self.currency_to.currentText()[:3]

        try:
            converted = convert_currency(currency_from, currency_to, currency_from_amount)
        except RatesNotAvailableError:
            choice = QMessageBox.critical(
                None,
                'Error',
                'It seems that you do not have an internet connection',
                QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel
            )
            if choice == QMessageBox.StandardButton.Retry:
                self.on_change()
        else:
            self.result_label.setText(f'{currency_from_amount} {currency_from} = {converted} {currency_to}')


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == '__main__':
    main()
