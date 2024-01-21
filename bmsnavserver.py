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

def get_registry_key(version):
  return rf'SOFTWARE\WOW6432Node\Benchmark Sims\Falcon BMS {version}'

class LogLevel(StrEnum):
  INFO = 'INFO'
  WARN = 'WARN'
  ERROR = 'ERROR'

DDS_DIR = 'dds'
SERVER_ROOT = 'serve'

DEFAULT_BMS_VERSION = '4.37'
DEFAULT_REGISTRY_KEY = get_registry_key(DEFAULT_BMS_VERSION)
DEFAULT_SERVER_PORT = 2676
DEFAULT_THEATERS = [
  {
    "name": "Korea"
  },
  {
    "name": "Balkans"
  },
  {
    "name": "Israel"
  }
]
DEFAULT_SELECTED_THEATER = DEFAULT_THEATERS[0]['name']

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

class Server(QThread):
  started = pyqtSignal()
  error = pyqtSignal(Exception)

  def __init__(self, port):
    super(Server, self).__init__()
    self.port = port

  def run(self):
    try:
      with TCPServer(("", self.port), HTTPHandler) as self._server:
        self.started.emit()
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
    self.theater_names = list(map(lambda t: t['name'], DEFAULT_THEATERS))
    self.selected_theater = DEFAULT_SELECTED_THEATER
    self.bms_version = DEFAULT_BMS_VERSION
    self.registry_key = DEFAULT_REGISTRY_KEY

    config_file = None
    selected_theater = DEFAULT_SELECTED_THEATER

    try:
      config_file = open('config.json', 'r')
      config = json.loads(config_file.read())

      try:
        bms_home = config['bmsHome']

        if bms_home:
          if os.path.exists(bms_home):
            self.bms_home = bms_home
          else:
            self.console_append('BMS home directory specified in config file does not exist; reverting to registry entry.', LogLevel.WARN)
      except Exception as bms_home_err:
        pass

      try:
        bms_version = config['bmsVersion']

        if version:
          self.bms_version = bms_version
          self.registry_key = get_registry_key(bms_version)
      except Exception as bms_version_err:
        pass

      try:
        port = config['port']

        if port > 1024 and port <= 65535:
          self.port = port
        else:
          self.console_append('Invalid port in config file; reverting to default.', LogLevel.WARN)
      except Exception as port_err:
        pass

      try:
        selected_theater = config['selectedTheater']

        if selected_theater:
          self.selected_theater = selected_theater
      except Exception as selected_theater_err:
        pass

      try:
        theaters = config['theaters']
        theater_names = [] 

        if theaters:
          theater_names = list(map(lambda t: t['name'], theaters))

        if theater_names:
          self.theater_names = theater_names
        else:
          self.console_append('Empty theater list in config file; reverting to default.', LogLevel.INFO)

        if selected_theater and selected_theater in theater_names:
          self.selected_theater = selected_theater 
        else:
          self.console_append('Specified selected theater not found; reverting to default.', LogLevel.WARN)
          self.selected_theater = self.theater_names[0]

      except Exception as theater_err:
        pass

    except Exception as err:
      self.console_append('Unable to read config file; using default values.', LogLevel.INFO)

    finally:
      if config_file:
        config_file.close()

    theater_combobox.addItems(self.theater_names)
    theater_combobox.setCurrentText(self.selected_theater)

    self.monitor = DDSMonitor(self._on_dds_change)
    self.console_append('Monitoring kneeboard DDS files for changes.');

    self.console_append('Generating kneeboard images...');
    self.converter = DDSConverter()
    self.converter.error.connect(self._on_conversion_error)
    self.converter.finished.connect(self._on_conversion_finished)
    self.converter.start()

    self.server = Server(self.port)
    self.server.error.connect(self._on_server_error)
    self.server.started.connect(self._on_server_started)
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
    config = None
    config_file = None

    try:
      with open('config.json', 'r') as config_file:
        config = json.loads(config_file.read())
    except Exception as json_read_err:
      config = {}
    finally:
      if config_file:
        config_file.close()

    config['selectedTheater'] = theater

    try:
      with open('config.json', 'w+') as config_file:
        config_file.write(json.dumps(config, indent=2)) 
    except Exception as json_write_err:
      self.console_append('Error writing selected theater to config file: ' + str(err), LogLevel.WARN)
    finally:
      if config_file:
        config_file.close()

  def _on_dds_change(self):
    self.console_append('Kneeboard DDS file(s) changed; regenerating images...') 
    self.converter = DDSConverter()
    self.converter.start()
    self.converter.finished.connect(self._on_conversion_finished)

  def _on_server_started(self):
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
