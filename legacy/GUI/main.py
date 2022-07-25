import sys
import logging
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5 import *

import pyvisa as visa
import numpy as np
import struct
import sys

import motor_control
import config_parse

# Make window setups their own functions?
# May need a "refresh status" function that re-checks subsystems to update status display (periodically?)
# Add: display positions on GUI
# Add: bring together all modules
# Add scan inputs to GUI
# Make scan GUI load defaults from config file
# Make input from GUI change params
# Add: saving numpy files for data https://stackoverflow.com/questions/30376581/save-numpy-array-in-append-mode
# BBB qemu emulation: https://github.com/hufscse-linux/bbbqemu

def initialize_scope(scope_type, IP_address):
    ''' Initalize and connect to oscilliscope. Supported scope types are Tektronix and Agilent,
    requiring slightly different commands for each.'''
    
    global logfile
    global log_window
    
    rm = visa.ResourceManager('@py')
    log_message(logfile, log_window, "Connecting to {} scope @ {}".format(scope_type, IP_address))
    
    try:
        if scope_type is 'Agilent':
            # Initialize connection to scope
            scope = rm.open_resource('TCPIP0::%s::inst0::INSTR'%(IP_address))
            print(scope.query('*IDN?'))
            # Set up scope
            scope.write(":WAVEFORM:FORMAT BYTE")
            scope.write(":WAVeform:POINts:MODE NORMAL")
            scope.write(":WAVeform:POINts 100")
            scope.write(":TRIGger:MODE EDGE")
            scope.write(":TRIGger:SOURce EXTernal")
            scope.write(":TRIGger:LEVel 0.5")
            log_message(logfile, log_window, "Successful configuration of {} scope ({})".format(scope_type, IP_address))
            return scope
        elif scope_type is 'Tektronix':
            scope = rm.open_resource('TCPIP0::%s::inst0::INSTR'%(IP_address))
            print(scope.query('*IDN?'))
            log_message(logfile, log_window, "Successful configuration of {} scope ({})".format(scope_type, IP_address))
            return scope
    except Exception as e:
        log_message(logfile, log_window, e)
        return None

def log_message(logfile, log_window, message):
    ''' Log message and timestamp to both GUI log window and log file. '''
    logging.info(message)
    with open(logfile, 'r') as f:
        text=f.read()
        log_window.setText(text)
    log_window.moveCursor(QTextCursor.End)

def dir_button_pressed(logfile, log_window, d):
    if d is 'up':
        log_message(logfile, log_window, 'Moving up (+Y)')
    elif d is 'down':
        log_message(logfile, log_window, 'Moving down (-Y)')
    elif d is 'left':
        log_message(logfile, log_window, 'Moving left (-X)')
    elif d is 'right':
        log_message(logfile, log_window, 'Moving right (+X)')
    elif d is 'forward':
        log_message(logfile, log_window, 'Moving forward (+Z)')
    elif d is 'back':
        log_message(logfile, log_window, 'Moving back (-Z)')
        
def config_save(config_file_path, config_editor, logfile, log_window):
    text = config_editor.toPlainText()
    try:
        with open(config_file_path, 'w') as f:
            f.write(text)
        log_message(logfile, log_window, 'Config. file saved to {}'.format(config_file_path))
        # Re-parse and load config file
    except Exception as e:
        log_message(logfile, log_window, 'Error in saving file: {}'.format(e))

