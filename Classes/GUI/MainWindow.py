import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QLabel, QWidget, QHBoxLayout
import PyQt5.QtGui as QtGui
import pyqtgraph as pg
from Classes.Audio.AudioManager import AudioController, Action
from Classes.GUI.ProcessorWindow import ProcessorWindow
from matplotlib import cm
from Classes.Audio.SignalProcessor import SignalProcessor
import matplotlib.pyplot as plt

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    SIDEBAR_SIZE = 330

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wave Editor")
        self.setWindowIcon(QIcon('../Resources/Icons/icon.png'))
        self.setFixedSize(QSize(1200, 800))

        self.getFont()
        self.initBoldFont()
        self.initTimeFont()

        # Audio Controller
        self.audioManager = AudioController()

        rootWidget = self.createRootLayout()
        self.setCentralWidget(rootWidget)

    def createMainBox(self):
        mainBox = QVBoxLayout()
        mainBox.addWidget(self.plotWaveForm())
        mainBox.addWidget(self.plotSpectrogram())
        mainBox.setContentsMargins(5, 5, 5, 5)
        mainBox.setSpacing(5)
        widget = QWidget()
        widget.setStyleSheet("background-color: #FFFFFF")
        widget.setLayout(mainBox)
        return widget

    def processorWidget(self):
        button = QPushButton("Select Frame")
        button.clicked.connect(self.processorAction)
        return button

    def checkEnergyZCRWidget(self):
        button = QPushButton("Energy-ZCR 200 frames")
        button.clicked.connect(self.energyAndZCRAction)
        return button

    def checkAutoCorrAndCepstralWidget(self):
        button = QPushButton("AutoCorrelation and Cepstral 200 frames")
        button.clicked.connect(self.autoCorrAction)
        return button

    def energyAndZCRAction(self):
        values, energyList, zcrList = SignalProcessor.getEnergyAndZCRForFirst200Frames(self.audioManager.signalData)
        plt.figure()
        plt.plot(values, energyList)
        plt.title("Energy of 200 frames")
        plt.xlabel("Frame Number")
        plt.ylabel("Energy")
        plt.show()

        plt.figure()
        plt.plot(values, zcrList)
        plt.title("ZCR of 200 frames")
        plt.xlabel("Frame Number")
        plt.ylabel("ZCR")
        plt.show()

    def autoCorrAction(self):
        values, autoCorrList, cepstralList = SignalProcessor.getAutoCorrAndCepstralFor200Frames(self.audioManager.signalData)
        plt.figure()
        plt.plot(values, autoCorrList)
        plt.title("Pitch with AutoCorrelation for 200 frames")
        plt.xlabel("Frame Number")
        plt.ylabel("Pitch Value")
        plt.show()

        plt.figure()
        plt.plot(values, cepstralList)
        plt.title("Pitch with Cepstral for 200 frames")
        plt.xlabel("Frame Number")
        plt.ylabel("Pitch Value")
        plt.show()

    def processorAction(self):
        self.processorWindow = ProcessorWindow()
        self.processorWindow.show()
        self.processorWindow.setSignalData(self.audioManager.signalData, self.audioManager.p_frequency_sampling)

    def createSideBar(self):
        sidebar = QVBoxLayout()
        # Remove default paddings and margins
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setSpacing(0)

        # Set Widgets
        sidebar.addWidget(self.initZoomRangeLabel(), 1)
        sidebar.addWidget(self.initZoomFromLayout(), 1)
        sidebar.addWidget(self.initZoomToLayout(), 1)
        sidebar.addWidget(QWidget(), 1)
        sidebar.addWidget(QWidget(), 1)
        sidebar.addWidget(self.initFrequencySamplingLabel(), 1)
        sidebar.addWidget(self.getFrequencyLayout(), 1)
        sidebar.addWidget(self.initBitsPerSampleLabel(), 1)
        sidebar.addWidget(self.getBitsPerSampleLayout(), 1)
        sidebar.addWidget(self.processorWidget())
        sidebar.addWidget(self.checkEnergyZCRWidget())
        sidebar.addWidget(self.checkAutoCorrAndCepstralWidget())
        sidebar.addWidget(QWidget(), 1)
        sidebar.addWidget(self.setVoiceControllers(), 1)
        sidebar.addWidget(self.initTimeLayout(), 1)
        sidebar.addWidget(self.initLoadAndSaveLayout(), 1)

        # Create Widget
        sidebarWidget = QWidget()
        sidebarWidget.setLayout(sidebar)
        sidebarWidget.setFixedWidth(self.SIDEBAR_SIZE)
        return sidebarWidget

    def createRootLayout(self):
        root = QHBoxLayout()
        root.addWidget(self.createSideBar())
        root.addWidget(self.createMainBox())
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        main_widget = QWidget()
        main_widget.setLayout(root)
        return main_widget

    def initZoomRangeLabel(self):
        labelZoomRange = QLabel("Zoom range", self)
        labelZoomRange.move(100, 35)
        labelZoomRange.setFont(self.boldFont)
        labelZoomRange.setStyleSheet("height: 25px;")
        labelZoomRange.setAlignment(Qt.AlignCenter)
        return labelZoomRange

    def initZoomFromLayout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.initZoomFromLabel(), 1)
        layout.addWidget(self.initZoomFromET(), 3)
        layout.addWidget(self.initZoomButton(), 1)
        wig = QWidget()
        wig.setLayout(layout)
        return wig

    def initZoomToLayout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.initZoomToLabel(), 1)
        layout.addWidget(self.initZoomToET(), 3)
        layout.addWidget(self.initZoomResetButton(), 1)
        wig = QWidget()
        wig.setLayout(layout)
        return wig

    def initZoomFromLabel(self):
        labelZoomFrom = QLabel("From", self)
        labelZoomFrom.move(15, 75)
        labelZoomFrom.setStyleSheet("height: 25px;")
        labelZoomFrom.setAlignment(Qt.AlignCenter)
        return labelZoomFrom

    def initZoomFromET(self):
        self.zoomFromET = QLineEdit()
        self.zoomFromET.move(50, 75)
        self.zoomFromET.setStyleSheet("height: 25px;")
        return self.zoomFromET

    def initZoomButton(self):
        button = QPushButton("Zoom")
        button.move(150, 75)
        button.setStyleSheet("height: 25px;")
        button.clicked.connect(self.zoomAction)
        return button

    def initZoomToET(self):
        self.zoomToET = QLineEdit()
        self.zoomToET.move(50, 75)
        self.zoomToET.setStyleSheet("height: 25px;")
        return self.zoomToET

    def initZoomResetButton(self):
        button = QPushButton("Reset")
        button.move(150, 121)
        button.setStyleSheet("height: 25px;")
        button.clicked.connect(self.resetZoomAction)
        return button

    def initZoomToLabel(self):
        labelZoomTo = QLabel("To", self)
        labelZoomTo.move(15, 121)
        labelZoomTo.setStyleSheet("height: 25px;")
        labelZoomTo.setAlignment(Qt.AlignCenter)
        return labelZoomTo

    def initFrequencySamplingLabel(self):
        labelSamplingFrequency = QLabel("Sampling Frequency", self)
        labelSamplingFrequency.setFont(self.littleBoldFont)
        labelSamplingFrequency.adjustSize()
        labelSamplingFrequency.move(15, 192)
        labelSamplingFrequency.setMargin(10)
        labelSamplingFrequency.setFont(self.littleBoldFont)
        return labelSamplingFrequency

    def initBitsPerSampleLabel(self):
        labelBitsPerSample = QLabel("Bits per sample", self)
        labelBitsPerSample.setFont(self.littleBoldFont)
        labelBitsPerSample.adjustSize()
        labelBitsPerSample.setMargin(10)
        labelBitsPerSample.move(15, 275)
        return labelBitsPerSample

    def getFrequencyLayout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.initHzET())
        layout.addWidget(self.initHzLabel())
        wid = QWidget()
        wid.setLayout(layout)
        return wid

    def getBitsPerSampleLayout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.initBitsET())
        layout.addWidget(self.initBitsLabel())
        wid = QWidget()
        wid.setLayout(layout)
        return wid

    def initHzLabel(self):
        labelHz = QLabel("Hz", self)
        labelHz.move(120, 225)
        labelHz.setStyleSheet("height: 20px;")
        return labelHz

    def initBitsLabel(self):
        labelBits = QLabel("bits", self)
        labelBits.move(120, 310)
        labelBits.setStyleSheet("height: 20px;")
        return labelBits

    def initHzET(self):
        self.frequencySamplingET = QLineEdit()
        self.frequencySamplingET.move(50, 225)
        self.frequencySamplingET.setText(str(16000))
        self.frequencySamplingET.setStyleSheet("height: 20px;")
        return self.frequencySamplingET

    def initBitsET(self):
        self.bitsPerSampleET = QLineEdit()
        self.bitsPerSampleET.move(50, 310)
        self.bitsPerSampleET.setText(str(16))
        self.bitsPerSampleET.setStyleSheet("height: 20px;")
        return self.bitsPerSampleET

    def record(self):
        bitsPerSample = int(self.bitsPerSampleET.text())
        fs = int(self.frequencySamplingET.text())

        self.setBitsPerSample(bitsPerSample)

        if 8000 <= fs <= 32000:
            self.setFrequency(fs)
        else:
            self.setFrequency(16000)

        self.audioManager.action(Action.RECORD)

    def play(self):
        self.audioManager.action(Action.PLAY)

    def stop(self):
        self.audioManager.action(Action.STOP)

    def load(self):
        self.audioManager.fileName = self.fileNameET.text()
        duration, frequency_sampling, bitsPerSample = self.audioManager.action(Action.LOAD)
        self.totalTimeLabel.setText(duration)
        self.frequencySamplingET.setText(str(frequency_sampling))
        self.bitsPerSampleET.setText(str(bitsPerSample))

    def save(self):
        self.audioManager.fileName = self.fileNameET.text()
        self.audioManager.action(Action.SAVE)

    def resetZoomAction(self):
        self.zoomFromET.setText("")
        self.zoomToET.setText("")
        self.audioManager.action(Action.RESET)

    def zoomAction(self):
        # if (self.zoomFromET.text()).is() and (self.zoomToET.text()).isnumeric():
        start = float(self.zoomFromET.text())
        end = float(self.zoomToET.text())
        if start < end:
            self.audioManager.setZoomValues(start, end)
            self.audioManager.action(Action.ZOOM)

    def setVoiceControllers(self):
        recordIcon = self.getIconControllers("../Resources/Icons/ic_record_f.png")
        playIcon = self.getIconControllers("../Resources/Icons/ic_play_f.png")
        stopIcon = self.getIconControllers("../Resources/Icons/ic_stop_f.png")

        recordIcon.clicked.connect(self.record)
        playIcon.clicked.connect(self.play)
        stopIcon.clicked.connect(self.stop)

        layout = QHBoxLayout()
        layout.addWidget(QWidget(), 2)
        layout.addWidget(recordIcon, 2)
        layout.addWidget(playIcon, 2)
        layout.addWidget(stopIcon, 2)
        layout.addWidget(QWidget(), 2)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def getIconControllers(self, path):
        icon = QtGui.QIcon(path)
        button = QPushButton()
        button.setIcon(icon)
        button.setFlat(True)
        button.setIconSize(QSize(40, 40))
        return button

    def initTimeLayout(self):
        self.currentTimeLabel = self.getTimeLabel("00 : 00 : 00")
        separatorTimeLabel = self.getTimeLabel("/")
        self.totalTimeLabel = self.getTimeLabel("00 : 00 : 00")

        self.currentTimeLabel.setAlignment(Qt.AlignCenter)
        separatorTimeLabel.setAlignment(Qt.AlignCenter)
        self.totalTimeLabel.setAlignment(Qt.AlignCenter)

        self.audioManager.setCurrentTimeQLabel(self.currentTimeLabel)
        self.audioManager.setTotalTimeQLabel(self.totalTimeLabel)

        layout = QHBoxLayout()
        layout.addWidget(QWidget(), 2)
        layout.addWidget(self.currentTimeLabel, 2)
        layout.addWidget(separatorTimeLabel, 1)
        layout.addWidget(self.totalTimeLabel, 2)
        layout.addWidget(QWidget(), 2)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def initLoadAndSaveLayout(self):
        self.fileNameET = self.initFileNameET()
        saveButton = self.getIconControllers("../Resources/Icons/ic_download_large.png")
        loadButton = self.getIconControllers("../Resources/Icons/ic_upload_large.png")

        # Set Actions
        loadButton.clicked.connect(self.load)
        saveButton.clicked.connect(self.save)

        layout = QHBoxLayout()
        layout.addWidget(self.fileNameET)
        layout.addWidget(saveButton)
        layout.addWidget(loadButton)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def initFileNameET(self):
        edittext = QLineEdit()
        edittext.setPlaceholderText("File name")
        edittext.setStyleSheet("height: 40px;")
        return edittext

    def getTimeLabel(self, text):
        label = QLabel(text, self)
        label.setFont(self.timeFont)
        return label

    def getFont(self):
        self.littleBoldFont = QtGui.QFont('Segoe UI')
        self.littleBoldFont.setBold(True)

    def initBoldFont(self):
        self.boldFont = QtGui.QFont('Segoe UI')
        self.boldFont.setBold(True)
        self.boldFont.setPixelSize(16)

    def initTimeFont(self):
        self.timeFont = QtGui.QFont('Segoe UI')
        self.timeFont.setBold(True)
        self.timeFont.setPixelSize(14)

    def plotWaveForm(self):
        self.waveFormWidget = pg.PlotWidget()
        self.waveFormWidget.setBackground("#FFFFFF")

        self.audioManager.setWaveFormPlotWidget(self.waveFormWidget)

        return self.waveFormWidget

    def plotSpectrogram(self):
        self.spectrogramWidget = SpectrogramWidget()
        styles = {'color': 'black', 'font-size': '14px'}
        self.spectrogramWidget.showGrid(x=True, y=True)
        self.spectrogramWidget.setLabel('left', 'Frequency', units='Hz', **styles)
        self.spectrogramWidget.setLabel('bottom', 'Time', **styles)
        self.spectrogramWidget.setBackground("#FFFFFF")

        self.audioManager.setSpectrogramWidget(self.spectrogramWidget)
        return self.spectrogramWidget

    def setFrequency(self, fs):
        self.audioManager.p_frequency_sampling = fs

    def setBitsPerSample(self, bitsPerSample):

        # formats = [pyaudio.paInt8, pyaudio.paInt16, pyaudio.paInt24, pyaudio.paInt32]
        width = int(bitsPerSample / 8)
        self.audioManager.widthBytes = width
        self.audioManager.p_format = self.audioManager.pa.get_format_from_width(width, False)

