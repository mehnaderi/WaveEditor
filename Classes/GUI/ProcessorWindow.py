from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QCheckBox, QRadioButton
import pyqtgraph as pg
from PyQt5.uic.Compiler.qtproxies import QtCore

from Classes.Audio.SignalProcessor import SignalProcessor as processor
from Classes.Audio.SignalProcessor import Window
import numpy as np

class ProcessorWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Process Frame")
        self.setWindowIcon(QIcon('../Resources/Icons/icon.png'))
        self.setFixedSize(QSize(900, 600))
        self.isFirstPlot = True

        self.signalData = list()
        self.fs = 16000

        root = QHBoxLayout()
        root.addWidget(self.createSideBar())
        root.addWidget(self.createMainBox())
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)
        self.isPreEmphasised = False


    def createSideBar(self):
        mainBox = QVBoxLayout()
        mainBox.setContentsMargins(5, 5, 5, 5)
        mainBox.setSpacing(5)
        mainBox.addWidget(QLabel("Frame Number"), 1)
        mainBox.addWidget(self.initFrameNumberET(), 1)
        mainBox.addWidget(QLabel("Frame Length"), 1)
        mainBox.addWidget(self.initFrameLengthET(), 1)
        mainBox.addWidget(QLabel("Frame Shifting"), 1)
        mainBox.addWidget(self.initFrameShiftET(), 1)
        mainBox.addWidget(self.initCoefficientLabel(), 2)
        mainBox.addWidget(self.initPreEmphasisCheckBox(), 2)
        mainBox.addWidget(self.initWindowingRadioButton(), 0.8)
        mainBox.addWidget(self.initShowFrameButton(), 2)
        widget = QWidget()
        # widget.setStyleSheet("background-color: #C9C9C9")
        widget.setLayout(mainBox)
        return widget

    def createMainBox(self):
        mainBox = QVBoxLayout()
        mainBox.addWidget(self.plotWaveForm())
        mainBox.addWidget(self.plotSpectrum())
        mainBox.setContentsMargins(5, 5, 5, 5)
        mainBox.setSpacing(5)
        widget = QWidget()
        widget.setStyleSheet("background-color: #FFFFFF")
        widget.setLayout(mainBox)
        return widget

    def initCoefficientLabel(self):
        self.coefficientLabel = QLabel("")
        return self.coefficientLabel

    def initPreEmphasisCheckBox(self):
        self.emphasisCheckBox = QCheckBox("Apply pre-emphasis")
        self.emphasisCheckBox.stateChanged.connect(self.preEmphasisAction)
        return self.emphasisCheckBox

    def initWindowingRadioButton(self):
        self.windowRectangularRadioButton = QRadioButton("Rectangular")

        self.windowHammingRadioButton = QRadioButton("Hamming")

        self.windowNoneRadioButton = QRadioButton("None")
        self.windowNoneRadioButton.setChecked(True)

        windowingLabel = QLabel("Windowing type")

        layout = QHBoxLayout()
        layout.addWidget(self.windowNoneRadioButton, 1)
        layout.addWidget(self.windowRectangularRadioButton, 1)
        layout.addWidget(self.windowHammingRadioButton, 1)

        superLayout = QVBoxLayout()
        superLayout.addWidget(windowingLabel, 1)
        superLayout.addLayout(layout, 1)

        widget = QWidget()
        widget.setLayout(superLayout)
        return widget




    def preEmphasisAction(self):
        self.isPreEmphasised = self.emphasisCheckBox.isChecked()


    def initShowFrameButton(self):
        button = QPushButton("Show frame")
        button.clicked.connect(self.showFrameAction)
        return button

    def showFrameAction(self):
        N = int(self.frameLengthET.text())
        M = int(self.frameShiftET.text())

        frameNo = int(self.frameNumberET.text())
        frame = processor.selectFrame(self.signalData, frameNo, N, M, self.fs)

        # Get x values
        timeSteps = float(1000) / self.fs
        N_Number = int(self.fs * N / 1000)
        M_Number = int(self.fs * M / 1000)
        x = list()

        startTime = frameNo * M_Number * 1000 / self.fs
        for i in range(N_Number):
            x.append(float(startTime + timeSteps * i)/1000)

        # Compute Coefficient for pre-emphasis
        coeff = processor.computePreEmphasisCoefficient(frame)
        self.coefficientLabel.setText(f"Coefficient : {coeff}")


        # Windowing
        if self.windowNoneRadioButton.isChecked():
            pass
        elif self.windowRectangularRadioButton.isChecked():
            frame = processor.windowing(frame, Window.RECTANGULAR)
        elif self.windowHammingRadioButton.isChecked():
            frame = processor.windowing(frame, Window.HAMMING)


        # Get y values
        # Apply Pre-emphasis
        if self.isPreEmphasised:
            frame = processor.PreEmphasis(frame)
        else:
            frame = frame.tolist()

        # Plot spectrum
        ySpectrum = processor.computeMagnitudeOfSpectrum(frame)
        xSpectrum = range(len(ySpectrum))


        # Plot data
        if self.isFirstPlot:
            self.data_line = self.waveformWidget.plot(x, frame, pen={'color': '#04B4AE', 'width': 1})
            self.spectrum_line = self.spectrumWidget.plot(xSpectrum, ySpectrum, pen={'color': '#04B4AE', 'width': 1})
            self.isFirstPlot = False
        else:
            self.data_line.setData(x, frame)
            self.spectrum_line.setData(xSpectrum, ySpectrum)


    def plotWaveForm(self):
        self.waveformWidget = pg.PlotWidget()
        self.waveformWidget.setBackground("#FFFFFF")
        styles = {'color': 'black', 'font-size': '12px'}
        self.waveformWidget.showGrid(x=True, y=True)
        self.waveformWidget.setLabel('left', 'Amplitude', **styles)
        self.waveformWidget.setLabel('bottom', 'Time (s)', **styles)
        return self.waveformWidget

    def plotSpectrum(self):
        self.spectrumWidget = pg.PlotWidget()
        self.spectrumWidget.setBackground("#FFFFFF")
        styles = {'color': 'black', 'font-size': '12px'}
        self.spectrumWidget.showGrid(x=True, y=True)
        self.spectrumWidget.setLabel('left', 'Magnitude (dB)', **styles)
        self.spectrumWidget.setLabel('bottom', 'Frequency (Hz)', **styles)
        return self.spectrumWidget

    def initFrameNumberET(self):
        self.frameNumberET = QLineEdit()
        self.frameNumberET.setStyleSheet("height: 25px;")
        self.frameNumberET.setPlaceholderText("Frame Number")
        return self.frameNumberET

    def initFrameLengthET(self):
        self.frameLengthET = QLineEdit()
        self.frameLengthET.setStyleSheet("height: 25px;")
        self.frameLengthET.setPlaceholderText("Frame Length (N)")
        return self.frameLengthET

    def initFrameShiftET(self):
        self.frameShiftET = QLineEdit()
        self.frameShiftET.setStyleSheet("height: 25px;")
        self.frameShiftET.setPlaceholderText("Frame Shift (M)")
        return self.frameShiftET


    def setSignalData(self, signalData, fs):
        self.signalData = signalData
        self.fs = fs









