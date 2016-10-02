# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 15:56:44 2016

@author: Moseph
"""

def Main():
    pass

########################## HELPER FUNCTIONS ##################################

def MakeNumpyArray(input_list):
    """
Converts lists into numpy arrays

:param list input_list: list to be converted to a numpy array
:return float32 np_array: converted numpy array
    """
    from numpy import array, float32
    
    np_array=array(input_list, dtype=float32)

    return np_array
    
def MakeList(input_array):
    """
Converts numpy arrays to lists

:param float32 input_array: numpy array to be converted to list
:return list output_list: converted list
    """
    
    output_list = list(input_array)
    
    return output_list
    
def MyIntegrate(input_curve):
    """
Sums up all values of a curve starting from the first non-zero value to the
last non-zero value

:param list input_curve: list of values from the curve
:return float curve_sum: the calculated sum
    """
    c = input_curve    
    f = 0
    l = 1
    
    # determine first non-zero value
    while c[f] == 0:
        f += 1
        
    # determine last non-zero value
    while c[-l] == 0:
        l += 1

    c_int = c[f:-l]
    
    curve_sum = sum(c_int)
    
    return curve_sum    
    
###############################################################################

def ReadInput(dynamic_range):
    """
Reads raw signal off of ADC pin and stores voltage readings and time

:param list dynamic_range: 1-by-2 list where first value represents the lower
                           limit expected of the raw signal and the second
                           value represents the upper limit expected
:return list signal: 2-by-N list of the signal and its corresponding time
    """
    from time import time
    
    v = []
    
    time_i = time
    time_e = []
    
    while time_e <= 5:
        v.append(read_raw("pin"))
        time_f = time
        time_e = time_f - time_i
    
    t = range(0, time_e, time_e / len(v))
    
    signal = [v, t]
    
    return signal

def LPFilter(signal, cutoff):
    """
Filters out frequency component above a specified frequency of raw signal

:param list signal: 2-by-N list of the signal and its corresponding time
:param int cutoff: the cutoff frequency in Hz
:return list f_signal: 2-by-N list of the filtered signal and its corresponding
                       time
    """
    #from numpy import fft, pi
    #from matplotlib.pyplot import figure, plot, show
    from scipy.signal import butter, filtfilt
    
    v = signal[0][:]
    t = signal[1][:]
    dt = (t[-1] - t[0]) / (len(t) - 1)
    Fs = 1 / dt
    nyq_f = Fs / 2
    
    #v_f = abs(fft.fft(v))
    #v_f = fft.fftshift(v_f)
    
    #f = fft.fftfreq(len(t), dt)
    #f /= (2 * pi)
    
    pad = len(v) / 10
    
    b, a = butter(4, cutoff / nyq_f)
    v_f = filtfilt(b, a, v, padlen=pad)
    
    # chop off last tenth of data (where ringing occurs) & keep the rest
    keep = .9 * len(v_f)
    v_f = v_f[0:keep]
    t = t[0:keep]
    
    for i in range(len(v_f)):
        v_f[i] = round(v_f[i], 3)
    
    #figure(1)
    #plot(t, v_f)
    #show()
    
    f_signal = [v_f, t]
    
    return f_signal    

def RemoveDCOffset(signal, t_window=1):
    """
Removes any DC offset from the raw signal my subtracting an averaged signal

:param list signal: 2-by-N list of the signal and its corresponding time
:param int t_window: window time used for averaging out signal (must be less
                     than total signal time!)
:return list orm_signal: 2-by-N list of the signal with offset removed and its
                         corresponding time
    """
    from numpy import convolve, ones
#    from matplotlib.pyplot import figure, plot, show
    
    v = signal[0][:]
    t = signal[1][:]
    tw = t_window
    
    window_len = len(v) * tw / t[-1]
    
    np_v = MakeNumpyArray(v)
    sqr = ones(window_len) / window_len
    
    offset = convolve(np_v, sqr, mode = 'same') ; #print 'offset: ', offset   
    
#    figure(1)
#    plot(t, np_v)
#    show()
    
    # Need to fix edges of the offset curve since only partial overlap occurs
    # at these parts of the convolution
    hwl = window_len / 2 # half window length
    
    offset[0:hwl] = offset[0:hwl] - offset[0] # remove any initial offset
    
    #set the left-sided edge eqaul to the sum of itself and the right-sided edge
    offset[0:hwl] = offset[0:hwl] + offset[len(offset) + 1 - hwl:len(offset)]
    #do the same with right edge
    offset[len(offset) + 1 - hwl:len(offset)] = offset[0:hwl]
    
#    figure(1)
#    plot(t, offset)
#    show()
    
    orm_array = np_v - offset
    
    #figure(3)
    #plot(t, orm_array)
    #show()
    
    orm_v = MakeList(orm_array)
    
    orm_signal = [orm_v, t]
    
    return orm_signal    

def CollectEHR(): # gen 2
    pass

def EnergyToBMD(signal):
    """
Converts the energy signal to a single value representing approximate bone
mineral density

:param list signal: 2-by-N list of the signal and its corresponding time
:return float bmd: calculated bone mineral density
    """
    
    v = signal[0][:]
    t = signal[1][:]
    
    v_sum = MyIntegrate(v)
    
    # define corresponding energy levels
    
    # these current values are just placeholder that will later be determined
    # through testing
    level_1 = 0
    level_2 = 0.3
    level_3 = 0.7
    level_4 = 1 
    
    if v_sum > level_4:
        bmd = None
        print 'ERROR! Abnormally high bone density.'
    elif v_sum > level_3:
        bmd = None
        print 'Very good bone density!'
    elif v_sum > level_2:
        bmd = None
        print 'Safe bone density.'
    elif v_sum > level_1:
        bmd = None
        print 'Unsafe bone density!'
    else:
        bmd = None
        print 'ERROR! Negative energy not plausible.'
        
    return bmd

def FractureRisk(): # gen 2
    pass

def UpdateEHR(): # gen 2
    pass

def UserOutput(bone_density):
    """
Displays the calculated bone mineral density for the processed signal

:param float bmd: calculated bone mineral density
    """
    pass

if __name__ == '__main__':
    Main()
