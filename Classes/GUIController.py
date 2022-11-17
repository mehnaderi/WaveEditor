import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
from AudioController2 import AudioController
try:
    import _thread as thread  # using Python 3
except ImportError:
    import thread  # falls back to import from Python 2


class GUIController:
    def __init__(self, windowName, windowSize, windowBg):
        # Init window
        self.window = tk.Tk(className=windowName)
        self.window.geometry(windowSize)
        self.window.configure(bg=windowBg)
        self.window.resizable(False, False)

        # Init some controllers
        self.isRecording = False
        self.window.durationValue = 0
        self.window.samplingFreq = 16000
        self.window.bitsPerSample = 8

        # Init buttons
        self.initAllViews()

        self.audioController = AudioController(self.window)


    def initAllViews(self):
        self.initSidebar()
        pass
        # self.initRecordButton()
        # self.initPauseButton()
        # self.initResumeButton()
        # self.initStopButton()
        # self.initSaveButton()
        # self.initLoadButton()
        # self.initDurationLabel()
        # self.initFileNameEditText()
        # self.initSamplingFrequencyEditText()
        # self.initBitsPerSampleEditText()
        # self.initSamplingFrequencyLabel()
        # self.initBitsPerSampleLabel()
        # self.initZoomFromLabel()
        # self.initZoomToLabel()
        # self.initZoomFromEditText()
        # self.initZoomToEditText()
        # self.initZoomButton()
        # self.initZoomResetButton()

        # separator = tk.Frame(self.window, bg="#D1B000", height=1, bd=0)
        # separator.place(relx=0, rely=0.65, relwidth=1, relheight=1 / float(600))
        #
        # separator2 = tk.Frame(self.window, bg="#D1B000", bd=0)
        # separator2.place(relx=0.6, rely=0.65, relwidth=1 / float(900), relheight=1)


    def initSidebar(self):
        Frame(self.window, bg="#D9D9D9", width=250, height=600, relief=FLAT, ).grid()
        self.initInputFileNameEditText()

    def initInputFileNameEditText(self):

        self.window.load_image = self.get_tk_image("Resources/Icons/ic_upload_f.png")
        # self.window.loadButton = Button(self.window, image=self.window.load_image, compound=CENTER, borderwidth=0,
        #                                 command=self.loadButtonAction)
        # self.window.loadButton.configure(bg="#FFFFFF")
        # self.window.loadButton.place(x=70, y=520)

        self.window.fileNameET = tk.Entry(self.window,  width=12, justify='left', font=("Calibri"))
        # self.window.fileNameET.configure(bg="#FEFEFE")
        # self.window.fileNameET.configure()
        self.window.fileNameET.configure(alpha=0.5)
        self.window.fileNameET.place(x=20, y=490)
        self.window.fileNameET.insert(0, "voice1.wav")


    def initRecordButton(self):
        self.window.record_img = self.get_tk_image("Resources/Icons/ic_record_f.png")
        self.window.recordButton = Button(self.window, image=self.window.record_img, compound=CENTER, borderwidth=0,
                                          command=self.recordButtonAction)
        self.window.recordButton.configure(bg="#FFFFFF")
        self.window.recordButton.place(x=200, y=520)

    def initResumeButton(self):
        self.window.resume_image = self.get_tk_image("Resources/Icons/ic_play_f.png")
        self.window.pauseButton = Button(self.window, image=self.window.resume_image, compound=CENTER, borderwidth=0,
                                         command=self.resumeButtonAction)
        self.window.pauseButton.configure(bg="#FFFFFF")
        self.window.pauseButton.place(x=250, y=520)

    def initPauseButton(self):
        self.window.pause_image = self.get_tk_image("Resources/Icons/ic_pause_f.png")
        self.window.pauseButton = Button(self.window, image=self.window.pause_image, compound=CENTER, borderwidth=0,
                                         command=self.pauseButtonAction)
        self.window.pauseButton.configure(bg="#FFFFFF")
        self.window.pauseButton.place(x=300, y=520)


    def initStopButton(self):
        self.window.stop_image = self.get_tk_image("Resources/Icons/ic_stop_f.png")
        self.window.stopButton = Button(self.window, image=self.window.stop_image, compound=CENTER, borderwidth=0,
                                        command=self.stopButtonAction)
        self.window.stopButton.configure(bg="#FFFFFF")
        self.window.stopButton.place(x=350, y=520)

    def initSaveButton(self):
        # Save button
        self.window.save_image = self.get_tk_image("Resources/Icons/ic_download_f.png")
        self.window.saveButton = Button(self.window, image=self.window.save_image, compound=CENTER, borderwidth=0,
                                        command=self.saveButtonAction)
        self.window.saveButton.configure(bg="#FFFFFF")
        self.window.saveButton.place(x=20, y=520)

    def initLoadButton(self):
        self.window.load_image = self.get_tk_image("Resources/Icons/ic_upload_f.png")
        self.window.loadButton = Button(self.window, image=self.window.load_image, compound=CENTER, borderwidth=0,
                                        command=self.loadButtonAction)
        self.window.loadButton.configure(bg="#FFFFFF")
        self.window.loadButton.place(x=70, y=520)

    def initDurationLabel(self):
        self.window.durationLabel = tk.Label(text=self.convertSecondsToString(self.window.durationValue),
                                             font=("Calibri", 14, "bold"))
        self.window.durationLabel.configure(bg="#FFFFFF")
        self.window.durationLabel.place(x=415, y=527.5)

    def initFileNameEditText(self):
        self.window.fileNameE = tk.Entry(self.window, width=12, justify='center', font=("Calibri"))
        self.window.fileNameE.configure(bg="#FEFEFE")
        self.window.fileNameE.place(x=20, y=490)
        self.window.fileNameE.insert(0, "voice1.wav")

    def initSamplingFrequencyEditText(self):
        self.window.samplingFreqE = tk.Entry(self.window, width=6, font=("Calibri", 12), justify='center')
        self.window.samplingFreqE.configure(bg="#FEFEFE")
        self.window.samplingFreqE.place(x=590, y=527.5)
        self.window.samplingFreqE.insert(0, self.window.samplingFreq)

    def initBitsPerSampleEditText(self):
        self.window.bitsPerSampleE = tk.Entry(self.window, width=6, font=("Calibri", 12), justify='center')
        self.window.bitsPerSampleE.configure(bg="#FEFEFE")
        self.window.bitsPerSampleE.place(x=742, y=527.5)
        self.window.bitsPerSampleE.insert(0, self.window.bitsPerSample)


    def initSamplingFrequencyLabel(self):
        self.window.samplingFreqL = tk.Label(text="Sampling Frequency",
                                             font=("Calibri", 12))
        self.window.samplingFreqL.configure(bg="#FFFFFF")
        self.window.samplingFreqL.place(x=550, y=500)

    def initBitsPerSampleLabel(self):
        self.window.bitsPerSampleL = tk.Label(text="Bits per sample",
                                             font=("Calibri", 12))
        self.window.bitsPerSampleL.configure(bg="#FFFFFF")
        self.window.bitsPerSampleL.place(x=720, y=500)

    def initZoomFromEditText(self):
        self.window.zoomFromE = tk.Entry(self.window, width=6, font=("Calibri", 12), justify='center')
        self.window.zoomFromE.configure(bg="#FEFEFE")
        self.window.zoomFromE.place(x=600, y=400)
        self.window.zoomFromE.insert(0, "0")

    def initZoomToEditText(self):
        self.window.zoomToE = tk.Entry(self.window, width=6, font=("Calibri", 12), justify='center')
        self.window.zoomToE.configure(bg="#FEFEFE")
        self.window.zoomToE.place(x=600, y=450)
        self.window.zoomToE.insert(0, "6")

    def initZoomFromLabel(self):
        self.window.zoomFromL = tk.Label(text="From",
                                             font=("Calibri", 12))
        self.window.zoomFromL.configure(bg="#FFFFFF")
        self.window.zoomFromL.place(x=550, y=400)

    def initZoomToLabel(self):
        self.window.zoomToL = tk.Label(text="To",
                                             font=("Calibri", 12))
        self.window.zoomToL.configure(bg="#FFFFFF")
        self.window.zoomToL.place(x=550, y=450)


    def initZoomButton(self):
        self.window.zoomButton = Button(self.window, text="Zoom", borderwidth=1,
                                        command=self.zoomButtonAction)
        self.window.zoomButton.configure(bg="#FFFFFF")
        self.window.zoomButton.place(x=700, y=400)

    def initZoomResetButton(self):
        self.window.zoomResetButton = Button(self.window, text="Reset", borderwidth=1,
                                        command=self.resetButtonAction)
        self.window.zoomResetButton.configure(bg="#FFFFFF")
        self.window.zoomResetButton.place(x=700, y=450)




    def get_tk_image(self, image_path, size=(40, 40)):
        self.window.img = Image.open(image_path)
        self.window.img = self.window.img.resize(size)
        return ImageTk.PhotoImage(self.window.img)

    def change_recording_status(self):
        if self.isRecording:
            self.window.pauseButton.configure(image=self.window.pause_image)
            self.resumeButtonAction()
        else:
            self.window.pauseButton.configure(image=self.window.resume_image)
            self.pauseButtonAction()
        self.isRecording = not self.isRecording

    @staticmethod
    def convertSecondsToString(seconds):
        h = seconds // 3600
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60
        return '{:02d} : {:02d} : {:02d}'.format(h, m, s)



    def recordButtonAction(self):
        self.audioController.record()

    def changeDurationLabelValue(self):
        self.window.durationLabel.config(text=self.convertSecondsToString(self.window.durationValue))

    def changeSamplingFreqE(self):
        self.window.samplingFreqE.delete(0, END)
        self.window.samplingFreqE.insert(0, self.window.samplingFreq)
        # self.window.samplingFreqE.config(text=self.window.samplingFreq)

    def changeBitsPerSample(self):
        self.window.bitsPerSampleE.delete(0, END)
        self.window.bitsPerSampleE.insert(0, self.window.bitsPerSample)

    def pauseButtonAction(self):
        self.audioController.pause()

    def resumeButtonAction(self):
        self.audioController.play()

    def stopButtonAction(self):
        self.audioController.stop()

    def saveButtonAction(self):
        self.audioController.save(self.window.fileNameE.get())
        pass

    def loadButtonAction(self):
        self.window.durationValue, self.window.samplingFreq, self.window.bitsPerSample = self.audioController.load(self.window.fileNameE.get())
        self.changeDurationLabelValue()
        self.changeSamplingFreqE()
        self.changeBitsPerSample()
        pass

    def zoomButtonAction(self):
        pass

    def resetButtonAction(self):
        pass
