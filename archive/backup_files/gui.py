"""
gui.py — PySide6 Desktop GUI application for DesktopPilot AI (Phase 7).

Run locally:
  python gui.py
"""
from __future__ import annotations

import asyncio
import sys
import uuid
from typing import Any

try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False

try:
    from agents.voice_agent import speak_text_async
except ImportError:
    def speak_text_async(text: str): pass

try:
    from PySide6.QtCore import QThread, Signal, Qt
    from PySide6.QtGui import QFont, QColor, QPalette
    from PySide6.QtWidgets import (
        QApplication,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QScrollArea,
        QSplitter,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


if PYSIDE6_AVAILABLE:

    class SpeechWorker(QThread):
        """Worker thread to record audio and perform speech-to-text."""
        finished = Signal(str)
        error = Signal(str)

        def run(self):
            if not SPEECH_AVAILABLE:
                self.error.emit("SpeechRecognition is not installed.")
                return

            recognizer = sr.Recognizer()
            recognizer.pause_threshold = 2.5  # Wait 2.5 seconds of silence before cutting off
            recognizer.dynamic_energy_threshold = True
            
            try:
                with sr.Microphone() as source:
                    # Adjust for ambient noise and record
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)
                
                text = recognizer.recognize_google(audio)
                self.finished.emit(text)
            except sr.WaitTimeoutError:
                self.error.emit("No speech detected (timeout).")
            except sr.UnknownValueError:
                self.error.emit("Could not understand audio.")
            except sr.RequestError as e:
                self.error.emit(f"Could not request results; {e}")
            except Exception as e:
                self.error.emit(f"Microphone error: {e}")

    class GraphWorker(QThread):
        """Worker thread to run LangGraph state graph asynchronously without blocking UI."""
        finished = Signal(dict)
        error = Signal(str)

        def __init__(self, user_input: str, session_id: str, messages: list[dict[str, str]], task_type: str | None = None, current_task_info: dict | None = None):
            super().__init__()
            self.user_input = user_input
            self.session_id = session_id
            self.messages = messages
            self.task_type = task_type
            self.current_task_info = current_task_info or {}

        def run(self):
            from graph.workflow import create_graph
            from graph.state import AgentState

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            graph = create_graph()
            state: AgentState = {
                "messages": self.messages,
                "session_id": self.session_id,
                "user_input": self.user_input,
                "task_type": self.task_type,
                "current_task_info": self.current_task_info,
                "requirements_complete": False,
                "clarifying_question": None,
                "plan": None,
                "current_step": 0,
                "last_execution_result": None,
                "validation_result": None,
                "replan_reason": None,
                "model_backend": "unknown",
                "capabilities": None,
                "memory_context": None,
                "final_response": None,
                "error": None,
                "execution_trace": [],
            }

            try:
                res = loop.run_until_complete(graph.ainvoke(state))
                self.finished.emit(res)
            except Exception as e:
                self.error.emit(str(e))
            finally:
                loop.close()


    class DesktopPilotWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.session_id = str(uuid.uuid4())
            self.messages: list[dict[str, str]] = []
            self.current_task_type = None
            self.current_task_info = {}
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle("DesktopPilot AI — Desktop Automation Engine")
            self.resize(1100, 750)

            # Dark theme styling
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #121417;
                    color: #E2E8F0;
                }
                QWidget {
                    background-color: #121417;
                    color: #E2E8F0;
                    font-family: 'Segoe UI', Roboto, sans-serif;
                }
                QFrame#chatContainer {
                    background-color: #1A1D24;
                    border-radius: 12px;
                    border: 1px solid #2D3748;
                }
                QFrame#sidebar {
                    background-color: #161920;
                    border-radius: 12px;
                    border: 1px solid #2D3748;
                }
                QLineEdit {
                    background-color: #262B36;
                    border: 1px solid #3A4254;
                    border-radius: 8px;
                    padding: 10px 14px;
                    color: #F7FAFC;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #4FD1C5;
                }
                QPushButton {
                    background-color: #3182CE;
                    color: white;
                    border-radius: 8px;
                    padding: 10px 18px;
                    font-weight: bold;
                    font-size: 14px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2B6CB0;
                }
                QPushButton#resetBtn {
                    background-color: #4A5568;
                }
                QPushButton#resetBtn:hover {
                    background-color: #718096;
                }
                QPushButton#voiceBtn {
                    background-color: #DD6B20;
                }
                QPushButton#voiceBtn:hover {
                    background-color: #C05621;
                }
                QTextEdit {
                    background-color: #1A1D24;
                    border: none;
                    color: #E2E8F0;
                    font-size: 14px;
                }
            """)

            # Main Layout Splitter
            splitter = QSplitter(Qt.Horizontal)

            # Left Pane — Chat
            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)

            header_label = QLabel("🤖 DesktopPilot AI Assistant")
            header_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
            header_label.setStyleSheet("color: #4FD1C5; padding: 6px 0;")
            left_layout.addWidget(header_label)

            self.chat_display = QTextEdit()
            self.chat_display.setReadOnly(True)
            left_layout.addWidget(self.chat_display)

            # Input Controls
            input_layout = QHBoxLayout()
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText("Type your instruction (e.g. 'Create an Excel report for sales')...")
            self.input_field.returnPressed.connect(self.send_message)
            input_layout.addWidget(self.input_field)

            self.send_btn = QPushButton("Send")
            self.send_btn.clicked.connect(self.send_message)
            input_layout.addWidget(self.send_btn)

            self.voice_btn = QPushButton("🎙️ Voice")
            self.voice_btn.setObjectName("voiceBtn")
            self.voice_btn.clicked.connect(self.start_voice_recording)
            input_layout.addWidget(self.voice_btn)

            self.reset_btn = QPushButton("Reset")
            self.reset_btn.setObjectName("resetBtn")
            self.reset_btn.clicked.connect(self.reset_session)
            input_layout.addWidget(self.reset_btn)

            left_layout.addLayout(input_layout)
            splitter.addWidget(left_widget)

            # Right Pane — Execution Trace & Plan
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)

            trace_title = QLabel("⚡ Execution Trace & Plan")
            trace_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
            trace_title.setStyleSheet("color: #F6AD55; padding: 6px 0;")
            right_layout.addWidget(trace_title)

            self.trace_display = QTextEdit()
            self.trace_display.setReadOnly(True)
            right_layout.addWidget(self.trace_display)

            splitter.addWidget(right_widget)
            splitter.setSizes([650, 450])

            self.setCentralWidget(splitter)
            self.append_system_message("DesktopPilot AI GUI Ready. Enter an instruction to begin.")

        def append_system_message(self, msg: str):
            self.chat_display.append(f"<div style='color: #A0AEC0; margin: 4px 0;'><b>[System]:</b> {msg}</div>")

        def append_user_message(self, msg: str):
            self.chat_display.append(f"<div style='color: #63B3ED; margin: 6px 0;'><b>You:</b> {msg}</div>")

        def append_assistant_message(self, msg: str):
            self.chat_display.append(f"<div style='color: #68D391; margin: 6px 0;'><b>Assistant:</b> {msg}</div>")

        def reset_session(self):
            self.session_id = str(uuid.uuid4())
            self.messages = []
            self.current_task_type = None
            self.current_task_info = {}
            self.chat_display.clear()
            self.trace_display.clear()
            self.append_system_message("Session reset.")

        def start_voice_recording(self):
            if not SPEECH_AVAILABLE:
                self.append_system_message("Voice features require SpeechRecognition. Run: pip install -r requirements-gui.txt")
                return
            
            self.voice_btn.setEnabled(False)
            self.voice_btn.setText("Listening...")
            self.append_system_message("Listening for your voice... speak now!")
            
            self.speech_worker = SpeechWorker()
            self.speech_worker.finished.connect(self.on_speech_finished)
            self.speech_worker.error.connect(self.on_speech_error)
            self.speech_worker.start()

        def on_speech_finished(self, text: str):
            self.voice_btn.setEnabled(True)
            self.voice_btn.setText("🎙️ Voice")
            self.input_field.setText(text)
            self.send_message()

        def on_speech_error(self, err: str):
            self.voice_btn.setEnabled(True)
            self.voice_btn.setText("🎙️ Voice")
            self.append_system_message(f"Voice Error: {err}")

        def send_message(self):
            text = self.input_field.text().strip()
            if not text:
                return

            self.input_field.clear()
            self.append_user_message(text)
            self.send_btn.setEnabled(False)
            
            self.messages.append({"role": "user", "content": text})

            self.worker = GraphWorker(text, self.session_id, self.messages, self.current_task_type, self.current_task_info)
            self.worker.finished.connect(self.on_graph_finished)
            self.worker.error.connect(self.on_graph_error)
            self.worker.start()

        def on_graph_finished(self, result: dict):
            self.send_btn.setEnabled(True)
            backend = result.get("model_backend", "unknown").upper()
            trace = result.get("execution_trace", [])

            if result.get("task_type"):
                self.current_task_type = result["task_type"]
            
            if "current_task_info" in result:
                self.current_task_info = result["current_task_info"]
                
            # Update trace display
            self.trace_display.clear()
            self.trace_display.append(f"Backend Mode: {backend}\n" + "─" * 40 + "\n")
            for t in trace:
                status_icon = "✅" if t.get("status") == "success" else "❌" if t.get("status") == "error" else "ℹ️"
                self.trace_display.append(f"{status_icon} [{t.get('agent')}] {t.get('message')}\n")

            plan = result.get("plan")
            if plan:
                self.trace_display.append("\n📋 Generated Execution Plan:\n")
                for s in plan:
                    self.trace_display.append(f"  Step {s.get('step_id')}: [{s.get('agent')}] {s.get('action')}")

            # Respond in chat window
            if result.get("clarifying_question"):
                q = result["clarifying_question"]
                self.append_assistant_message(f"<b>(Needs Clarification):</b> {q}")
                self.messages.append({"role": "assistant", "content": q})
                speak_text_async(q)
            elif result.get("final_response"):
                resp = result["final_response"]
                self.append_assistant_message(resp)
                self.messages.append({"role": "assistant", "content": resp})
                speak_text_async(resp)
            elif result.get("error"):
                self.append_system_message(f"Error: {result['error']}")

        def on_graph_error(self, err_msg: str):
            self.send_btn.setEnabled(True)
            self.append_system_message(f"Execution Error: {err_msg}")


def main():
    if not PYSIDE6_AVAILABLE:
        print("PySide6 is not installed. To run the Desktop GUI, install PySide6:")
        print("  pip install -r requirements-gui.txt")
        print("\nAlternatively, you can run the CLI interface:")
        print("  python main.py")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = DesktopPilotWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
