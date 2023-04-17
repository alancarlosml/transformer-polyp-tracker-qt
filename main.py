import sys
import sqlite3
import datetime
from pathlib import Path

import cv2
from PIL import Image

from PyQt5.QtCore import QTimer, QSize, Qt
from PyQt5.QtWidgets import QFileDialog, QApplication, QMainWindow, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap

from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

from model import load_model, process_frame, process_activation_map
from polyp_tracker_screen import PolypTrackerScreen
from global_vars import GlobalVars


class VideoProcessor(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.ui = PolypTrackerScreen()
        self.global_vars = GlobalVars.get_instance() 
        self.frameCount = 0
        self.totalFrames = 0
        self.cap = None
        self.fps = self.global_vars.fps
        self.detr = None
        self.conn = sqlite3.connect('polyp_tracker.db')
        self.conn.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, start_time DATE, end_time DATE, filename TEXT, status TEXT)')
        self.id_conn = 0    
                
        self.timer = QTimer()
        self.timer.setInterval(int(1000 / self.fps))
        self.timer.timeout.connect(self.processVideoFrame)
        self.ui.upload_btn.clicked.connect(self.loadVideo)
        self.ui.reset_btn.clicked.connect(self.resetProcessing)

    def getModel(self):
        if self.detr is None:
            self.detr = load_model()
            
    def processFrameWrapper(self, frame, process_type):
        detr = self.detr
        if process_type == 'frame':
            im, frame_time = process_frame(detr, frame)
            return im, frame_time
        elif process_type == 'activation_map':
            im = process_activation_map(detr, frame)
            return im
        else:
            self.ui.statusBar().showMessage("Status: Invalid process_type argument")
            
    def loadVideo(self):
        
        self.getModel() 
        
        self.resetProcessing()
        
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi)")
        
        now = datetime.datetime.now()
        formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
                
        cursor = self.conn.cursor()
        cursor.execute(f"INSERT INTO history (start_time, status) VALUES ('{formatted_now}', 'started')")
        self.conn.commit()
        self.id_conn = cursor.lastrowid

        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)

            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.totalFrames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            self.ui.progressBar.setMaximum(self.totalFrames)

            self.ui.reset_btn.setEnabled(True)
            self.ui.upload_btn.setEnabled(False)

            self.timer.setInterval(int(1000 / self.fps))
            self.timer.start()
            self.timer.timeout.connect(self.processVideoFrame)

    '''
    def processVideoFrame(self):
        frameNum = self.cap.get(cv2.CAP_PROP_POS_FRAMES)

        self.ui.progressBar.setValue(int(frameNum))

        success, frame = self.cap.read()
        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            processedFrame, processTime = self.process_frame_wrapper(frame, process_type='frame')
            
            im = Image.fromarray(cv2.cvtColor(processedFrame, cv2.COLOR_BGR2RGB))
            
            image_original = os.path.join('media', 'output', f'original_{int(frameNum):d}.png')
            im.save(image_original)
        
            activateMap = self.process_frame_wrapper(frame, process_type='activation_map')

            self.frameCount += 1
            self.displayFrame(processedFrame, activateMap, self.frameCount, processTime)

        else:
            self.timer.stop()
    '''
    
    def processVideoFrame(self):
        frameNum = self.cap.get(cv2.CAP_PROP_POS_FRAMES)

        self.ui.progressBar.setValue(int(frameNum))

        success, frame = self.cap.read()
        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            processedFrame, processTime = self.processFrameWrapper(frame, process_type='frame')
            
            im = Image.fromarray(cv2.cvtColor(processedFrame, cv2.COLOR_BGR2RGB))
            
            image_original = Path('media', 'output', f'original_{int(frameNum):d}.png')
            im.save(str(image_original))
        
            activateMap = self.processFrameWrapper(frame, process_type='activation_map')

            self.frameCount += 1
            self.displayFrame(processedFrame, activateMap, self.frameCount, processTime)

        else:
            self.timer.stop()
    
            
    def updateUI(self, processedFrame, activateMap, frameCount, processTime):
        #processed frame
        height, width, _ = processedFrame.shape
        bytesPerLine = 3 * width
        label_size = QSize(400, 400)
        rgb_processed_frame = cv2.cvtColor(processedFrame, cv2.COLOR_BGR2RGB)
        qImg = QImage(rgb_processed_frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qImg).scaled(label_size, Qt.KeepAspectRatio)

        # Define o tamanho do label e centraliza a imagem
        #label_size_scaled = QSize(pixmap.width(), pixmap.height())
        self.ui.video_label1.setPixmap(pixmap)
        self.ui.video_label1.setFixedSize(label_size)
        self.ui.video_label1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.video_label1.setAlignment(Qt.AlignCenter)

        #self.ui.video_label1.setPixmap(QPixmap.fromImage(qImg))
        #self.ui.video_label1.adjustSize()

        #activation maps
        height, width, _ = activateMap.shape
        bytesPerLine = 3 * width
        rgb_activate_map = cv2.cvtColor(activateMap, cv2.COLOR_BGR2RGB)
        qImgMap = QImage(rgb_activate_map.data, width, height, bytesPerLine, QImage.Format_RGB888)
        
        pixmap_map = QPixmap.fromImage(qImgMap).scaled(label_size, Qt.KeepAspectRatio)
        
        self.ui.video_label2.setPixmap(pixmap_map)
        self.ui.video_label2.setFixedSize(label_size)
        self.ui.video_label2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.video_label2.setAlignment(Qt.AlignCenter)

        #self.ui.video_label2.setPixmap(QPixmap.fromImage(qImgMap))
        #self.ui.video_label2.adjustSize()

        self.ui.frame_label.setText(f"Frame: {frameCount}")
        self.ui.processing_time_label.setText(f"Processing Time: {processTime:.2f} ms")

    def updateStatusBar(self, frameCount):
        if frameCount < self.totalFrames:
            self.ui.statusBar().showMessage("Status: Processing...")
            self.ui.reset_btn.setEnabled(True)
            self.ui.upload_btn.setEnabled(False)

            self.conn.execute(f"UPDATE history SET status = 'processing' WHERE id = {self.id_conn}")
            self.conn.commit()
        else:
            self.ui.statusBar().showMessage("Status: Processing completed successfully.")
            self.ui.reset_btn.setEnabled(False)
            self.ui.upload_btn.setEnabled(True)
            
    def clearOutputFiles(self, input_images_path):
        path = Path(input_images_path)
        for file_path in path.iterdir():
            try:
                if file_path.is_file() or file_path.is_symlink():
                    file_path.unlink()
            except Exception as e:
                self.ui.statusBar().showMessage("Status: Error on remove output files.")

    def saveVideo(self):
        now = datetime.datetime.now()
        formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
                        
        filename = now.strftime("%Y-%m-%d_%H-%M-%S.mp4")
        output_video_path = Path('media') / filename
        input_images_path = Path('media') / 'output'

        clip = ImageSequenceClip(str(input_images_path), fps=self.fps)
        clip.write_videofile(str(output_video_path))
        
        self.conn.execute(f"UPDATE history SET end_time = '{formatted_now}', filename = '{str(output_video_path)}', status = 'finished' WHERE id = {self.id_conn}")
        self.conn.commit()
        
        self.clearOutputFiles(str(input_images_path))
    
    '''    
    def clearOutputFiles(self, input_images_path):
        for filename in os.listdir(input_images_path):
            file_path = os.path.join(input_images_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                self.ui.statusBar().showMessage("Status: Error on remove output files.")

    def saveVideo(self):
        now = datetime.datetime.now()
        formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
                        
        filename = now.strftime("%Y-%m-%d_%H-%M-%S.mp4")
        output_video_path = os.path.join('media', filename)
        input_images_path = os.path.join('media', 'output')

        clip = ImageSequenceClip(input_images_path, fps=self.fps)
        clip.write_videofile(output_video_path)
        
        self.conn.execute(f"UPDATE history SET end_time = '{formatted_now}', filename = '{output_video_path}', status = 'finished' WHERE id = {self.id_conn}")
        self.conn.commit()
        
        self.clearOutputFiles(input_images_path)
    '''

    def displayFrame(self, processedFrame, activateMap, frameCount, processTime):
        self.updateUI(processedFrame, activateMap, frameCount, processTime)
        self.updateStatusBar(frameCount)
        if frameCount == self.totalFrames:
            self.saveVideo() 
            self.cap.release()     
                    
    def resetProcessing(self):
        self.video_path = None
        self.id_conn = 0
        self.frameCount = 0
        self.totalFrames = 0
        self.ui.reset_btn.setEnabled(False)
        self.ui.upload_btn.setEnabled(False)
        self.ui.frame_label.setText(f"Frame:")
        self.ui.processing_time_label.setText(f"Processing Time:")
        self.ui.video_label1.setPixmap(QPixmap())
        self.ui.video_label2.setPixmap(QPixmap())
        self.ui.progressBar.setValue(0)
        self.ui.statusBar().showMessage("Status: ")
        self.timer.stop()
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    video_processor = VideoProcessor()
    video_processor.ui.show()
    sys.exit(app.exec_())