import sys
import os
import json
import ntpath
import winreg
import fnmatch
import subprocess

from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import TCPServer, ThreadingMixIn
from enum import StrEnum
from datetime import datetime

from PIL import Image
from PyQt5.Qt import QDesktopServices, QUrl
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

SERVER_ROOT = 'serve'

DEFAULT_BMS_VERSION = '4.37'
DEFAULT_REGISTRY_KEY = get_registry_key(DEFAULT_BMS_VERSION)
DEFAULT_SERVER_PORT = 2676
DEFAULT_THEATERS = [
  {
    "name": "Korea",
    "addOnDir": ""
  },
  {
    "name": "Balkans",
    "addOnDir": "Add-On Balkans"
  },
  {
    "name": "Israel",
    "addOnDir": "Add-On Israel"
  },
  {
    "name": "EMF",
    "addOnDir": "Add-On EMF"
  }
]
DEFAULT_SELECTED_THEATER = DEFAULT_THEATERS[0]

def console_get_message(message, level = LogLevel.INFO):
  now = datetime.now()
  time = now.strftime('%H:%M:%S')
  return f'[{level} {time}] {message}'

# ======== Classes ========

class ThreadingServer(ThreadingMixIn, HTTPServer):
  pass

class HTTPHandler(SimpleHTTPRequestHandler):
  def __init__(self, *args, **kwargs):
    try:
      super().__init__(*args, directory=SERVER_ROOT, **kwargs)
    except Exception as handler_err:
      # These are mostly (always?) due to connections being forcibly closed by the app; no big
      # deal and safe to ignore.
      # sys.stderr.write('Handler error: ' + str(handler_err) + '\n')
      pass

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
      with ThreadingServer(('0.0.0.0', self.port), HTTPHandler) as self._server:
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

  def __init__(self, dds_path):
    super(DDSConverter, self).__init__()
    self.dds_path = dds_path

  def run(self):
    try:
      if os.path.isdir(self.dds_path):
        for i in range(7982, 7998):
          dds_file = os.path.join(self.dds_path, f'{i}.dds')
          self.convert(dds_file)
      else:
        self.convert(self.dds_path)

    except Exception as err:
      self.error.emit(err)

  def stop(self):
    self.wait()

  def convert(self, dds_file):
    dds_index = int(ntpath.basename(dds_file).split('.')[0])
    img_index = (dds_index - 7982) + 1

    if img_index < 10:
      img_index = f'0{str(img_index)}' 

    out_left_path = os.path.join(SERVER_ROOT, f'l{img_index}.png')
    out_right_path = os.path.join(SERVER_ROOT, f'r{img_index}.png')

    with Image.open(dds_file) as img:
      left_dims = (0 ,0, int(img.size[0] / 2), img.size[1])
      right_dims = int(img.size[0] / 2), 0, img.size[0], img.size[1]
      self.write_png(img, out_left_path, left_dims)
      self.write_png(img, out_right_path, right_dims)

  def write_png(self, img, out_path, dims):
    cropped = img.crop(dims)
    cropped.save(out_path, 'png')

class DDSMonitor():
  def __init__(self, bms_home_dir, on_change):
    super(DDSMonitor, self).__init__()
    self.bms_home_dir = bms_home_dir
    self.on_change = on_change
    self.fs_watcher = None
    self.kneeboards = []
    self.dds_dir = None

  def _get_kneeboards(self, selected_theater):
    kneeboards = []
    dds_dir = None
    addon_dir = selected_theater['addOnDir']

    if addon_dir:
      dds_dir = os.path.join(self.bms_home_dir, 'Data', addon_dir, 'Terrdata', 'Objects', 'KoreaObj')
    else:
      dds_dir = os.path.join(self.bms_home_dir, 'Data', 'TerrData', 'Objects', 'KoreaObj')

    for i in range(7982, 7998):
      kneeboards.append(os.path.join(dds_dir, f'{i}.dds'))

    return kneeboards, dds_dir

  def start(self, selected_theater):
    kneeboards, dds_dir = self._get_kneeboards(selected_theater)
    self.kneeboards = kneeboards
    self.dds_dir = dds_dir
    self.fs_watcher = QFileSystemWatcher(kneeboards)
    self.fs_watcher.fileChanged.connect(self.on_change)

    return dds_dir

  def restart(self, selected_theater):
    kneeboards = self.kneeboards
    dds_dir = self.dds_dir

    if kneeboards and self.fs_watcher.files():
      self.fs_watcher.removePaths(kneeboards)

    if selected_theater:
      kneeboards, dds_dir = self._get_kneeboards(selected_theater)
      self.kneeboards = kneeboards
      self.dds_dir = dds_dir

    self.fs_watcher.addPaths(kneeboards)

    return dds_dir