class SpectrogramWidget(pg.PlotWidget):
    read_collected = QtCore.pyqtSignal(np.ndarray)
    counter = 0
    def __init__(self):
        super(SpectrogramWidget, self).__init__()
        self.chunk = 4096
        self.fs = 16000


    def build(self):
        self.img = pg.ImageItem()
        self.addItem(self.img)

        self.img_array = np.full((1000, int(self.chunk)), 255)
        # colormap
        colormap = cm.get_cmap("CMRmap")
        colormap._init()
        lut = (colormap._lut * 255).view(np.ndarray)

        # set colormap
        self.img.setLookupTable(lut)
        self.img.setLevels([-0, 75])

        # prepare window for later use
        self.win = np.hanning(self.chunk)
        self.show()

    def update(self, chunk):
        # normalized, windowed frequencies in data chunk
        spec = np.fft.rfft(chunk * self.win) / self.chunk
        print(len(chunk))
        # get magnitude
        psd = abs(spec)
        # convert to dB scale
        psd = 20 * np.log10(psd)
        psd = self.pad_or_truncate(psd, 4096)

        self.img_array[self.counter:] = psd
        self.counter += 1

        self.img.setImage(self.img_array, autoLevels=False)

    def clear(self):
        self.counter = 0

    def pad_or_truncate(self, startList, targetLen):
        otherList = np.full((targetLen - len(startList)), 255)
        return np.concatenate([startList, otherList])
