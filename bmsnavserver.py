import sys
import os
import json
from os.path import abspath
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import TCPServer
from enum import StrEnum
from datetime import datetime
from PIL import Image
from PyQt5.QtCore import QFileSystemWatcher, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
  QApplication,
  QHBoxLayout,
  QVBoxLayout,
  QComboBox,
  QLabel,
  QMainWindow,
  QPlainTextEdit,
  QPushButton,
  QScrollBar,
  QWidget
)

# The main entry point for the BMSNavServer app.
#
# Author: Sean Eidemiller (seidemiller@gmail.com)

# ======== Global ========

class LogLevel(StrEnum):
  INFO = 'INFO'
  WARN = 'WARN'
  ERROR = 'ERROR'

DDS_DIR = 'dds'
SERVER_ROOT = 'serve'
DEFAULT_SERVER_PORT = 2676
DEFAULT_THEATERS = ["Korea", "Balkans", "Israel"]

def console_get_message(message, level = LogLevel.INFO):
  now = datetime.now()
  time = now.strftime('%H:%M:%S')
  return f'[{level} {time}] {message}'

# ======== Classes ========

class HTTPHandler(SimpleHTTPRequestHandler):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, directory=SERVER_ROOT, **kwargs)

  def log_message(self, format, *args):
    pass

class ServerDaemon(QThread):
  error = pyqtSignal(Exception)
  initialized = pyqtSignal()

  def __init__(self, port):
    super(ServerDaemon, self).__init__()
    self.port = port

  def run(self):
    try:
      with TCPServer(("", self.port), HTTPHandler) as self._server:
        self.initialized.emit()
        self._server.serve_forever()
    except Exception as err:
      self.error.emit(err)

  def stop(self):
    self._server.shutdown()
    self._server.socket.close()
    self.wait()

class DDSConverter(QThread):
  error = pyqtSignal(Exception)

  def run(self):
    try:
      for i in range(7982, 7998):
        in_path = os.path.join(DDS_DIR, f'{i}.dds')
        index = (i - 7982) + 1

        if index < 10:
          index = f'0{str(index)}' 

        out_left_path = os.path.join(SERVER_ROOT, f'l{index}.png')
        out_right_path = os.path.join(SERVER_ROOT, f'r{index}.png')

        with Image.open(in_path) as img:
          left_dims = (0 ,0, int(img.size[0] / 2), img.size[1])
          right_dims = int(img.size[0] / 2), 0, img.size[0], img.size[1]
          self.write_png(img, out_left_path, left_dims)
          self.write_png(img, out_right_path, right_dims)
    except Exception as err:
      self.error.emit(err)

  def stop(self):
    self.wait()

  def write_png(self, img, out_path, dims):
    cropped = img.crop(dims)
    cropped.save(out_path, 'png')

class DDSMonitor():
  def __init__(self, on_change):
    kneeboards = []
    for i in range(7982, 7998):
      kneeboards.append(os.path.join(DDS_DIR, f'{i}.dds'))

    self.fs_watcher = QFileSystemWatcher(kneeboards)    
    self.fs_watcher.fileChanged.connect(on_change)

