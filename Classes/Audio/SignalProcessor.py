from enum import Enum

from scipy.fft import rfft
from scipy.fftpack import fft, ifft
import numpy as np
import math

class Window(Enum):
    # Define Status
    RECTANGULAR = 'Rectangular'
    HAMMING = 'HAMMING'
    HANNING = 'HANNING'


class SignalProcessor:

    WINDOW_RECTANGULAR = "Rectangular"

    @staticmethod
    def PreEmphasis(frame):
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

        fftResult = 20 * np.log(np.abs(fftResult))

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
        # Fill frame
        for i in range(N):
            if i >= len(signalData):
                break
            frame[i] = signalData[startPoint + i]

        return frame









