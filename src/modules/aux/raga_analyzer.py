"""
Raga Analyzer Component for Metadata Tab
"""

from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QLabel, QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWidget

from src.services.ai_service import AIService


class RagaAnalysisWorker(QThread):
    """Worker thread for running raga analysis without blocking UI"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, ai_service: AIService, file_path: str):
        super().__init__()
        self.ai_service = ai_service
        self.file_path = file_path

    def run(self) -> None:
        try:
            result = self.ai_service.analyze_raga(self.file_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class RagaAnalyzerWidget(QWidget):
    """Widget for triggering and displaying Raga analysis results"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ai_service = AIService()
        self.current_file: Optional[str] = None
        self.worker: Optional[RagaAnalysisWorker] = None
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.analyze_btn = QPushButton("Analyze Raga")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)  # Disabled until a file is selected
        layout.addWidget(self.analyze_btn)

        # Results labels
        self.result_labels: List[QLabel] = []
        self.progress_bars: List[QProgressBar] = []

        for _ in range(3):
            lbl = QLabel("")
            lbl.setVisible(False)
            layout.addWidget(lbl)
            self.result_labels.append(lbl)

            pb = QProgressBar()
            pb.setRange(0, 100)
            pb.setVisible(False)
            pb.setTextVisible(False)
            pb.setFixedHeight(4)
            layout.addWidget(pb)
            self.progress_bars.append(pb)

    def set_file(self, file_path: Optional[str]) -> None:
        self.current_file = file_path
        self.analyze_btn.setEnabled(file_path is not None)
        self.clear_results()

    def clear_results(self) -> None:
        for lbl in self.result_labels:
            lbl.setVisible(False)
            lbl.setText("")
        for pb in self.progress_bars:
            pb.setVisible(False)
            pb.setValue(0)

    def start_analysis(self) -> None:
        if not self.current_file:
            return

        health = self.ai_service.check_health()
        if not health.get("enabled", False):
            QMessageBox.warning(self, "AI Disabled", "AI Analysis is disabled in settings.")
            return

        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("Analyzing...")
        self.clear_results()

        self.worker = RagaAnalysisWorker(self.ai_service, self.current_file)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_analysis_finished(self, result: Dict[str, Any]) -> None:
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("Analyze Raga")

        top_ragas = result.get("ragas", [])

        if not top_ragas:
            self.result_labels[0].setText("No raga detected.")
            self.result_labels[0].setVisible(True)
            return

        for i, (raga_name, confidence) in enumerate(top_ragas[:3]):
            if i < len(self.result_labels):
                pct = int(confidence * 100)
                self.result_labels[i].setText(f"{raga_name}: {pct}%")
                self.result_labels[i].setVisible(True)

                self.progress_bars[i].setValue(pct)
                self.progress_bars[i].setVisible(True)

    def on_analysis_error(self, error_msg: str) -> None:
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("Analyze Raga")
        QMessageBox.critical(self, "Analysis Error", f"Failed to analyze raga: {error_msg}")