class BriefingConverter(QThread):
  error = pyqtSignal(Exception)

  def __init__(self, briefing_dir):
    super(BriefingConverter, self).__init__()
    self.briefing_dir = briefing_dir

  def run(self):
    most_recent_briefing = None
    most_recent_time = 0

    try:
      entries = os.scandir(self.briefing_dir)

      for entry in entries:
        if fnmatch.fnmatch(entry, '*briefing.html'):
          mod_time = entry.stat().st_mtime_ns

          if mod_time > most_recent_time:
            most_recent_briefing = entry
            most_recent_time = mod_time

      entries.close()

      if most_recent_briefing:
        # TODO: This is an ugly way to copy a file, but I was getting errors with
        # shutil.copy/copy2 because the BMS process still had the file open. :\
        out_path = os.path.join(SERVER_ROOT, 'briefing.html')
        cmd = 'copy "%s" "%s" >nul 2>&1' % (most_recent_briefing.path, out_path)
        status = subprocess.call(cmd, shell=True)

    except Exception as err:
      self.error.emit(err)

  def stop(self):
    self.wait()

  def convert(self, dds_file):
    dds_index = int(ntpath.basename(dds_file).split('.')[0])
    img_index = (dds_index - 7982) + 1

    if img_index < 10:
      img_index = f'0{str(img_index)}' 

    out_left_path = os.path.join(SERVER_ROOT, f'l{img_index}.png')
    out_right_path = os.path.join(SERVER_ROOT, f'r{img_index}.png')

    with Image.open(dds_file) as img:
      left_dims = (0 ,0, int(img.size[0] / 2), img.size[1])
      right_dims = int(img.size[0] / 2), 0, img.size[0], img.size[1]
      self.write_png(img, out_left_path, left_dims)
      self.write_png(img, out_right_path, right_dims)

  def write_png(self, img, out_path, dims):
    cropped = img.crop(dims)
    cropped.save(out_path, 'png')

class BriefingMonitor(): 
  def __init__(self, bms_home_dir, on_change):
    super(BriefingMonitor, self).__init__()
    self.bms_home_dir = bms_home_dir
    self.on_change = on_change
    self.briefing_dir = None
    self.fs_watcher = None

  def start(self):
    self.briefing_dir = os.path.join(self.bms_home_dir, 'User', 'Briefings')
    self.fs_watcher = QFileSystemWatcher([self.briefing_dir])
    self.fs_watcher.directoryChanged.connect(self.on_change)

    return self.briefing_dir

# ======== Window and UI Elements ========