class Window(QMainWindow):
  def __init__(self):
    super(Window, self).__init__()

    self.console_messages = console_get_message('Welcome to BMSNavServer! Initializing...')

    self.setWindowTitle("BMSNavServer")
    self.setGeometry(0, 0, 800, 400)

    central_widget = QWidget()
    central_widget.setObjectName('central')

    central_layout = QVBoxLayout()
    central_widget.setLayout(central_layout)

    controls = QWidget()
    controls.setObjectName('controls')

    controls_layout = QHBoxLayout()
    controls.setLayout(controls_layout)

    theater_selection = QWidget()
    theater_selection.setObjectName('theater_selection')

    theater_selection_layout = QHBoxLayout()
    theater_selection.setLayout(theater_selection_layout)

    theater_label = QLabel()
    theater_label.setObjectName('theater_label')
    theater_label.setText('Theater:')

    theater_combobox = QComboBox()
    theater_combobox.currentTextChanged.connect(self._on_theater_change);

    theater_selection_layout.addWidget(theater_label)
    theater_selection_layout.addStretch(1)
    theater_selection_layout.addWidget(theater_combobox)
    theater_selection_layout.setContentsMargins(4, 0, 0, 0)

    clear_button = QPushButton()
    clear_button.setObjectName('clear_button')
    clear_button.setText('Clear Console')
    clear_button.clicked.connect(self.console_clear)

    controls_layout.addWidget(theater_selection)
    controls_layout.addStretch(1)
    controls_layout.addWidget(clear_button)
    controls_layout.setContentsMargins(0, 0, 0, 0)

    self.console_output = QPlainTextEdit()
    self.console_output.setObjectName('console_output')
    self.console_output.setReadOnly(True)
    self.console_output.setPlainText(self.console_messages)
    self.console_output.setFont(QFont('Courier New'))

    self.console_output_scrollbar = QScrollBar()
    self.console_output.setVerticalScrollBar(self.console_output_scrollbar)

    central_layout.addWidget(controls)
    central_layout.addWidget(self.console_output)

    self.setCentralWidget(central_widget)

    self.port = DEFAULT_SERVER_PORT
    self.theaters = DEFAULT_THEATERS

    try:
      config_file = open('config.json', 'r')
      self.config = json.loads(config_file.read())

      try:
        port = self.config['port']

        if port > 1024 and port <= 65535:
          self.port = port
        else:
          self.console_append('Invalid port in config file; reverting to default.', LogLevel.WARN)
      except Exception as port_err:
        self.console_append('Error reading port from config file; reverting to default.', LogLevel.WARN)

      try:
        theaters = self.config['theaters']
        theater_names = [] 

        for t in theaters:
          theater_names.append(t['name'])

        self.theaters = theater_names

      except Exception as theater_err:
        self.console_append('Error reading theaters from config file; reverting to default.', LogLevel.WARN)

      config_file.close()

    except Exception as err:
      self.console_append('Error reading config file: ' + str(err), LogLevel.WARN)

    theater_combobox.addItems(self.theaters)     

    self.monitor = DDSMonitor(self._on_dds_change)
    self.console_append('Monitoring kneeboard DDS files for changes.');

    self.console_append('Generating kneeboard images...');
    self.converter = DDSConverter()
    self.converter.error.connect(self._on_conversion_error)
    self.converter.finished.connect(self._on_conversion_finished)
    self.converter.start()

    self.server = ServerDaemon(self.port)
    self.server.error.connect(self._on_server_error)
    self.server.initialized.connect(self._on_server_initialized)
    self.server.start()

  def console_append(self, message, level = LogLevel.INFO):
    console_message = console_get_message(message, level)
    self.console_messages += f'\n{console_message}'
    self.console_output.setPlainText(self.console_messages)
    self.console_output_scrollbar.setValue(self.console_output_scrollbar.maximum())

  def console_clear(self):
    message = console_get_message('Console cleared.') 
    self.console_messages = message;
    self.console_output.setPlainText(self.console_messages)
    self.console_output_scrollbar.setValue(self.console_output_scrollbar.maximum()) 

  def _on_theater_change(self, theater):
    self.config['selectedTheater'] = theater

    try:
      with open('config.json', 'w') as config_file:
        config_file.write(json.dumps(self.config, indent=2)) 
        config_file.close()
    except Exception as err:
      self.console_append('Error writing selected theater to config file: ' + str(err))

  def _on_dds_change(self):
    self.console_append('Kneeboard DDS file(s) changed; regenerating images...') 
    self.converter = DDSConverter()
    self.converter.start()
    self.converter.finished.connect(self._on_conversion_finished)

  def _on_server_initialized(self):
    self.console_append(f'Server started on port {self.port}: waiting for requests.')
    self.console_append('Initialization complete.')

  def _on_server_error(self, err):
    self.console_append('Error initializing server: ' + str(err), LogLevel.ERROR)

  def _on_conversion_finished(self):
    self.console_append('Kneeboard images generated.');

  def _on_conversion_error(self, err):
    self.console_append('Error generating kneeboard images: ' + str(err), LogLevel.ERROR)

# ======== Main ========

if not os.path.exists(SERVER_ROOT):
  os.makedirs(SERVER_ROOT)

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
