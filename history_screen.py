import os
import sqlite3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel)

from video_player_window import VideoPlayerWindow


class HistoryScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("History")
        self.setGeometry(100, 100, 840, 600)
        self.initUI()
        
    def initUI(self):
        
        self.head = QLabel("History", self)
        font = QFont("Arial", 20, QFont.Bold)
        self.head.setFont(font)
        self.head.setGeometry(20, 50, self.head.width(), self.head.height())
        
        headBox = QHBoxLayout()
        headBox.addWidget(self.head)
        
        # Cria a tabela com 4 colunas
        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Id", "Start time", "End time", "Filename", "Status", "Action"])
        self.table.resize(800, 350)
        self.table.move(20, 100)
        
        # Adiciona botões para navegar entre as páginas
        self.prev_button = QPushButton("Previous", self)
        self.prev_button.move(50, 520)
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self.prevPage)
        
        self.next_button = QPushButton("Next", self)
        self.next_button.move(150, 520)
        self.next_button.clicked.connect(self.nextPage)
        
        # Define o número de linhas por página e carrega a primeira página
        self.rows_per_page = 10
        self.loadPage(0)
        
    def loadPage(self, page):
        # Remove todas as linhas da tabela
        self.table.setRowCount(0)
        
        # Carrega as linhas para a página especificada
        start_row = page * self.rows_per_page
        end_row = start_row + self.rows_per_page

        # Conecta ao banco de dados
        conn = sqlite3.connect('polyp_tracker.db')

        # Cria um cursor para executar as consultas SQL
        cursor = conn.cursor()

        # Executa a consulta para obter as informações da tabela "history"
        cursor.execute("SELECT id, start_time, end_time, filename, status FROM history LIMIT ?, ?", (start_row, self.rows_per_page))

        # Obtém os resultados da consulta
        results = cursor.fetchall()

        # Preenche a tabela com as informações da consulta
        for row_data in results:
            # Adiciona uma linha na tabela
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Preenche as células da linha com as informações correspondentes
            self.table.setItem(row, 0, QTableWidgetItem(str(row_data[0])))
            self.table.setItem(row, 1, QTableWidgetItem(str(row_data[1])))
            self.table.setItem(row, 2, QTableWidgetItem(str(row_data[2])))
            self.table.setItem(row, 3, QTableWidgetItem(str(row_data[3])))
            self.table.setItem(row, 4, QTableWidgetItem(str(row_data[4])))
            self.table.setColumnWidth(3, 250)

            # Adiciona um botão na célula da última coluna
            button = QPushButton("Play", self)
            self.table.setCellWidget(row, 5, button)
            button.clicked.connect(self.playVideo)

        self.table.sortItems(1, True)

        # Atualiza o estado dos botões "Previous" e "Next"
        num_rows = self.table.rowCount()

        # Cria um cursor para executar as consultas SQL
        #cursor = conn.cursor()

        # Executa a consulta para obter o número total de linhas na tabela "history"
        cursor.execute("SELECT COUNT(*) FROM history")

        # Obtém o número total de linhas da consulta
        total_rows = cursor.fetchone()[0]

        # Fecha a conexão com o banco de dados
        conn.close()

        self.prev_button.setEnabled(page > 0)
        self.next_button.setEnabled(num_rows == self.rows_per_page and end_row < total_rows)
        
    def nextPage(self):
        # Carrega a próxima página
        current_page = self.table.rowCount() // self.rows_per_page
        self.loadPage(current_page + 1)
        
    def prevPage(self):
        # Carrega a página anterior
        current_page = self.table.rowCount() // self.rows_per_page
        self.loadPage(current_page - 1)
        
    def playVideo(self):
        button = self.sender()
        if button:
            row = self.table.indexAt(button.pos()).row()
            filename = self.table.item(row, 3).text()
            filename = os.path.abspath(filename)
            print(filename)
            videoPlayer = VideoPlayerWindow(filename, self)
            videoPlayer.exec_()
        
if __name__ == "__main__":
    app = QApplication([])
    window = HistoryScreen()
    window.show()
    app.exec_()
    