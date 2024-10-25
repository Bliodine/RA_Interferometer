"Importing modules"
from numpy as np
from matplotlib.pyplot as plt

"Defining a time array"
sample_rate         = 10e6
measurement_time    = 0.5
time                = np.linspace(0,measurement_time, sample_rate * measurement_time)

"Construct a random science signal"

"We want to be able to measure a phase shift between signals in the order 10-100 pico seconds accuracy"