class Window(QMainWindow):
  def __init__(self):
    super(Window, self).__init__()

    self.dds_monitor = None
    self.dds_dir = None
    self.dds_converter = None
    self.dds_converter_err = None
    self.briefing_monitor = None
    self.briefing_converter = None
    self.briefing_converter_err = None

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
    self.theater_combobox = theater_combobox

    theater_selection_layout.addWidget(theater_label)
    theater_selection_layout.addStretch(1)
    theater_selection_layout.addWidget(theater_combobox)
    theater_selection_layout.setContentsMargins(4, 0, 0, 0)

    doc_button = QPushButton()
    doc_button.setObjectName('doc_button')
    doc_button.setText('Documentation')
    doc_button.clicked.connect(self.doc_open)

    clear_button = QPushButton()
    clear_button.setObjectName('clear_button')
    clear_button.setText('Clear Console')
    clear_button.clicked.connect(self.console_clear)

    controls_layout.addWidget(theater_selection)
    controls_layout.addStretch(1)
    controls_layout.addWidget(doc_button)
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
    self.theater_names = list(map(lambda t: t['name'], DEFAULT_THEATERS))
    self.bms_version = DEFAULT_BMS_VERSION
    self.registry_key = DEFAULT_REGISTRY_KEY

    config_file = None
    self.selected_theater = DEFAULT_SELECTED_THEATER

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
        selected_theater = self._get_theater_from_name(config['selectedTheater'])

        if selected_theater:
          self.selected_theater = selected_theater
      except Exception as selected_theater_err:
        pass

    except Exception as err:
      self.console_append('Unable to read config file; using default values.', LogLevel.INFO)

    finally:
      if config_file:
        config_file.close()

    bms_home = self._get_bms_home_dir()
    init_failed = False

    if bms_home:
      briefing_dir = None

      try:
        self.briefing_monitor = BriefingMonitor(bms_home, self._on_briefing_change)
        briefing_dir = self.briefing_monitor.start()
        self.console_append('Monitoring briefings directory for changes.')
      except Exception as briefing_monitor_err:
        self.console_append('Error monitoring briefings directory for changes: ' + str(briefing_monitor_err), LogLevel.ERROR)
        init_failed = True

      if briefing_dir:
        self.briefing_converter = BriefingConverter(briefing_dir)
        self.briefing_converter.error.connect(self._on_briefing_conversion_error)
        self.briefing_converter.finished.connect(self._on_briefing_conversion_finished) 
        self.briefing_converter.start()

      if (not init_failed):
        try:
          self.dds_monitor = DDSMonitor(bms_home, self._on_dds_change)
          self.dds_dir = self.dds_monitor.start(self.selected_theater)
          self.console_append('Monitoring kneeboard DDS files for changes.')
        except Exception as dds_monitor_err:
          self.console_append('Error monitoring kneeboard DDS files for changes: ' + str(dds_monitor_err), LogLevel.ERROR)
          init_failed = True

        if self.dds_dir:
          self.console_append('Generating kneeboard images...')

          self.theater_combobox.setEnabled(False)
          self.dds_converter = DDSConverter(self.dds_dir)
          self.dds_converter.error.connect(self._on_dds_conversion_error)
          self.dds_converter.finished.connect(self._on_dds_conversion_finished)
          self.dds_converter.start()

          self.server = Server(self.port)
          self.server.error.connect(self._on_server_error)
          self.server.started.connect(self._on_server_started)
          self.server.start()

    else:
      init_failed = True

    theater_combobox.addItems(self.theater_names)
    theater_combobox.setCurrentText(self.selected_theater['name'])
    theater_combobox.currentTextChanged.connect(self._on_theater_change)

    if init_failed:
      self.console_append('Initialization failed.', LogLevel.ERROR)

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

  def doc_open(self):
    try:
      QDesktopServices.openUrl(QUrl('https://github.com/doomsean/bmsnav'))
    except Exception as doc_err:
      self.console_append('Unable to open documentation website: ' + str(doc_err))

  def _get_bms_home_dir(self):
    try:
      reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
      key = winreg.OpenKey(reg, self.registry_key)

      for idx in range(8):
        try:
          vals = winreg.EnumValue(key, idx)

          if vals[0] == 'baseDir':
            base_dir = os.path.normpath(vals[1])

            if os.path.isdir(base_dir):
              return base_dir

        except Exception as reg_err:
          raise reg_err

    except Exception as err:
      sys.stderr.write(str(err))
      self.console_append('Error locating BMS directory from registry; specify with "bmsHome" in config.json file.', LogLevel.ERROR)

    return None

  def _get_theater_from_name(self, theater_name):
    for theater in self.theaters: 
      if theater['name'] == theater_name:
        return theater

    return None

  def _on_theater_change(self, theater_name):
    theater = self._get_theater_from_name(theater_name) 

    if not theater:
      self.console_append('Invalid theater: ' + theater_name, LogLevel.ERROR)
    elif theater != self.selected_theater['name']:
      self.console_append('Theater changed; generating kneeboard images...')

      self.selected_theater = theater

      if self.dds_monitor:
        self.dds_dir = self.dds_monitor.restart(theater)

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

      config['selectedTheater'] = theater_name

      try:
        with open('config.json', 'w+') as config_file:
          config_file.write(json.dumps(config, indent=2)) 
      except Exception as json_write_err:
        self.console_append('Error writing selected theater to config file: ' + str(err), LogLevel.WARN)
      finally:
        if config_file:
          config_file.close()

      self.theater_combobox.setEnabled(False)
      self.dds_converter = DDSConverter(self.dds_dir)
      self.dds_converter.error.connect(self._on_dds_conversion_error)
      self.dds_converter.finished.connect(self._on_dds_conversion_finished)
      self.dds_converter.start()

  def _on_dds_change(self, path):
    if "7982.dds" in path:
      self.console_append('Kneeboard DDS file(s) changed; regenerating images...') 
      self.theater_combobox.setEnabled(False)

    self.dds_converter = DDSConverter(path)
    self.dds_converter.start()

    if "7997.dds" in path:
      self.converter.finished.connect(self._on_conversion_finished)

  def _on_dds_conversion_finished(self):
    if not self.dds_converter_err:
      self.console_append('Kneeboard images generated.')
    else:
      self.console_append('Error generating kneeboard image(s): ' + str(self.dds_converter_err), LogLevel.ERROR)

    self.theater_combobox.setEnabled(True)
    self.dds_monitor.restart(None)
    self.dds_converter_err = None

  def _on_dds_conversion_error(self, err):
    self.dds_converter_err = err;

  def _on_briefing_change(self, path):
    self.console_append('Briefing changed; copying HTML file...')
    self.briefing_converter = BriefingConverter(path)
    self.briefing_converter.error.connect(self._on_briefing_conversion_error)
    self.briefing_converter.finished.connect(self._on_briefing_conversion_finished)
    self.briefing_converter.start()

  def _on_briefing_conversion_finished(self):
    if not self.briefing_converter_err:
      self.console_append('Copied briefing HTML file.')
    else:
      self.console_append('Error copying briefing HTML file: ' + str(self.briefing_converter_err), LogLevel.ERROR)

    self.briefing_converter_err = None

  def _on_briefing_conversion_error(self, err):
    self.briefing_converter_err = err

  def _on_server_started(self):
    self.console_append(f'Server started on port {self.port}: waiting for requests.')
    self.console_append('Initialization complete.')

  def _on_server_error(self, err):
    self.console_append('Error initializing server: ' + str(err), LogLevel.ERROR)

# ======== Main ========

if not os.path.exists(SERVER_ROOT):
  os.makedirs(SERVER_ROOT)

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
