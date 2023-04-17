from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (QVBoxLayout, QFileDialog, QWidget, QMainWindow, QAction, QGroupBox, 
                             QLabel, QHBoxLayout, QPushButton, QProgressBar)

from history_screen import HistoryScreen
from global_vars import GlobalVars

class PolypTrackerScreen(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.initUI()
        self.main_screen = None
        self.history_screen = None
        self.global_vars = GlobalVars.get_instance() 

    def initUI(self):
        
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        fontBold = QFont()
        fontBold.setBold(True)
        
        menubar = self.menuBar()
        self.polyp_menu = menubar.addMenu('File')
        
        self.open_history_action = QAction('History', self)
        self.open_history_action.setShortcut('Ctrl+H')
        self.open_history_action.triggered.connect(self.open_history)
        self.polyp_menu.addAction(self.open_history_action)
        
        self.exit_action = QAction('Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(self.close)
        self.polyp_menu.addAction(self.exit_action)
        
        self.layout_menus = QHBoxLayout()
        self.layout_menus.addWidget(menubar)

        self.setWindowTitle("PolypTracker")
        self.setGeometry(100, 100, 840, 600)
 
        self.head = QLabel("PolypTracker", self)
        font = QFont("Arial", 20, QFont.Bold)
        self.head.setFont(font)
        
        upload_layout = QHBoxLayout()
        upload_groupbox = QGroupBox()
        upload_layout.addWidget(upload_groupbox)
        
        groupbox_layout = QVBoxLayout(upload_groupbox)

        upload_hbox = QHBoxLayout()
        upload_hbox.setContentsMargins(0, 0, 0, 0)

        upload_label = QLabel("Weights path:")
        upload_label.setFont(fontBold)

        self.upload_path = QLabel("")
        self.upload_path.setAlignment(Qt.AlignLeft)

        upload_button = QPushButton("Upload")

        upload_hbox.addWidget(upload_label)
        upload_hbox.addWidget(self.upload_path)
        upload_hbox.addWidget(upload_button, alignment=Qt.AlignRight)

        groupbox_layout.addLayout(upload_hbox)
        upload_button.clicked.connect(self.open_file_dialog)

        upload_groupbox.setStyleSheet("QGroupBox { border: 1px solid black; }")

        self.video_label1 = QLabel(self)
        self.video_label1.setAlignment(Qt.AlignCenter)
        self.video_label1.setStyleSheet("border: 1px solid black")
        self.video_label1.setFixedSize(400, 400)

        self.video_label2 = QLabel(self)
        self.video_label2.setAlignment(Qt.AlignCenter)
        self.video_label2.setStyleSheet("border: 1px solid black")
        self.video_label2.setFixedSize(400, 400)

        self.video_processing_label = QLabel("Video Processing", self)
        self.video_processing_label.setAlignment(Qt.AlignCenter)
        self.video_processing_label.setFont(fontBold)

        self.activation_map_label = QLabel("Activation Map", self)
        self.activation_map_label.setAlignment(Qt.AlignCenter)
        self.activation_map_label.setFont(fontBold)

        self.frame_label = QLabel("Frame: ", self)
        self.frame_label.setAlignment(Qt.AlignLeft)

        self.processing_time_label = QLabel("Processing Time: ", self)
        self.processing_time_label.setAlignment(Qt.AlignLeft)

        self.upload_btn = QPushButton("Start", self)
        self.upload_btn.setGeometry(QRect(10, 550, 150, 40))

        self.reset_btn = QPushButton("Reset", self)
        self.reset_btn.setGeometry(QRect(170, 550, 150, 40))

        self.upload_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        
        self.statusBar().showMessage("Status: ")
        
        self.progress_label = QLabel("Progress: ", self)
        self.progress_label.setAlignment(Qt.AlignLeft)
        
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)

        progressBox = QHBoxLayout()
        progressBox.addWidget(self.progress_label)
        progressBox.addWidget(self.progressBar)

        headBox = QHBoxLayout()
        headBox.addWidget(self.head)

        labelBox = QHBoxLayout()
        labelBox.addWidget(self.video_processing_label)
        labelBox.addWidget(self.activation_map_label)

        imageBox = QHBoxLayout()
        imageBox.addWidget(self.video_label1)
        imageBox.addWidget(self.video_label2)
        
        resultBox = QHBoxLayout()
        resultBox.addWidget(self.frame_label)
        resultBox.addWidget(self.processing_time_label)

        groupBox = QGroupBox(self)
        groupBox.setStyleSheet("QGroupBox { border: 1px solid black; }")
        groupBox.setLayout(resultBox)
        
        progressGroupBox = QGroupBox(self)
        progressGroupBox.setStyleSheet("QGroupBox { border: 1px solid black; }")
        progressGroupBox.setLayout(progressBox)
        
        vbox = QVBoxLayout()
        
        headWidget = QWidget()
        headWidget.setLayout(headBox)
        layout.addLayout(self.layout_menus)
        layout.addStretch(1)
        vbox.addWidget(headWidget)
        
        vbox.addLayout(upload_layout)
        vbox.addLayout(labelBox)
        vbox.addLayout(imageBox)
        vbox.addWidget(self.upload_btn)
        vbox.addWidget(self.reset_btn)
        vbox.addWidget(groupBox)
        vbox.addWidget(progressGroupBox)

        layout.addLayout(vbox)
        
    def open_file_dialog(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Arquivos de modelo (*.pth)")
        file_dialog.setDefaultSuffix("pth")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.upload_path.setText(file_path)
            self.global_vars.weights_path = file_path 
            self.upload_btn.setEnabled(True)   

    def open_history(self):
        if not self.history_screen:  
            self.history_screen = HistoryScreen() 
        self.history_screen.show()
