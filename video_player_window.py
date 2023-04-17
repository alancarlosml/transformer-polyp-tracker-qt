from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QPushButton, QHBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class VideoPlayerWindow(QDialog):
    def __init__(self, filename, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('Video Player')

        self.mediaPlayer = QMediaPlayer(self)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))

        videoWidget = QVideoWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(videoWidget)
        self.mediaPlayer.setVideoOutput(videoWidget)

        self.playButton = QPushButton("Play", self)
        self.pauseButton = QPushButton("Pause", self)
        self.stopButton = QPushButton("Stop", self)
        self.backButton = QPushButton("Back", self)
        self.forwardButton = QPushButton("Forward", self)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.playButton)
        buttonLayout.addWidget(self.pauseButton)
        buttonLayout.addWidget(self.stopButton)
        buttonLayout.addWidget(self.backButton)
        buttonLayout.addWidget(self.forwardButton)
        layout.addLayout(buttonLayout)

        self.playButton.clicked.connect(self.mediaPlayer.play)
        self.pauseButton.clicked.connect(self.mediaPlayer.pause)
        self.stopButton.clicked.connect(self.mediaPlayer.stop)
        self.backButton.clicked.connect(lambda: self.mediaPlayer.setPosition(self.mediaPlayer.position() - 5000))
        self.forwardButton.clicked.connect(lambda: self.mediaPlayer.setPosition(self.mediaPlayer.position() + 5000))
        
        self.setGeometry(100, 100, 400, 400)
        
        self.mediaPlayer.play()

