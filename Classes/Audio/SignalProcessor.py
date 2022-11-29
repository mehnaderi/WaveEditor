from enum import Enum

from scipy.fft import rfft, ifft
import numpy as np
import math
import scipy

class Window(Enum):
    # Define Status
    RECTANGULAR = 'Rectangular'
    HAMMING = 'HAMMING'
    HANNING = 'HANNING'


class SignalProcessor:

    WINDOW_RECTANGULAR = "Rectangular"

    @staticmethod
    def preEmphasis(frame):
        preEmphSignal = np.empty(len(frame))

        coeff = SignalProcessor.computePreEmphasisCoefficient(frame)

        # For first sample
        preEmphSignal[0] = frame[0]

        # Other samples
        for sample in range(1, len(frame)):
            preEmphSignal[sample] = frame[sample] - coeff * frame[sample - 1]

        return preEmphSignal

    @staticmethod
    def computePreEmphasisCoefficient(frame):
        r0 = SignalProcessor.computeAutoCorrelationCoefficient(frame, 0)
        r1 = SignalProcessor.computeAutoCorrelationCoefficient(frame, 1)
        return float(r1) / r0

    @staticmethod
    def computeAutoCorrelationCoefficient(frame, etta):
        N = len(frame)
        sumValue = float(0)
        for i in range(N):
            s_n_etta = 0
            if i - etta >= 0:
                s_n_etta = frame[i - etta]

            sumValue += frame[i] * s_n_etta

        return sumValue / N

    @staticmethod
    def windowing(frame, windowType):
        # Generate window :
        window = np.zeros(len(frame))

        if windowType == Window.RECTANGULAR:
            # Rectangular window:      w[n] = 1
            window = np.ones(len(frame))

        elif windowType == Window.HAMMING:
            # Hamming window:          w[n] = 0.54 - 0.46*cos(2*pi.n/N)
            for i in range(len(frame)):
                window[i] = 0.54 - 0.46 * math.cos(2 * math.pi * i / len(frame))

        elif windowType == Window.HANNING:
            # Hanning window:          w[n] = 0.5 - 0.5*cos(2*pi.n/N)
            for i in range(len(frame)):
                window[i] = 0.5 - 0.5 * math.cos(2 * math.pi * i / len(frame))

        # Apply window on frame
        return np.multiply(frame, window)

    @staticmethod
    def computeMagnitudeOfSpectrum(frame):
        fftResult = rfft(frame)
        fftResult = 20 * np.log10(np.abs(fftResult))

        return fftResult

    @staticmethod
    def selectFrame(signalData, frameNo=0, N=480, M=160, p_frequency_sampling=16000):
        """
        *    frameNo : number of frame (starting with 0)
        *    N : Frame length (ms)
        *    M : Frame shift (ms)
        """

        # Convert millisecond to number of samples
        N = int(p_frequency_sampling * N / 1000)
        M = int(p_frequency_sampling * M / 1000)
        # define start point
        startPoint = frameNo * M

        # Create new frame
        frame = np.zeros(N)
        maxSample = 0
        # Fill frame
        for i in range(N):
            if i >= len(signalData):
                break
            frame[i] = signalData[startPoint + i]
            # For Normalize values
            if frame[i] > maxSample:
                maxSample = frame[i]

        return frame / maxSample

    # calculate energy of frame
    @staticmethod
    def getEnergy(frame):
        # Initial Energy
        Energy = 0

        for sample in frame:
            Energy += sample * sample

        # Average
        Energy /= len(frame)
        return Energy

    # calculate ZCR for one frame
    @staticmethod
    def getZCR(frame):
        # Init zcr:
        zcr = 0
        # compute number of ZCRs
        for i in range(1, len(frame)):
            zcr += math.fabs(SignalProcessor.sign(frame[i]) - SignalProcessor.sign(frame[i - 1])) / 2

        # Average
        zcr /= len(frame)
        return zcr

    # Sign function
    @staticmethod
    def sign(inputValue):
        return 1 if inputValue >= 0 else -1

    # calculate correlation coefficients for one frame
    @staticmethod
    def getCORR(frame):
        correlations = []
        for eta in range(len(frame)):
            corr = 0
            for i in range(eta, len(frame)):
                corr += frame[i] * frame[i - eta]

            corr /= (len(frame) - eta + 1)
            correlations.append(corr)

        correlations = np.array(correlations)
        return correlations

    # calculate correlation coefficients for one frame
    @staticmethod
    def getAMDF(frame):
        correlations = []
        for eta in range(len(frame)):
            amdf = 0
            for i in range(eta, len(frame)):
                amdf += math.fabs(frame[i] - frame[i - eta])

            amdf /= (len(frame) - eta + 1)
            correlations.append(amdf)

        correlations = np.array(correlations)
        return correlations


    @staticmethod
    def getFormant(frame, fs):
        # Apply windowing and pre-emphasis on frame
        frame = SignalProcessor.windowing(frame, Window.HAMMING)
        frame = SignalProcessor.preEmphasis(frame)
        # Apply FFT on frame
        ySpectrum = SignalProcessor.computeMagnitudeOfSpectrum(frame)
        peaks = scipy.signal.find_peaks(ySpectrum, height=-30, distance=50)

        # Generate x values
        xSpectrum = [*range(0, int(fs / 2), int((fs / 2) / len(ySpectrum)))]
        while len(xSpectrum) > len(ySpectrum):
            xSpectrum.pop()
        xSpectrum = np.array(xSpectrum)

        return peaks, xSpectrum, ySpectrum

    @staticmethod
    def getCEPSTRAL(frame):
        # Apply windowing and pre-emphasis on frame
        frame = SignalProcessor.windowing(frame, Window.HAMMING)
        frame = SignalProcessor.preEmphasis(frame)
        # Apply FFT on frame
        # cepstrals = np.abs(ifft(ySpectrum))

        fftResult = np.log10(np.absolute(rfft(frame)))
        cepstrals = np.absolute(ifft(fftResult))


        cepstrals = cepstrals[:int(len(cepstrals)/2)]
        # cepstrals = 20 * np.log10(np.abs(cepstrals))
        # Generate x values
        xSpectrum = range(len(cepstrals))
        xSpectrum = np.array(xSpectrum)

        return xSpectrum, cepstrals

    @staticmethod
    def getEnergyAndZCRForFirst200Frames(signal):
        energyList = list()
        zcrList = list()
        for i in range(110, 310):
            frame = SignalProcessor.selectFrame(signal, frameNo=i, N=30, M=10, p_frequency_sampling=16000)
            energyList.append(SignalProcessor.getEnergy(frame))
            zcrList.append(SignalProcessor.getZCR(frame))

        xValues = np.array(range(200))
        return xValues, energyList, zcrList

    @staticmethod
    def getAutoCorrAndCepstralFor200Frames(signal, fs=16000):
        autoCorrPeakList = list()
        cepstralPeakList = list()
        for i in range(110, 310):
            frame = SignalProcessor.selectFrame(signal, frameNo=i, N=30, M=10, p_frequency_sampling=fs)

            # Compute pitch with autoCorrelation
            autoCorr = SignalProcessor.getCORR(frame)

            peaks = scipy.signal.find_peaks(autoCorr, height=0.01, distance=300)
            if len(peaks[0]) != 0:
                if peaks[0][0] > 20:
                    F_pitch = fs / peaks[0][0]
                    autoCorrPeakList.append(int(F_pitch))
                elif len(peaks[0]) > 1:
                    F_pitch = fs / peaks[0][1]
                    autoCorrPeakList.append(F_pitch)
                else:
                    autoCorrPeakList.append(int(150))
            else:
                autoCorrPeakList.append(150)

            # if len(peaks[0]) != 0:
            #     autoCorrPeakList.append(int(fs / peaks[0][0]))
            # else:
            #     autoCorrPeakList.append(0)

            # Compute pitch with Cepstral
            xSpectrum, ySpectrum = SignalProcessor.getCEPSTRAL(frame)

            peaks = scipy.signal.find_peaks(ySpectrum, distance=30, height=0.06)
            if len(peaks[0]) != 0:
                if peaks[0][0] > 20:
                    F_pitch = fs / (peaks[0][0]*2)
                    cepstralPeakList.append(int(F_pitch))
                elif len(peaks[0]) > 1:
                    F_pitch = fs / (peaks[0][1]*2)
                    cepstralPeakList.append(F_pitch)
                else:
                    cepstralPeakList.append(int(150))
            else:
                cepstralPeakList.append(150)

        xValues = np.array(range(200))
        return xValues, autoCorrPeakList, cepstralPeakList








