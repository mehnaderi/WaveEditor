import pyaudio
import wave
from threading import Thread
from pylab import *
from os.path import exists
from enum import Enum
import numpy as np
from scipy import signal
from scipy.io import wavfile
from Classes.GUI.ProcessorWindow import ProcessorWindow

class Status(Enum):
    # Define Status
    NONE = 1
    RECORDING = 2
    RECORD_PAUSED = 3
    READY = 4
    PLAY = 5
    PLAY_PAUSED = 6

class Action(Enum):
    # Action Names
    RECORD = 10
    LOAD = 11
    SAVE = 12
    STOP = 13
    PLAY = 14
    ZOOM = 15
    RESET = 16

class AudioController:
    # Audio Parameters
    p_chunk = 4096
    p_frequency_sampling = 16000
    CHANNELS = 1
    # p_format = pyaudio.paInt16
    p_format = pyaudio.paInt32

    # Coding variables (Others)
    fileName = ''
    chunkList = list()
    signalData = list()
    xWave = list(range(-5, 0))
    yWave = list(zeros(5))
    totalTimeValue = 0
    zoomedData = list()
    totalTimeFloatCounter = 0.0
    currentTimeFloatCounter = 0.0
    totalTimeString = ""
    currentTimeValue = 0
    currentTimeString = "00:00:00"
    currentPlayCounter = 0
    current = float(0)
    zoomFrom = 0
    zoomTo = 1

    def __init__(self):
        self.status = Status.NONE
        self.pa = pyaudio.PyAudio()

    def clearFrames(self):
        self.chunkList = list()
        self.signalData = list()
        self.xWave = list(range(-2, 0))
        self.yWave = list(zeros(2))
        self.current = float(0)
        self.totalTimeFloatCounter = float(0)
        self.updateTotalTime(0)

    def action(self, actionName):
        # Load New Wav File :
        if actionName == Action.LOAD and self.checkFileExists():
            self.status = Status.READY
            return self.load()

        elif actionName == Action.ZOOM:
            self.zoomAction()
        elif actionName == Action.RESET:
            self.zoomFrom = 0
            self.zoomTo = 1
            self.resetZoomAction()

        # Record For First Action
        elif self.status == Status.NONE and actionName == Action.RECORD:
            self.clearFrames()
            self.status = Status.RECORDING
            self.record()

        # Other Actions
        elif self.status == Status.READY:
            if actionName == Action.RECORD:
                self.status = Status.RECORDING
                self.clearFrames()
                self.record()
            elif actionName == Action.PLAY:
                self.currentPlayCounter = 0
                self.status = Status.PLAY
                self.play()
            elif actionName == Action.SAVE:
                self.save()


        elif self.status == Status.PLAY_PAUSED:
            if actionName == Action.RECORD:
                self.status = Status.RECORDING
                self.clearFrames()
                self.record()
            elif actionName == Action.PLAY:
                self.status = Status.PLAY
                self.play()
            elif actionName == Action.STOP:
                self.currentPlayCounter = 0
                self.status = Status.READY
                self.stop()
            elif actionName == Action.SAVE:
                self.save()


        elif self.status == Status.RECORD_PAUSED:
            if actionName == Action.RECORD:
                # Continue recording
                self.status = Status.RECORDING
                self.record()
            elif actionName == Action.PLAY:
                self.currentPlayCounter = 0
                self.status = Status.PLAY
                self.play()
            elif actionName == Action.STOP:
                self.currentPlayCounter = 0
                self.status = Status.READY
                self.stop()
            elif actionName == Action.SAVE:
                self.save()

        elif self.status == Status.PLAY:
            if actionName == Action.RECORD:
                self.status = Status.RECORDING
                self.clearFrames()
                self.record()
            elif actionName == Action.PLAY:
                self.status = Status.PLAY_PAUSED
            elif actionName == Action.STOP:
                self.currentPlayCounter = 0
                self.status = Status.READY
                self.stop()
            elif actionName == Action.SAVE:
                self.save()


        elif self.status == Status.RECORDING:
            if actionName == Action.RECORD:
                self.status = Status.NONE
                while self.recordingThread.is_alive():
                    pass
                self.clearFrames()
                self.status = Status.RECORDING
                self.record()
            elif actionName == Action.PLAY:
                self.status = Status.RECORD_PAUSED
            elif actionName == Action.STOP:
                self.currentPlayCounter = 0
                self.status = Status.READY
                self.stop()

    def setFileName(self, fileName):
        self.fileName = fileName

    def getFileName(self):
        return self.fileName

    def checkFileExists(self):
        return exists(self.makeFileName())

    def makeFileName(self):
        return f"./{self.fileName}.wav"

    def setCurrentTimeQLabel(self, currentLabel):
        self.currentTimeQLabel = currentLabel

    def setTotalTimeQLabel(self, totalLabel):
        self.totalTimeQLabel = totalLabel

    def setWaveFormPlotWidget(self, plotWidget):
        self.waveformWidget = plotWidget
        self.initWaveForm()

    def setSpectrogramWidget(self, spectrogramWidget):
        self.spectrogramWidget = spectrogramWidget

    def setZoomValues(self, fromValue, toValue):
        self.zoomFrom = fromValue
        self.zoomTo = toValue

    @staticmethod
    def convertSecondsToString(seconds):
        h = seconds // 3600
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60
        return '{:02d} : {:02d} : {:02d}'.format(h, m, s)

    def record(self):
        # Start recording in thread
        self.recordingThread = Thread(target=self.recordThread, args=())
        self.recordingThread.daemon = True
        self.recordingThread.start()

    def recordThread(self):
        chunks_in_second = (self.p_frequency_sampling / self.p_chunk)
        # Record
        self.stream = self.pa.open(
            format=self.p_format,
            channels=self.CHANNELS,
            rate=self.p_frequency_sampling,
            input=True,
            frames_per_buffer=self.p_chunk
        )
        self.updateCurrentTime(0)

        # Save frames and update UI
        while self.status == Status.RECORDING:
            # Read frames
            data = self.stream.read(self.p_chunk)
            self.chunkList.append(data)
            self.signalData.extend(data)
            if self.widthBytes == 1:
                npData = np.frombuffer(data, dtype=np.int8)
                self.updateWaveForm(npData)
            if self.widthBytes == 2:
                npData = np.frombuffer(data, dtype=np.int16)
                self.updateWaveForm(npData)
            if self.widthBytes == 4:
                npData = np.frombuffer(data, dtype=np.int32)
                self.updateWaveForm(npData)
            # self.updateSpectrogram(data)

            # Update time tracker and GUI updater
            self.totalTimeFloatCounter += 1
            # Update duration in GUI
            self.updateTotalTime(int(self.totalTimeFloatCounter / chunks_in_second))

    def play(self):
        self.playingThread = Thread(target=self.playThread, args=())
        self.playingThread.daemon = True
        self.playingThread.start()

    def playThread(self):
        chunks_in_second = self.p_frequency_sampling / self.p_chunk
        self.stream = self.pa.open(
            format=self.p_format,
            channels=self.CHANNELS,
            rate=self.p_frequency_sampling,
            output=True)

        # Read data in chunks
        data = self.chunkList[self.currentPlayCounter]
        self.currentPlayCounter += 1
        while self.status == Status.PLAY and data != b'':

            self.stream.write(data)
            if self.currentPlayCounter >= len(self.chunkList):
                break
            data = self.chunkList[self.currentPlayCounter]
            self.currentPlayCounter += 1

            # Update time tracker and GUI updater
            self.currentTimeFloatCounter += 1
            self.updateCurrentTime(int(self.currentTimeFloatCounter / chunks_in_second))

        if data == b'' or self.currentPlayCounter == len(self.chunkList):
            self.action(Action.STOP)
            self.updateCurrentTime(0)

    def updateCurrentTime(self, seconds):
        self.currentTimeValue = seconds
        self.currentTimeString = self.convertSecondsToString(self.currentTimeValue)
        self.currentTimeQLabel.setText(self.currentTimeString)

    def updateTotalTime(self, seconds):
        self.totalTimeValue = seconds
        self.totalTimeString = self.convertSecondsToString(self.totalTimeValue)
        self.totalTimeQLabel.setText(self.totalTimeString)

    def stop(self):
        self.updateCurrentTime(0)

    def save(self):
        obj = wave.open(self.makeFileName(), 'w')
        obj.setnchannels(self.CHANNELS)
        obj.setsampwidth(self.pa.get_sample_size(self.p_format))
        obj.setframerate(self.p_frequency_sampling)
        obj.writeframes(b''.join(self.chunkList))
        obj.close()

    def zoomAction(self):
        xZoom = list()
        yZoom = list()

        for i in range(len(self.xWave)):
            if i >= len(self.xWave) or self.xWave[i] > self.zoomTo:
                break
            if i < len(self.xWave) and self.xWave[i] >= self.zoomFrom:
                xZoom.append(self.xWave[i])
                yZoom.append(self.yWave[i])

        self.data_line.setData(xZoom, yZoom)  # Update the data.

    def resetZoomAction(self):
        self.data_line.setData(self.xWave, self.yWave)  # Update the data.

    def load(self):
        # Init audio stream
        self.p_frequency_sampling, signalData = wavfile.read(self.makeFileName())
        wf = wave.open(self.makeFileName(), 'r')

        self.widthBytes = wf.getsampwidth()
        self.p_format = self.pa.get_format_from_width(wf.getsampwidth(), False)

        self.CHANNELS = wf.getnchannels()

        self.stream = self.pa.open(
            format=self.p_format,
            channels=self.CHANNELS,
            rate=self.p_frequency_sampling,
            output=True)

        # Convert to frames
        # Clear Frames
        self.clearFrames()
        # Read first chunk
        data = wf.readframes(self.p_chunk)
        # Update total time
        self.totalTimeValue = int(wf.getnframes() / float(self.p_frequency_sampling))
        self.updateTotalTime(self.totalTimeValue)

        tempBuffer = list()
        self.signalData.extend(signalData)
        while data != b'':
            self.chunkList.append(data)
            data = wf.readframes(self.p_chunk)
            if self.widthBytes == 1:
                tempBuffer.extend(np.frombuffer(data, dtype=np.int8))
            if self.widthBytes == 2:
                tempBuffer.extend(np.frombuffer(data, dtype=np.int16))
            if self.widthBytes == 3:
                tempBuffer.extend(np.frombuffer(data, dtype=np.int32))

        # plot_b.specgram(tempBuffer, NFFT=1024, Fs=self.p_frequency_sampling, noverlap=900)
        # plot_b.set_xlabel('Time')
        # plot_b.set_ylabel('Frequency')
        # plt.show()

        self.updateWaveForm(tempBuffer)
        return self.totalTimeString, self.p_frequency_sampling, self.widthBytes * 8

    def initWaveForm(self):

        styles = {'color': 'black', 'font-size': '14px'}
        self.waveformWidget.showGrid(x=True, y=True)
        self.waveformWidget.setLabel('left', 'Amplitude', **styles)
        self.waveformWidget.setLabel('bottom', 'Time (s)', **styles)

        self.data_line = self.waveformWidget.plot(self.xWave, self.yWave, pen={'color': '#04B4AE', 'width': 0.5})

    def updateWaveForm(self, y):

        timeSteps = float(1) / self.p_frequency_sampling
        # Update X-axis values
        for i in range(len(y)):
            self.xWave.append(self.current)
            self.current += timeSteps

        # Update Y-axis values
        self.yWave.extend(y)

        self.data_line.setData(self.xWave, self.yWave)  # Update the data.

    def initSpectrogram(self):
        styles = {'color': 'black', 'font-size': '12px'}
        # self.waveFormWidget.showGrid(x=True, y=True)
        self.spectrogramWidget.setLabel('left', 'Amplitude', **styles)
        self.spectrogramWidget.setLabel('bottom', 'Time (s)', **styles)

        self.s = self.spectrogramWidget.specgram(self.yWave, NFFT=1024, Fs=self.p_frequency_sampling, noverlap=900)

    # def updateSpectrogram(self, chunk):
    #     self.spectrogramWidget
    #
    #     plot_b = plt.subplot(212)
    #     plot_b.specgram(tempBuffer, NFFT=1024, Fs=self.p_frequency_sampling, noverlap=900)
    #     plot_b.set_xlabel('Time')
    #     plot_b.set_ylabel('Frequency')
    #     plt.show()
    #     # self.spectrogramWidget.update(chunk)
    #     pass

    def terminate(self):
        self.stream.close()
        self.pa.terminate()

    def selectFrame(self, frameNo, N, M):
        """
        *    frameNo : number of frame (starting with 0)
        *    N : Frame length (ms)
        *    M : Frame shift (ms)
        """

        # Convert millisecond to number of samples
        N = int(self.p_frequency_sampling * N / 1000)
        M = int(self.p_frequency_sampling * M / 1000)
        # define start point
        startPoint = frameNo * M

        # Create new frame
        frame = np.zeros(N)
        # Fill frame
        for i in range(N):
            if i >= len(self.signalData):
                break
            frame[i] = self.signalData[startPoint + i]

        return frame

    def showFrame(self, frameNo, N, M):


        frame = self.selectFrame(frameNo, N, M)
        # Convert millisecond to number of samples
        N_Number = int(self.p_frequency_sampling * N / 1000)
        M_Number = int(self.p_frequency_sampling * M / 1000)

        x = range(0, N_Number)
        y = frame.tolist()

        # Update Y-axis values
        # self.yWave.extend(y)

        self.data_line.setData(x, y)  # Update the data.



