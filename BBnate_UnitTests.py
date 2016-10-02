# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 13:45:54 2016

@author: Moseph
"""

import unittest
import BBnate_Functions as BBdef

class BBnateTests(unittest.TestCase):
    """
This class contains all the unit tests for the BB-nate, bone density measuring
device, being developed by BoneMARK. Includes testing all phases of the
software processing, from dynamic of range of raw input signal to ensuring
the output measurement is accurate and can be synced with EHR.
    """
    def MakeSine(self, time, amplitude, frequency, phase):
        """
This function is for creating sine waves of varying time, amplitude, freq,
and phase for simulating input signals
        """
        from numpy import sin, pi
        t = time
        a = amplitude
        f = frequency
        p = phase
        
        curve = a * sin(2 * pi * f * t + p)
        return curve
            
#    def test_ReadInput(self):
#        """
#Checks for the resolution of the read in signal given an expected dynamic range
#        """
#        bitdepth = 1023 # Arduino Uno has 10-bit resolution
#        
#        # synthetic signal(s) to simulate raw data read on ADC pin
#        from numpy import arange, zeros
#        from math import exp
#        
#        # Fs = 1000 # sampling frequency, Arduino in theory can do 10,000 / s
#        # step = 1 / Fs
#        t = arange(0, 5, 0.001) # time
#        
#        # signal 1 - modified Gaussian curve
#        A = 1.5 ; B = 2.5 ; C = .9
#        ex = (t - B) ** 2 / -2 / C ** 2
#        signal_1 = zeros(len(t))
#        for index in range(len(signal_1)):
#            if A * exp(ex[index]) <= A / 2:
#                signal_1[index] = A * exp(ex[index])
#            else:
#                signal_1[index] = A / 2
#        # finding the resolutions of signal 1
#        diff = abs(signal_1[1] - signal_1[0])
#        for index in range(2, len(signal_1)):
#            if abs(signal_1[index] - signal_1[index - 1]) < diff:
#                if abs(signal_1[index] - signal_1[index - 1]) != 0:
#                    diff = abs(signal_1[index] - signal_1[index - 1])
#                    # diff is smallest difference b/w adjacent values in signal_1
#                else:
#                    pass
#            else:
#                pass
#        print 'smallest difference:',diff
#        M = max(signal_1) ; m = min(signal_1) # max and min of signal_1
#        dyn_range = [m, M]
#        print 'dynamic range:',dyn_range
#        
#        res = abs((M - m) / bitdepth)
#        print res
#        
#        # test resolution
#        self.assertLessEqual(res, diff, msg = 'Given the dynamic range of %r and bit depth %d, this resolution is not gonna cut it!' % (dyn_range, bitdepth))
#        
    def test_LPFilter(self):
        """
Checks that lowpass filter is properly removing frequency from the input signal
        """
        
        #from matplotlib.pylab import figure, plot, show        
        
        A = 2 # amplitude
        f = None # frequency, Hz
        phi = 0 # phase
        from numpy import arange, zeros
        t = arange(0, 5, 0.001) # time
        Fc = 10 # cutoff frequency in Hz
        
        # signal 1 - all 60 Hz
        f = 60
        signal_1v = self.MakeSine(t, A, f, phi)
        signal_1 = [signal_1v, t]
        
        nothing = zeros(len(signal_1v)) # expected output after being filtered
        
        # signal 2 - all 5 Hz
        f = 5
        signal_2v = self.MakeSine(t, A, f, phi)
        signal_2 = [signal_2v, t]
        
        # signal 3 - both 60 Hz and 5 Hz
        signal_3v = signal_1v + signal_2v
        signal_3 = [signal_3v, t]
        
        # signal 4 - DC (0 Hz)
        signal_4v = nothing + 4
        signal_4 = [signal_4v, t]
        
        # Case 1 - all 60 Hz
        output_1 = BBdef.LPFilter(signal_1, Fc)
        output_1 = BBdef.MakeNumpyArray(output_1)
        self.assertEqual(len(output_1[0]), .9 * len(signal_1v), msg = "Where's the ruler!?...Unequal list lengths")
        self.assertAlmostEqual(output_1[0].any(), nothing.any(), msg = "Signal 1 was not filtered correctly...Maybe try a strainer???")
        
        # Case 2 - 5 Hz
        output_2 = BBdef.LPFilter(signal_2, Fc)
        output_2 = BBdef.MakeNumpyArray(output_2)
        self.assertEqual(len(output_2[0]), .9 * len(signal_2v), msg = "These lists are not the same length...just saying.")
        self.assertAlmostEqual(output_2[0].any(), signal_2v.any(), msg = "Signal 2 should look the same as it's output...like twins. But it doesn't.")
        
        # Case 3 - both 60 Hz and 5 Hz
        output_3 = BBdef.LPFilter(signal_3, Fc)
        output_3 = BBdef.MakeNumpyArray(output_3)
        self.assertEqual(len(output_3[0]), .9 * len(signal_3v), msg = "Who knew measuring length could be so hard? You do!")
        self.assertAlmostEqual(output_3[0].any(), output_2.any(), msg = "Signal 3 output should look like Signal 2. Why doesn't it?")
    
        # Case 4 - DC
        output_4 = BBdef.LPFilter(signal_4, Fc)
        output_4 = BBdef.MakeNumpyArray(output_4)
        self.assertEqual(len(output_4[0]), .9 * len(signal_4v), msg = "One list is longer than the other, whoops.")
        self.assertAlmostEqual(output_4[0].any(), signal_4v.any(), msg = "Signal 4 is incorrectly being tampered with.")
        
    
    def test_RemoveDCOffset(self):
        """
Checks that DC offset is removed from input signal properly
        """
        
        A = 2 # amplitude
        f = 20 # frequency, Hz
        phi = 0 # phase
        from numpy import arange, average
        #from matplotlib.pyplot import figure, plot, show
        t = arange(0, 5, 0.001) # time
        
        # creation of signal to test DC offset removal functionality
        signal_1A = self.MakeSine(t, A, f, phi)
        signal_1B = signal_1A + 4 # the offset
        signal_1Bin = [signal_1B, t]
        #figure(1)
        #plot(t, signal_1A)
        #show()
        
        #figure(2)
        #plot(t, signal_1B)
        #show()
        
        #print 'original mean: ', average(signal_1A), '\nand length: ', len(signal_1A)
        
        output_1 = BBdef.RemoveDCOffset(signal_1Bin)
        output_1 = BBdef.MakeNumpyArray(output_1)
        output_1v = output_1[0][:]
        
        mean = average(output_1v)
        
        #figure(3)
        #plot(t, output_1v)
        #show()
        
        #print 'new mean: ', mean, '\nand length: ', len(output_1v)
        
        self.assertEqual(len(output_1v), len(signal_1B), msg = "Don't have time to be messing up length measurements!")
        self.assertLessEqual(mean, 0.05, msg = "The mean should be about zero, which it isn't...")
        self.assertAlmostEqual(output_1v.any(), signal_1A.any(), msg = "Remove DC offset? More like Include DC onset.")
        
if __name__ == '__main__':
    unittest.main()