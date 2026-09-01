"""
BCH Codec - GUI Application with Anime Theme
Supports numeric (0-4) and text input modes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QMessageBox, QFrame,
    QComboBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

from bch import BCHCode, text_to_symbols, symbols_to_text


ANIME_STYLE = """
QMainWindow { background-color: #1a0a1e; }
QWidget { background-color: #1a0a1e; color: #e8d0e8; }
QLabel { color: #ff9ed8; font-size: 13px; font-weight: bold; padding: 4px 0; background: transparent; }
QLabel#titleLabel { color: #ff69b4; font-size: 24px; font-weight: bold; padding: 12px; background: transparent; border-bottom: 2px solid #ff69b4; }
QLabel#subtitleLabel { color: #d490b0; font-size: 13px; padding: 0 0 8px 0; background: transparent; }
QLabel#infoLabel { color: #b080b4; font-size: 12px; padding: 2px 0; background: transparent; }
QTextEdit { background-color: #2d1130; color: #e8d0e8; border: 2px solid #5c2d5e; border-radius: 8px; padding: 10px; font-size: 14px; font-family: 'Consolas', 'Courier New', monospace; selection-background-color: #ff69b4; selection-color: #1a0a1e; }
QTextEdit:focus { border-color: #ff69b4; }
QPushButton { background-color: #ff69b4; color: #1a0a1e; border: none; border-radius: 20px; padding: 10px 30px; font-size: 14px; font-weight: bold; min-width: 140px; }
QPushButton:hover { background-color: #ff8dc7; }
QPushButton:pressed { background-color: #e05598; }
QPushButton:disabled { background-color: #4a2d4e; color: #7a5a7e; }
QPushButton#decodeBtn { background-color: #9b59b6; }
QPushButton#decodeBtn:hover { background-color: #af7ac5; }
QPushButton#decodeBtn:pressed { background-color: #7d3c98; }
QFrame { border: 1px solid #5c2d5e; border-radius: 10px; padding: 8px; background-color: #221025; }
QComboBox { background-color: #2d1130; color: #e8d0e8; border: 2px solid #5c2d5e; border-radius: 6px; padding: 6px 12px; font-size: 13px; min-width: 120px; }
QComboBox:hover { border-color: #ff69b4; }
QComboBox::drop-down { border: none; }
QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #ff69b4; margin-right: 8px; }
QComboBox QAbstractItemView { background-color: #2d1130; color: #e8d0e8; selection-background-color: #ff69b4; border: 1px solid #5c2d5e; }
QCheckBox { color: #d490b0; font-size: 13px; spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 2px solid #5c2d5e; background-color: #2d1130; }
QCheckBox::indicator:checked { background-color: #ff69b4; border-color: #ff69b4; }
QScrollBar:vertical { background: #2d1130; width: 10px; border-radius: 5px; }
QScrollBar::handle:vertical { background: #ff69b4; border-radius: 5px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""


class BCHApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bch = BCHCode(t=11, j0=1)
        self.last_codeword = []
        self.last_codeword_len = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("✦ BCH Codec — GF(5⁷) t=11 ✦")
        self.setMinimumSize(820, 720)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("✦ BCH Codec ✦")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Galois Field GF(5⁷)  ·  t = 11  ·  j₀ = 1")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Mode selector
        mode_row = QHBoxLayout()
        mode_row.setAlignment(Qt.AlignCenter)

        mode_label = QLabel("Input mode:")
        mode_row.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["🔢 Numeric (0–4)", "🔤 Text"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_change)
        mode_row.addWidget(self.mode_combo)

        self.show_symbols_check = QCheckBox("Show symbol representation")
        self.show_symbols_check.setChecked(True)
        self.show_symbols_check.setVisible(False)
        mode_row.addWidget(self.show_symbols_check)

        layout.addLayout(mode_row)

        # Input section
        in_frame = QFrame()
        in_layout = QVBoxLayout(in_frame)
        in_layout.setContentsMargins(10, 8, 10, 8)

        self.in_label = QLabel("✉ Message to encode (space-separated integers 0–4):")
        in_layout.addWidget(self.in_label)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("e.g. 1 2 3 0 4 1 2 3 0 4")
        self.input_text.setMaximumHeight(80)
        in_layout.addWidget(self.input_text)

        self.symbol_preview = QLabel("")
        self.symbol_preview.setObjectName("infoLabel")
        self.symbol_preview.setWordWrap(True)
        self.symbol_preview.setVisible(False)
        in_layout.addWidget(self.symbol_preview)

        encode_btn = QPushButton("✦ Encode ✦")
        encode_btn.clicked.connect(self.on_encode)
        in_layout.addWidget(encode_btn, alignment=Qt.AlignCenter)

        layout.addWidget(in_frame)

        # Encoded / Received section
        enc_frame = QFrame()
        enc_layout = QVBoxLayout(enc_frame)
        enc_layout.setContentsMargins(10, 8, 10, 8)

        enc_label = QLabel("🔐 Encoded codeword  (you may edit to inject errors):")
        enc_layout.addWidget(enc_label)

        self.encoded_text = QTextEdit()
        self.encoded_text.setPlaceholderText("Encoded data will appear here...")
        self.encoded_text.setMinimumHeight(100)
        enc_layout.addWidget(self.encoded_text)

        decode_btn = QPushButton("🔍 Decode")
        decode_btn.setObjectName("decodeBtn")
        decode_btn.clicked.connect(self.on_decode)
        enc_layout.addWidget(decode_btn, alignment=Qt.AlignCenter)

        layout.addWidget(enc_frame)

        # Output section
        out_frame = QFrame()
        out_layout = QVBoxLayout(out_frame)
        out_layout.setContentsMargins(10, 8, 10, 8)

        self.out_label = QLabel("📄 Decoded message:")
        out_layout.addWidget(self.out_label)

        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Decoded message will appear here...")
        self.output_text.setMaximumHeight(80)
        self.output_text.setReadOnly(True)
        out_layout.addWidget(self.output_text)

        layout.addWidget(out_frame)

        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #d490b0; font-size: 12px; padding: 4px;")
        layout.addWidget(self.status_label)

        # Stats
        stats_label = QLabel(
            f"n = {self.bch.n}  |  k = {self.bch.k}  |  deg(g) = {self.bch.deg_g}  |  t = {self.bch.t}"
        )
        stats_label.setAlignment(Qt.AlignCenter)
        stats_label.setStyleSheet("color: #7a5a7e; font-size: 11px; background: transparent;")
        layout.addWidget(stats_label)

        self._on_mode_change(0)

    def _on_mode_change(self, idx):
        is_text = idx == 1
        self.show_symbols_check.setVisible(is_text)
        if is_text:
            self.in_label.setText("✉ Message to encode (any text):")
            self.input_text.setPlaceholderText("Type your message here...")
            self.out_label.setText("📄 Decoded text:")
            self.symbol_preview.setVisible(True)
        else:
            self.in_label.setText("✉ Message to encode (space-separated integers 0–4):")
            self.input_text.setPlaceholderText("e.g. 1 2 3 0 4 1 2 3 0 4")
            self.out_label.setText("📄 Decoded message:")
            self.symbol_preview.setVisible(False)

    def _parse_input(self):
        """Parse input based on current mode. Returns (symbols, error_str)."""
        raw = self.input_text.toPlainText().strip()
        if not raw:
            return None, "Please enter a message to encode."

        if self.mode_combo.currentIndex() == 1:
            # Text mode
            symbols = text_to_symbols(raw)
            if not symbols:
                return None, "No symbols generated from text."
            return symbols, None
        else:
            # Numeric mode
            parts = raw.split()
            values = []
            for p in parts:
                try:
                    v = int(p)
                    if v < 0 or v > 4:
                        raise ValueError
                    values.append(v)
                except ValueError:
                    return None, f"Invalid symbol: '{p}' — must be integer 0–4"
            if not values:
                return None, "No symbols entered."
            return values, None

    def _format_symbols(self, syms):
        return " ".join(str(s) for s in syms)

    def _format_codeword(self, syms):
        return " ".join(str(s) for s in syms)

    def _decode_output(self, symbols):
        if self.mode_combo.currentIndex() == 1:
            return symbols_to_text(symbols)
        else:
            return self._format_symbols(symbols)

    def on_encode(self):
        symbols, err = self._parse_input()
        if err:
            QMessageBox.warning(self, "Input Error", err)
            return

        try:
            codeword = self.bch.encode(symbols)
            self.last_codeword = codeword
            self.last_codeword_len = len(codeword)
            self.encoded_text.setPlainText(self._format_codeword(codeword))

            show_syms = self.mode_combo.currentIndex() == 1 and self.show_symbols_check.isChecked()
            if show_syms:
                raw = self.input_text.toPlainText().strip()
                self.symbol_preview.setText(
                    f"📊 Symbols ({len(symbols)}): {self._format_symbols(symbols)}"
                )
            else:
                self.symbol_preview.clear()

            self.output_text.clear()
            self.status_label.setText(
                f"✓ Encoded {len(symbols)} symbols → {len(codeword)} symbols "
                f"({len(codeword) - len(symbols)} parity)"
            )
        except Exception as e:
            QMessageBox.critical(self, "Encoding Error", str(e))

    def on_decode(self):
        raw = self.encoded_text.toPlainText().strip()
        if not raw:
            QMessageBox.warning(self, "Input Error", "No encoded data to decode.")
            return

        parts = raw.split()
        symbols = []
        for p in parts:
            try:
                v = int(p)
                if v < 0 or v > 4:
                    raise ValueError
                symbols.append(v)
            except ValueError:
                QMessageBox.warning(
                    self, "Input Error",
                    f"Invalid symbol: '{p}' — codeword must be integers 0–4"
                )
                return

        if not symbols:
            QMessageBox.warning(self, "Input Error", "No symbols to decode.")
            return

        if self.last_codeword_len > 0 and len(symbols) != self.last_codeword_len:
            self.output_text.clear()
            self.status_label.setText(
                f"✗ Length mismatch: expected {self.last_codeword_len} symbols, "
                f"got {len(symbols)}. The codeword length must not be changed."
            )
            return

        try:
            decoded, success, info = self.bch.decode(symbols)
            output = self._decode_output(decoded) if decoded else ""
            if success:
                self.output_text.setPlainText(output)
                self.status_label.setText(f"✓ {info}")
            else:
                self.output_text.setPlainText(output if output else "")
                self.status_label.setText(f"✗ {info}")
        except Exception as e:
            QMessageBox.critical(self, "Decoding Error", str(e))


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(ANIME_STYLE)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1a0a1e"))
    palette.setColor(QPalette.WindowText, QColor("#e8d0e8"))
    palette.setColor(QPalette.Base, QColor("#2d1130"))
    palette.setColor(QPalette.Text, QColor("#e8d0e8"))
    palette.setColor(QPalette.Highlight, QColor("#ff69b4"))
    palette.setColor(QPalette.HighlightedText, QColor("#1a0a1e"))
    app.setPalette(palette)

    window = BCHApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