if __name__ == '__main__':
    # Setup logging
    logfile = 'log.txt'
    logging.basicConfig(filename=logfile, format='%(asctime)s %(message)s', datefmt='%I:%M:%S', filemode='w', level=logging.DEBUG)
    
    # Setup GUI
    app = QApplication(sys.argv)
    
    main_window = QMainWindow()
    main_window.setFixedSize(600,600)
    main_window.setWindowTitle('NuMI horn field-mapping system')
    
    window = QWidget()
    window_layout = QGridLayout()
    window.setLayout(window_layout)
    
    control_window = QWidget()
    control_layout = QHBoxLayout()
    control_window.setLayout(control_layout)
    
    control_buttons = QWidget()
    control_grid = QGridLayout()
    control_buttons.setLayout(control_grid)
    control_layout.addWidget(control_buttons)
    
    # Log output window
    log_window = QTextEdit(window)
    log_window.setReadOnly(True)
    log_window.setLineWrapMode(QTextEdit.NoWrap)
    font = log_window.font()
    font.setFamily("Courier")
    font.setPointSize(10)
    log_message(logfile, log_window, 'Program initalized.')
    
    # Read in configuration file
    try:
        scope_A_params, scope_B_params = config_parse.get_scope_params()
        BB = config_parse.get_BB_params()
    except Exception as e:
        log_message(logfile, log_window, 'Error in loading configuration file: {}'.format(e))
        
    #------- Setup status window ---------------
    readout = QTextEdit()
    # Temporary variable for designing layout
    
    # Try connecting to both scopes. If successful, change status accordingly
    # Read scope parameters from the config file
    
    scope_A_device = initialize_scope(scope_A_params['Type'], scope_A_params['IP'])
    scope_B_device = initialize_scope(scope_B_params['Type'], scope_B_params['IP'])
    if scope_A_device and scope_B_device:
        log_message(logfile, log_window, 'Scope connections successful')
        oscope_status = "OK"
    else:
        log_message(logfile, log_window, 'Error in connecting to scopes')
        oscope_status = "Failed"
    
    #oscope_status = "OK"
    probe_status = "OK"
    motor_status = "Failed"
    
    green = '#78BE20'
    red = '#AF272F'
    
    if oscope_status is "OK":
        oscope_status_color = green
    else:
        oscope_status_color = red
    
    x_pos = 0.0
    y_pos = 0.0
    z_pos = 10.0
    readout_text = '''
    <body style="background-color:#f2f2f2;">
    <center>
    <table cellpadding=10>
        <tr><td style="text-align: center;"><h2>Subsystem Status Checks</h2></td></tr>
    </table>
    <table border cellpadding=10>
        <tr><td style="text-align: center; background-color:{}">Oscilloscopes: <b>{}</b></td></tr>
    </table>
    <p>&nbsp;</p>
    <font size=4>
    <table cellpadding=5>
        <tr><td colspan=2 style="text-align: center;"><h2>Live Position Readings</h2></td></tr>
        <tr>
            <td style="text-align: center;">X-axis</td>
            <td style="text-align: center;">{}</td>
        </tr>
        <tr>
            <td style="text-align: center;">Y-axis</td>
            <td style="text-align: center;">{}</td>
        </tr>
        <tr>
            <td style="text-align: center;">Z-axis</td>
            <td style="text-align: center;">{}</td>
        </tr>
    </table>
    </font>
    </center>
    </body>
    '''.format(oscope_status_color, oscope_status, x_pos, y_pos, z_pos)
    readout.setText(readout_text)
    
    control_layout.addWidget(readout)
    
    #-----------------------------------
    
    # These each need to be fleshed out
    cal_window = QWidget()
    DAQ_window = QWidget()
    scan_window = QWidget()
    
    #------------Setup Config Editor Window-------------
    config_window = QWidget()
    config_window_layout = QGridLayout()
    config_window.setLayout(config_window_layout)
    
    config_editor = QPlainTextEdit()
    font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
    config_editor.setFont(font)
    font.setPointSize(10)
    config_file_path = 'config.ini'
    
    save_config_button = QPushButton('Save Config')
    save_config_button.clicked.connect(lambda: config_save(config_file_path, config_editor, logfile, log_window)) # save file
    
    config_window_layout.setRowStretch(0,9)
    config_window_layout.setRowStretch(1,1)
    
    config_window_layout.addWidget(config_editor,0,0)
    config_window_layout.addWidget(save_config_button,1,0)
    
    with open(config_file_path, 'r') as f:
        config_text = f.read()
    
    config_editor.setPlainText(config_text)
    
    #-----------------------------------
    
    # Main menubar
    menubar = main_window.menuBar()
    file_menu = menubar.addMenu('File')
    
    exit_act = QAction('Exit', window)        
    exit_act.triggered.connect(qApp.quit)
    file_menu.addAction(exit_act)
    
    # Initialize tabs
    tabs = QTabWidget()
    tabs.addTab(control_window, "Control")
    tabs.addTab(config_window, "Config")
    tabs.addTab(cal_window, "Calibration")
    tabs.addTab(DAQ_window, "DAQ")
    tabs.addTab(scan_window, "Scan")
    
    # Setup buttons
    u_button = QPushButton('Up')
    control_grid.addWidget(u_button,0,0,1,3)
    u_button.clicked.connect(lambda: dir_button_pressed(logfile, log_window, 'up'))
    d_button = QPushButton('Down')
    control_grid.addWidget(d_button,1,0,1,3)
    d_button.clicked.connect(lambda: dir_button_pressed(logfile, log_window, 'down'))
    l_button = QPushButton('Left')
    control_grid.addWidget(l_button,2,0,2,1)
    l_button.clicked.connect(lambda: dir_button_pressed(logfile, log_window, 'left'))
    r_button = QPushButton('Right')
    control_grid.addWidget(r_button,2,2,2,1)
    r_button.clicked.connect(lambda: dir_button_pressed(logfile, log_window, 'right'))
    f_button = QPushButton('Forward')
    control_grid.addWidget(f_button,2,1)
    f_button.clicked.connect(lambda: dir_button_pressed(logfile, log_window, 'forward'))
    b_button = QPushButton('Back')
    control_grid.addWidget(b_button,3,1)
    b_button.clicked.connect(lambda: dir_button_pressed(logfile, log_window, 'back'))
    
    window_layout.setRowStretch(0, 3)
    window_layout.addWidget(tabs,0,0)
    window_layout.setRowStretch(1, 1)
    window_layout.addWidget(log_window,1,0)
    
    main_window.setCentralWidget(window)
    main_window.show()
    sys.exit(app.exec_())
