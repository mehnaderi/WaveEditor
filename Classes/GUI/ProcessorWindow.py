from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QCheckBox, QRadioButton
import pyqtgraph as pg
import scipy
import numpy as np
from Classes.Audio.SignalProcessor import SignalProcessor as processor
from Classes.Audio.SignalProcessor import Window

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
        self.isFirstWaveformPlot = True
        self.isFirstSpectrumPlot = True

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
        mainBox.addWidget(QWidget(), 3)
        mainBox.addWidget(self.initCoefficientLabel(), 2)
        mainBox.addWidget(self.initFrameEnergyLabel(), 2)
        mainBox.addWidget(self.initFrameZCRLabel(), 2)
        mainBox.addWidget(QWidget(), 2)
        mainBox.addWidget(self.initPreEmphasisCheckBox(), 2)
        mainBox.addWidget(self.initWindowingRadioButton(), 0.8)
        mainBox.addWidget(self.initShowFrameButton(), 2)
        mainBox.addWidget(self.initAutoCorrelationButton(), 2)
        mainBox.addWidget(self.initAMDFButton(), 2)
        mainBox.addWidget(self.initShowFormantsButton(), 2)
        mainBox.addWidget(self.initShowCepstralsButton(), 2)
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

    def initFrameEnergyLabel(self):
        self.energyLabel = QLabel("")
        return self.energyLabel

    def initFrameZCRLabel(self):
        self.zcrLabel = QLabel("")
        return self.zcrLabel

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

    def initAutoCorrelationButton(self):
        button = QPushButton("AutoCorrelation")
        button.clicked.connect(self.autoCorrelationButtonClicked)
        return button

    def initAMDFButton(self):
        button = QPushButton("AMDF")
        button.clicked.connect(self.amdfButtonClicked)
        return button

    def initShowFormantsButton(self):
        button = QPushButton("Show Formants")
        button.clicked.connect(self.showFormantsButtonClicked)
        return button

    def initShowCepstralsButton(self):
        button = QPushButton("Show Cepstrals")
        button.clicked.connect(self.showCepstralsButtonClicked)
        return button

    def autoCorrelationButtonClicked(self):
        # Edit labels
        self.spectrumWidget.hide()
        self.waveformWidget.show()
        styles = {'color': 'black', 'font-size': '12px'}
        self.spectrumWidget.setLabel('top', '', **styles)
        styles = {'color': 'black', 'font-size': '12px'}
        self.waveformWidget.setLabel('left', '', **styles)
        self.waveformWidget.setLabel('bottom', 'Autocorrelation', **styles)

        N = int(self.frameLengthET.text())
        M = int(self.frameShiftET.text())

        frameNo = int(self.frameNumberET.text())
        frame = processor.selectFrame(self.signalData, frameNo, N, M, self.fs)
        autoCorr = processor.getCORR(frame)

        peaks = scipy.signal.find_peaks(autoCorr, height=0.01, distance=300)
        if len(peaks[0]) != 0:
            F_pitch = self.fs / peaks[0][0]
            self.waveformWidget.setLabel('top', f'Pitch Frequency with AutoCorrelation = {F_pitch:.0f} Hz', **styles)
        else:
            self.waveformWidget.setLabel('top', '', **styles)


        # Get x values
        N_Number = int(self.fs * N / 1000)

        x = range(N_Number)

        # Plot data
        if self.isFirstWaveformPlot:
            self.data_line = self.waveformWidget.plot(x, autoCorr, pen={'color': '#04B4AE', 'width': 1})
            # self.spectrum_line = self.spectrumWidget.plot(xSpectrum, ySpectrum, pen={'color': '#04B4AE', 'width': 1})
            self.isFirstWaveformPlot = False
        else:
            self.data_line.setData(x, autoCorr)
            # self.spectrum_line.setData(xSpectrum, ySpectrum)

    def amdfButtonClicked(self):
        # Edit labels
        self.spectrumWidget.hide()
        self.waveformWidget.show()
        styles = {'color': 'black', 'font-size': '12px'}
        self.spectrumWidget.setLabel('top', '', **styles)
        styles = {'color': 'black', 'font-size': '12px'}
        self.waveformWidget.setLabel('left', '', **styles)
        self.waveformWidget.setLabel('bottom', 'AMDF', **styles)

        N = int(self.frameLengthET.text())
        M = int(self.frameShiftET.text())

        frameNo = int(self.frameNumberET.text())
        frame = processor.selectFrame(self.signalData, frameNo, N, M, self.fs)
        amdf = processor.getAMDF(frame)

        # peaks = scipy.signal.find_peaks(autoCorr, height=50000000)
        valleys = scipy.signal.find_peaks(-amdf, height=-50000000, distance=300)

        if len(valleys[0]) != 0:
            F_pitch = self.fs / valleys[0][0]
            self.waveformWidget.setLabel('top', f'Pitch Frequency with AMDF = {F_pitch:.0f} Hz', **styles)
        else:
            self.waveformWidget.setLabel('top', '', **styles)
        # Get x values
        N_Number = int(self.fs * N / 1000)

        x = range(N_Number)

        # Plot data
        if self.isFirstWaveformPlot:
            self.data_line = self.waveformWidget.plot(x, amdf, pen={'color': '#04B4AE', 'width': 1})
            # self.spectrum_line = self.spectrumWidget.plot(xSpectrum, ySpectrum, pen={'color': '#04B4AE', 'width': 1})
            self.isFirstWaveformPlot = False
        else:
            self.data_line.setData(x, amdf)
            # self.spectrum_line.setData(xSpectrum, ySpectrum)

    def showFormantsButtonClicked(self):
        self.waveformWidget.hide()
        self.spectrumWidget.show()
        styles = {'color': 'black', 'font-size': '12px'}
        self.spectrumWidget.setLabel('top', '', **styles)
        self.spectrumWidget.setLabel('left', 'Magnitude (dB)', **styles)
        self.spectrumWidget.setLabel('bottom', 'Frequency (Hz)', **styles)
        N = int(self.frameLengthET.text())
        M = int(self.frameShiftET.text())
        frameNo = int(self.frameNumberET.text())
        frame = processor.selectFrame(self.signalData, frameNo, N, M, self.fs)

        formants, xSpectrum, ySpectrum = processor.getFormant(frame, self.fs)

        xData = []
        yData = []
        for i in formants[0]:
            xData.append(xSpectrum[i])
            yData.append(ySpectrum[i])

        # Create the scatter plot and add it to the view
        self.spectrumFormantsScatter.clear()
        self.spectrumFormantsScatter.setData(xData, yData)

        # Plot data
        if self.isFirstSpectrumPlot:
            self.spectrum_line = self.spectrumWidget.plot(xSpectrum, ySpectrum, pen={'color': '#04B4AE', 'width': 1})
            self.isFirstSpectrumPlot = False
        else:
            self.spectrum_line.setData(xSpectrum, ySpectrum)

    def showCepstralsButtonClicked(self):
        self.waveformWidget.hide()
        self.spectrumWidget.show()
        N = int(self.frameLengthET.text())
        M = int(self.frameShiftET.text())
        frameNo = int(self.frameNumberET.text())
        frame = processor.selectFrame(self.signalData, frameNo, N, M, self.fs)

        xSpectrum, ySpectrum = processor.getCEPSTRAL(frame)

        styles = {'color': 'black', 'font-size': '12px'}
        peaks = scipy.signal.find_peaks(ySpectrum, distance=30, height=0.06)
        if len(peaks[0]) != 0:
            if peaks[0][0] > 20:
                F_pitch = self.fs / (peaks[0][0]*2)
                self.spectrumWidget.setLabel('top', f'Pitch Frequency with Cepstral Analysis = {F_pitch:.0f} Hz',
                                             **styles)
            elif len(peaks[0]) > 1:
                F_pitch = self.fs / (peaks[0][1]*2)
                self.spectrumWidget.setLabel('top', f'Pitch Frequency with Cepstral Analysis = {F_pitch:.0f} Hz',
                                             **styles)
            else:
                self.spectrumWidget.setLabel('top', '', **styles)
        else:
            self.spectrumWidget.setLabel('top', '', **styles)

        self.spectrumFormantsScatter.clear()
        self.spectrumWidget.setLabel('left', 'Cepstral value', **styles)
        self.spectrumWidget.setLabel('bottom', 'Quefrency (Samples)', **styles)


        # Plot data
        if self.isFirstSpectrumPlot:
            self.spectrum_line = self.spectrumWidget.plot(xSpectrum, ySpectrum, pen={'color': '#04B4AE', 'width': 1})
            self.isFirstSpectrumPlot = False
        else:
            self.spectrum_line.setData(xSpectrum, ySpectrum)


    def showFrameAction(self):
        self.spectrumWidget.show()
        self.waveformWidget.show()
        styles = {'color': 'black', 'font-size': '12px'}
        self.spectrumWidget.setLabel('top', '', **styles)
        self.spectrumWidget.setLabel('left', 'Magnitude (dB)', **styles)
        self.spectrumWidget.setLabel('bottom', 'Frequency (Hz)', **styles)
        styles = {'color': 'black', 'font-size': '12px'}
        self.waveformWidget.setLabel('left', 'Amplitude', **styles)
        self.waveformWidget.setLabel('bottom', 'Time (s)', **styles)
        self.waveformWidget.setLabel('top', '', **styles)

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

        # Compute Coefficient for pre-emphasis and show it
        coeff = processor.computePreEmphasisCoefficient(frame)
        self.coefficientLabel.setText(f"Coefficient : {coeff:.3f}")

        # Compute Energy and ZCR: (and show them)
        energy = processor.getEnergy(frame)
        zcr = processor.getZCR(frame)
        self.energyLabel.setText(f"Energy : {energy:.3f}")
        self.zcrLabel.setText(f"ZCR : {zcr:.3f}")



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
            frame = processor.preEmphasis(frame)
        else:
            frame = frame.tolist()

        # Plot spectrum
        ySpectrum = processor.computeMagnitudeOfSpectrum(frame)
        # Generate x values
        xSpectrum = [*range(0, int(self.fs/2), int((self.fs/2)/len(ySpectrum)))]
        while len(xSpectrum) > len(ySpectrum):
            xSpectrum.pop()

        self.spectrumFormantsScatter.clear()
        # Plot data
        if self.isFirstSpectrumPlot:
            self.spectrum_line = self.spectrumWidget.plot(xSpectrum, ySpectrum, pen={'color': '#04B4AE', 'width': 1})
            self.isFirstSpectrumPlot = False
        else:
            self.spectrum_line.setData(xSpectrum, ySpectrum)

        if self.isFirstWaveformPlot:
            self.data_line = self.waveformWidget.plot(x, frame, pen={'color': '#04B4AE', 'width': 1})
            self.isFirstWaveformPlot = False
        else:
            self.data_line.setData(x, frame)


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
        self.spectrumFormantsScatter = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color='r'), symbol='o', size=3)
        self.spectrumWidget.addItem(self.spectrumFormantsScatter)
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









