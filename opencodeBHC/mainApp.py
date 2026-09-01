import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QTableWidget,
    QTableWidgetItem, QGroupBox, QGridLayout, QHeaderView,
    QMessageBox, QStatusBar, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor

from BCH import BCHCode


class BCHApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bch = BCHCode()
        self.gf = self.bch.gf

        self.original_codeword: list[int] = []
        self.current_codeword: list[int] = []
        self.injected_errors: list[tuple[int, int, int]] = []
        self.message_base5: list[int] = []

        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("BCH Codec — GF(5⁷), t=11, j₀=1")
        self.setMinimumSize(920, 720)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(5)

        params = QLabel(
            f"<b>n = {self.bch.n}</b>  |  "
            f"<b>k = {self.bch.k}</b>  |  "
            f"<b>t = {self.bch.t}</b>  |  "
            f"<b>deg(g) = {len(self.bch.g) - 1}</b>  |  "
            f"<b>GF(5⁷)</b>  |  "
            f"<b>primitive: x⁷ + 3x + 3</b>"
        )
        params.setAlignment(Qt.AlignCenter)
        layout.addWidget(params)

        msg_group = QGroupBox("Message Input")
        msg_layout = QVBoxLayout(msg_group)
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText(
            "Digits 0-4 (space-separated) or any text (ASCII code mod 5)"
        )
        msg_layout.addWidget(self.input_text)
        btn_row = QHBoxLayout()
        self.btn_encode = QPushButton("Encode")
        self.btn_encode.clicked.connect(self._on_encode)
        btn_row.addWidget(self.btn_encode)
        btn_row.addStretch()
        msg_layout.addLayout(btn_row)
        layout.addWidget(msg_group)

        self.label_base5 = QLabel("Base-5 message: —")
        self.label_base5.setWordWrap(True)
        layout.addWidget(self.label_base5)

        cw_group = QGroupBox("Codeword")
        cw_layout = QVBoxLayout(cw_group)
        self.codeword_display = QTextEdit()
        self.codeword_display.setReadOnly(True)
        mono = QFont("Courier New", 8)
        mono.setStyleHint(QFont.Monospace)
        self.codeword_display.setFont(mono)
        cw_layout.addWidget(self.codeword_display)
        layout.addWidget(cw_group)

        inject_group = QGroupBox("Error Injection")
        inject_grid = QGridLayout(inject_group)
        inject_grid.addWidget(QLabel("Position:"), 0, 0)
        self.spin_pos = QSpinBox()
        self.spin_pos.setRange(0, self.bch.n - 1)
        self.spin_pos.setToolTip(f"Codeword position (0 … {self.bch.n - 1})")
        self.spin_pos.setSingleStep(1)
        inject_grid.addWidget(self.spin_pos, 0, 1)
        inject_grid.addWidget(QLabel("New value:"), 0, 2)
        self.combo_val = QComboBox()
        self.combo_val.addItems([str(i) for i in range(5)])
        inject_grid.addWidget(self.combo_val, 0, 3)
        self.btn_inject = QPushButton("Inject Error")
        self.btn_inject.clicked.connect(self._on_inject)
        inject_grid.addWidget(self.btn_inject, 0, 4)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self._on_reset)
        inject_grid.addWidget(self.btn_reset, 0, 5)
        self.inject_table = QTableWidget(0, 3)
        self.inject_table.setHorizontalHeaderLabels(["Position", "Original", "New"])
        self.inject_table.horizontalHeader().setStretchLastSection(True)
        self.inject_table.setMaximumHeight(100)
        inject_grid.addWidget(self.inject_table, 1, 0, 1, 6)
        layout.addWidget(inject_group)

        self.btn_decode = QPushButton("Decode")
        self.btn_decode.clicked.connect(self._on_decode)
        self.btn_decode.setEnabled(False)
        layout.addWidget(self.btn_decode)

        result_group = QGroupBox("Decoding Results")
        result_layout = QVBoxLayout(result_group)
        self.decoded_label = QLabel("Decoded message: —")
        self.decoded_label.setWordWrap(True)
        result_layout.addWidget(self.decoded_label)
        self.error_table = QTableWidget(0, 3)
        self.error_table.setHorizontalHeaderLabels(["Position", "Error Value", "Corrected"])
        self.error_table.horizontalHeader().setStretchLastSection(True)
        result_layout.addWidget(self.error_table)
        layout.addWidget(result_group)

        self.statusBar().showMessage("Ready")

    def _parse_input(self) -> list[int] | None:
        raw = self.input_text.text().strip()
        if not raw:
            QMessageBox.warning(self, "Input Error", "Please enter a message.")
            return None

        tokens = raw.split()
        if tokens and all(t.isdigit() for t in tokens):
            digits = [int(t) % 5 for t in tokens]
            if any(int(t) >= 5 for t in tokens):
                QMessageBox.information(self, "Info", "Values >= 5 reduced mod 5.")
        else:
            digits = [ord(ch) % 5 for ch in raw]

        if len(digits) > self.bch.k:
            QMessageBox.warning(
                self, "Message Too Long",
                f"Message produces {len(digits)} symbols, max is {self.bch.k}."
            )
            return None
        return digits

    def _update_codeword_display(self):
        cw = self.current_codeword
        n = len(cw)
        chunk = 200
        lines = []
        for start in range(0, n, chunk):
            end = min(start + chunk, n)
            seg = "".join(str(d) for d in cw[start:end])
            lines.append(f"[{start:>5}–{end-1:>5}]  {seg}")
        self.codeword_display.setPlainText("\n".join(lines))
        self.codeword_display.moveCursor(QTextCursor.Start)

    def _on_encode(self):
        digits = self._parse_input()
        if digits is None:
            return

        self.message_base5 = digits
        self.label_base5.setText(
            f"Base-5 message ({len(digits)} symbols): "
            + " ".join(str(d) for d in digits)
        )

        self.original_codeword = self.bch.encode(digits)
        self.current_codeword = list(self.original_codeword)
        self.injected_errors = []
        self.inject_table.setRowCount(0)
        self.error_table.setRowCount(0)
        self.decoded_label.setText("Decoded message: —")

        self._update_codeword_display()
        self.btn_decode.setEnabled(True)
        self.statusBar().showMessage(
            f"Encoded {len(digits)} symbols → codeword ({len(self.original_codeword)} symbols)"
        )

    def _on_inject(self):
        if not self.current_codeword:
            return
        pos = self.spin_pos.value()
        val = int(self.combo_val.currentText())
        orig = self.original_codeword[pos]
        self.current_codeword[pos] = val

        self.injected_errors.append((pos, orig, val))
        r = self.inject_table.rowCount()
        self.inject_table.insertRow(r)
        self.inject_table.setItem(r, 0, QTableWidgetItem(str(pos)))
        self.inject_table.setItem(r, 1, QTableWidgetItem(str(orig)))
        self.inject_table.setItem(r, 2, QTableWidgetItem(str(val)))
        self._update_codeword_display()
        self.statusBar().showMessage(f"Injected error at pos {pos}: {orig} → {val}")

    def _on_reset(self):
        if not self.original_codeword:
            return
        self.current_codeword = list(self.original_codeword)
        self.injected_errors = []
        self.inject_table.setRowCount(0)
        self.error_table.setRowCount(0)
        self.decoded_label.setText("Decoded message: —")
        self._update_codeword_display()
        self.statusBar().showMessage("Codeword reset")

    def _on_decode(self):
        if not self.current_codeword:
            return
        self.statusBar().showMessage("Decoding (Chien search over 78k elements)…")
        QApplication.processEvents()

        decoded, err_positions, err_values = self.bch.decode(self.current_codeword)

        n_msg = len(self.message_base5)
        msg_str = " ".join(str(d) for d in decoded[:n_msg])
        self.decoded_label.setText(f"Decoded message ({n_msg} symbols): {msg_str}")

        self.error_table.setRowCount(0)
        if err_positions:
            for pos, val in zip(err_positions, err_values):
                r = self.error_table.rowCount()
                self.error_table.insertRow(r)
                self.error_table.setItem(r, 0, QTableWidgetItem(str(pos)))
                self.error_table.setItem(r, 1, QTableWidgetItem(str(val)))
                corrected = self.gf.sub(self.current_codeword[pos], val)
                self.error_table.setItem(r, 2, QTableWidgetItem(str(corrected)))
            status = f"{len(err_positions)} error(s) detected and corrected"
        else:
            status = "No errors detected"

        ok = decoded[:n_msg] == self.message_base5
        icon = "✅" if ok else "❌"
        self.statusBar().showMessage(f"{status}  {icon}")


def main():
    app = QApplication(sys.argv)
    window = BCHApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
