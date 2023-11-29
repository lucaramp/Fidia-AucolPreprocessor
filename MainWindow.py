
import builtins
import os

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QColor, QIntValidator
from PySide2.QtWidgets import (QMainWindow, QListWidget, QAction, QSplitter, QVBoxLayout, QWidget, QStatusBar,
                               QFileDialog, QApplication, QListWidgetItem, QLineEdit, QLabel, QGridLayout, QPushButton,
                               QHBoxLayout)
from Preprocessor import Preporcessor

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Carica il file di stile
        with open('./QSS/NeonButtons.qss', 'r') as f:
            style = f.read()
        # Applica lo stile alla finestra
        self.setStyleSheet(style)

        self.setWindowTitle("Aucol Pre Processor")
        self.setWindowIcon(QIcon("./IMG/Fidialogo.bmp"))
        self.resize(1200,800)
        self.file_name = ''
        self.dir_name = ''

        # creo il listWIdget per visualizzare il file originale ed il post processato
        self.orig_file_widget = QListWidget()
        self.out_file_widget = QListWidget()

        self.orig_file_widget.verticalScrollBar().valueChanged.connect(self. v_sync_scroll_list_widget)
        self.out_file_widget.verticalScrollBar().valueChanged.connect(self.v_sync_scroll_list_widget)

        self.orig_file_widget.horizontalScrollBar().valueChanged.connect(self.h_sync_scroll_list_widget)
        self.out_file_widget.horizontalScrollBar().valueChanged.connect(self.h_sync_scroll_list_widget)

        self.orig_file_widget.itemSelectionChanged.connect(self.sync_selection_list)
        self.out_file_widget.itemSelectionChanged.connect(self.sync_selection_list)

        self.defines_widget = QListWidget()
        self.defines_widget.itemSelectionChanged.connect(self.update_defines)

        self.next_diff_butt = QPushButton("Next Diff")
        self.prev_diff_butt = QPushButton("Prev Diff")

        self.next_diff_butt.clicked.connect(self.on_but_next_clicked)
        self.prev_diff_butt.clicked.connect(self.on_but_prev_clicked)

        butt_ly = QHBoxLayout()
        butt_ly.addWidget(self.prev_diff_butt)
        butt_ly.addWidget(self.next_diff_butt)
        two_butt = QWidget()
        two_butt.setLayout(butt_ly)
        defines_ly = QVBoxLayout()
        defines_ly.addWidget(two_butt)
        defines_ly.addWidget(self.defines_widget)
        split_defines = QWidget()
        split_defines.setLayout(defines_ly)
        # Crea un QSplitter per gestire la disposizione dei widget
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.orig_file_widget)
        splitter.addWidget(self.out_file_widget)
        splitter.addWidget(split_defines)
        splitter.setStretchFactor(0,4)
        splitter.setStretchFactor(1,4)
        splitter.setStretchFactor(2,2)

        # Crea un layout e aggiungi il QSplitter
        layout = QVBoxLayout()
        layout.addWidget(splitter)

        # Crea un QWidget centrale per la finestra principale e imposta il layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Crea una barra di stato
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Crea un menu a tendina con le voci "Open" e "Exit"
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        self.open_action = QAction("Open", self)
        self.open_action.triggered.connect(self.open_file)

        self.analyze_action = QAction("Analyze Defines",self)
        self.analyze_action.triggered.connect(self.analyze_file)
        self.analyze_action.setEnabled(False)

        self.preprocess_action = QAction("Preprocess File",self)
        self.preprocess_action.triggered.connect(self.preprocess_file)
        self.preprocess_action.setEnabled(False)

        self.prev_diff_butt.setEnabled(False)
        self.next_diff_butt.setEnabled(False)

        self.save_as_action = QAction("Save as", self)
        self.save_as_action.triggered.connect(self.save_as)
        self.save_as_action.setEnabled(False)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(self.open_action)
        file_menu.addAction(self.analyze_action)
        file_menu.addAction(self.preprocess_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_as_action)
        file_menu.addAction(exit_action)

        #redirigo la print sulla status bar
        self.sys_print = builtins.print
        builtins.print = self.print_to_status_bar

        #istanzio il preprocessore
        self.processor = Preporcessor()

    def print_to_status_bar(self, *args, **kwargs):
        message = ' '.join(map(str, args))
        self.sys_print(message)
        # Aggiorna la barra di stato
        self.status_bar.showMessage(message,timeout=15000)

    def open_file(self):
        # Implementa qui la logica per aprire un orig_file_lines
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Aucol File", "", "Aucol Files (*.plc);;All Files (*)")
        self.analyze_action.setEnabled(False)
        self.preprocess_action.setEnabled(False)
        self.next_diff_butt.setEnabled(False)
        self.prev_diff_butt.setEnabled(False)
        self.save_as_action.setEnabled(False)
        if file_path:
            #cancello le liste
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.orig_file_widget.clear() , self.defines_widget.clear() , self.out_file_widget.clear()
            self.dir_name = os.path.dirname(file_path)
            self.file_name = os.path.basename(file_path)
            print(f"Selected {self.file_name} from {self.dir_name}")
            self.addFileToListWidget(self.file_name,self.orig_file_widget)
            self.processor.setOriginalFileName(self.dir_name,self.file_name)
            self.analyze_action.setEnabled(True)
            QApplication.restoreOverrideCursor()
        pass

    def addFileToListWidget(self,fileName,widget : QListWidget, bFormatEmpty : bool = False) -> None:
        file_lst = list()
        with open(self.dir_name + os.sep + fileName, 'r') as f:
            file_lst = f.readlines()
        widget.clear()
        lst = [s.rstrip('\n') for s in file_lst]
        if widget is self.defines_widget:
            for text in lst:
                item = QListWidgetItem(self.defines_widget)
                widget.addItem(item)
                line_view = QLabel()
                line_edit = QLineEdit()

                linesplit = text.split("=")
                define_key =""
                value_key =""
                if len(linesplit) > 0:
                    define_key = linesplit[0]
                    value_key = linesplit[1]

                line_view.setText(define_key)
                line_edit.setText(value_key)
                two_cols = QWidget()
                ly = QGridLayout()
                ly.addWidget(line_view,0,0)
                ly.addWidget(line_edit,0,1)
                ly.setColumnStretch(0,80)
                ly.setColumnStretch(1,20)
                two_cols.setLayout(ly)
                item.setSizeHint(two_cols.sizeHint())
                widget.setItemWidget(item, two_cols )

        else:
            widget.addItems(lst)
        if bFormatEmpty:
            # Cerca l'elemento con il testo 'pippo' e cambia il suo colore di sfondo e carattere
            for i in range(widget.count()):
                item = widget.item(i)
                if self.processor.EMPTY_LINE_TAG in item.text():
                    item.setBackground(QColor('yellow'))  # Cambia il colore di sfondo in giallo
                    item.setForeground(QColor('red'))  # Cambia il colore del carattere in rosso

    #def updateText(self, text):
        # Salva il nuovo testo in una variabile di istanza
        #self.updated_text = text

    def analyze_file(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        print(f"Analyzing {self.file_name}   in {self.dir_name}")
        self.preprocess_action.setEnabled(False)
        self.next_diff_butt.setEnabled(False)
        self.prev_diff_butt.setEnabled(False)
        self.save_as_action.setEnabled(False)
        if self.processor.ParceDirectives():
            print(f"success! Created {self.processor.file_name_no_comm} - {self.processor.file_name_include} - {self.processor.file_name_defines} - {self.processor.file_name_tokens}")
            self.defines_widget.clear() , self.out_file_widget.clear()
            self.addFileToListWidget(self.processor.file_name_defines,self.defines_widget)
            self.preprocess_action.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def preprocess_file(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        print("preprocess_file")
        self.prev_diff_butt.setEnabled(False)
        self.next_diff_butt.setEnabled(False)
        self.save_as_action.setEnabled(False)
        if self.processor.GenerateProcessed():
            print(f"success! Created {self.processor.file_name_out} - {self.processor.file_name_out_diff}")
            self.out_file_widget.clear()
            self.orig_file_widget.verticalScrollBar().setValue(0)
            self.addFileToListWidget(self.processor.file_name_out_diff,self.out_file_widget,bFormatEmpty=True)
            self.prev_diff_butt.setEnabled(True)
            self.next_diff_butt.setEnabled(True)
            self.save_as_action.setEnabled(True)
            self.update()
        QApplication.restoreOverrideCursor()

    def save_as(self):
        file_name = QFileDialog.getSaveFileName(self, 'Save file')
        if file_name[0]:
            with open(file_name[0], 'w') as f:
                # Qui puoi scrivere i dati nel file
                f.write(" ")
        pass

    def v_sync_scroll_list_widget(self, value):
        sender = self.sender()
        # print(f"sync_scroll_list_widget  {str(value)}")
        if sender == self.orig_file_widget.verticalScrollBar() and self.out_file_widget.count() != 0:
            self.out_file_widget.verticalScrollBar().setValue(value)

        if sender == self.out_file_widget.verticalScrollBar() and self.orig_file_widget.count() != 0:
            self.orig_file_widget.verticalScrollBar().setValue(value)

    def h_sync_scroll_list_widget(self, value):
        sender = self.sender()
        # print(f"sync_scroll_list_widget  {str(value)}")
        if sender == self.orig_file_widget.horizontalScrollBar() and self.out_file_widget.count() != 0:
            self.out_file_widget.horizontalScrollBar().setValue(value)

        if sender == self.out_file_widget.horizontalScrollBar() and self.orig_file_widget.count() != 0:
            self.orig_file_widget.horizontalScrollBar().setValue(value)

    def sync_selection_list(self):
        sender = self.sender()
        if sender == self.orig_file_widget and self.out_file_widget.count() != 0:
            self.out_file_widget.setCurrentRow(self.orig_file_widget.currentRow())

        if sender == self.out_file_widget and self.orig_file_widget.count() != 0:
            self.orig_file_widget.setCurrentRow(self.out_file_widget.currentRow())

    def update_defines(self):
        print("qui devo aggiornare i defines e tornare ad Analyze phase")
        pass
    
    def on_but_next_clicked(self):
        current_row = self.out_file_widget.currentRow()
        print(f"Next clicked: inizio a cercare dalla riga {current_row}")
        if current_row < 0:
            self.out_file_widget.setCurrentRow(0)
            current_row=0
            return
        for i in range(current_row, self.out_file_widget.count()):
            item = self.out_file_widget.item(i)
            if self.processor.EMPTY_LINE_TAG in item.text():
                print(f"Elemento trovato: {item.text()}")
                if i < self.out_file_widget.count():
                    self.out_file_widget.setCurrentRow(i+1)
                break

    def on_but_prev_clicked(self):
        current_row = self.out_file_widget.currentRow()
        print(f"Prev clicked: inizio a cercare dalla riga {current_row}")
        if current_row < 0:
            return
        for i in range(current_row - 1, -1, -1):
            item = self.out_file_widget.item(i)
            if self.processor.EMPTY_LINE_TAG in item.text():
                print(f"Elemento trovato: {item.text()}")
                if i > 0:
                    self.out_file_widget.setCurrentRow(i - 1)
                break


