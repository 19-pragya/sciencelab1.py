def set_sine1(self, freq):
        """
		Set the frequency of wavegen 1 after setting its waveform type to sinusoidal
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency to set on wave generator 1.
		==============  ============================================================================================
		:return: frequency
		"""
        return self.set_w1(freq, 'sine')

    def set_sine2(self, freq):
        """
		Set the frequency of wavegen 2 after setting its waveform type to sinusoidal
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency to set on wave generator 1.
		==============  ============================================================================================
		:return: frequency
		"""
        return self.set_w2(freq, 'sine')

    def set_w1(self, freq, waveType=None):
        """
		Set the frequency of wavegen 1
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency to set on wave generator 1.
		waveType		'sine','tria' . Default : Do not reload table. and use last set table
		==============  ============================================================================================
		:return: frequency
		"""
        if freq < 0.1:
            self.__print__('freq too low')
            return 0
        elif freq < 1100:
            HIGHRES = 1
            table_size = 512
        else:
            HIGHRES = 0
            table_size = 32

        if waveType:  # User wants to set a particular waveform type. sine or tria
            if waveType in ['sine', 'tria']:
                if (self.WType['W1'] != waveType):
                    self.load_equation('W1', waveType)
            else:
                print('Not a valid waveform. try sine or tria')

        p = [1, 8, 64, 256]
        prescaler = 0
        while prescaler <= 3:
            wavelength = int(round(64e6 / freq / p[prescaler] / table_size))
            freq = (64e6 / wavelength / p[prescaler] / table_size)
            if wavelength < 65525: break
            prescaler += 1
        if prescaler == 4:
            self.__print__('out of range')
            return 0

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_SINE1)
        self.H.__sendByte__(HIGHRES | (prescaler << 1))  # use larger table for low frequencies
        self.H.__sendInt__(wavelength - 1)
        self.H.__get_ack__()
        self.sine1freq = freq
        return freq

    def set_w2(self, freq, waveType=None):
        """
		Set the frequency of wavegen 2
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency to set on wave generator 1.
		==============  ============================================================================================
		:return: frequency
		"""
        if freq < 0.1:
            self.__print__('freq too low')
            return 0
        elif freq < 1100:
            HIGHRES = 1
            table_size = 512
        else:
            HIGHRES = 0
            table_size = 32

        if waveType:  # User wants to set a particular waveform type. sine or tria
            if waveType in ['sine', 'tria']:
                if (self.WType['W2'] != waveType):
                    self.load_equation('W2', waveType)
            else:
                print('Not a valid waveform. try sine or tria')

        p = [1, 8, 64, 256]
        prescaler = 0
        while prescaler <= 3:
            wavelength = int(round(64e6 / freq / p[prescaler] / table_size))
            freq = (64e6 / wavelength / p[prescaler] / table_size)
            if wavelength < 65525: break
            prescaler += 1
        if prescaler == 4:
            self.__print__('out of range')
            return 0

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_SINE2)
        self.H.__sendByte__(HIGHRES | (prescaler << 1))  # use larger table for low frequencies
        self.H.__sendInt__(wavelength - 1)
        self.H.__get_ack__()
        self.sine2freq = freq

        return freq

    def readbackWaveform(self, chan):
        """
		Set the frequency of wavegen 1
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		chan            Any of W1,W2,SQR1,SQR2,SQR3,SQR4
		==============  ============================================================================================
		:return: frequency
		"""
        if chan == 'W1':
            return self.sine1freq
        elif chan == 'W2':
            return self.sine2freq
        elif chan[:3] == 'SQR':
            return self.sqrfreq.get(chan, None)

    def set_waves(self, freq, phase, f2=None):
        """
		Set the frequency of wavegen
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency to set on both wave generators
		phase           Phase difference between the two. 0-360 degrees
		f2              Only specify if you require two separate frequencies to be set
		==============  ============================================================================================
		:return: frequency
		"""
        if f2:
            freq2 = f2
        else:
            freq2 = freq

        if freq < 0.1:
            self.__print__('freq1 too low')
            return 0
        elif freq < 1100:
            HIGHRES = 1
            table_size = 512
        else:
            HIGHRES = 0
            table_size = 32

        if freq2 < 0.1:
            self.__print__('freq2 too low')
            return 0
        elif freq2 < 1100:
            HIGHRES2 = 1
            table_size2 = 512
        else:
            HIGHRES2 = 0
            table_size2 = 32
        if freq < 1. or freq2 < 1.:
            self.__print__('extremely low frequencies will have reduced amplitudes due to AC coupling restrictions')

        p = [1, 8, 64, 256]
        prescaler1 = 0
        while prescaler1 <= 3:
            wavelength = int(round(64e6 / freq / p[prescaler1] / table_size))
            retfreq = (64e6 / wavelength / p[prescaler1] / table_size)
            if wavelength < 65525: break
            prescaler1 += 1
        if prescaler1 == 4:
            self.__print__('#1 out of range')
            return 0

        p = [1, 8, 64, 256]
        prescaler2 = 0
        while prescaler2 <= 3:
            wavelength2 = int(round(64e6 / freq2 / p[prescaler2] / table_size2))
            retfreq2 = (64e6 / wavelength2 / p[prescaler2] / table_size2)
            if wavelength2 < 65525: break
            prescaler2 += 1
        if prescaler2 == 4:
            self.__print__('#2 out of range')
            return 0

        phase_coarse = int(table_size2 * (phase) / 360.)
        phase_fine = int(wavelength2 * (phase - (phase_coarse) * 360. / table_size2) / (360. / table_size2))

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_BOTH_WG)

        self.H.__sendInt__(wavelength - 1)  # not really wavelength. time between each datapoint
        self.H.__sendInt__(wavelength2 - 1)  # not really wavelength. time between each datapoint
        self.H.__sendInt__(phase_coarse)  # table position for phase adjust
        self.H.__sendInt__(phase_fine)  # timer delay / fine phase adjust

        self.H.__sendByte__((prescaler2 << 4) | (prescaler1 << 2) | (HIGHRES2 << 1) | (
            HIGHRES))  # use larger table for low frequencies
        self.H.__get_ack__()
        self.sine1freq = retfreq
        self.sine2freq = retfreq2

        return retfreq

    def load_equation(self, chan, function, span=None, **kwargs):
        '''
		Load an arbitrary waveform to the waveform generators
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		chan             The waveform generator to alter. W1 or W2
		function            A function that will be used to generate the datapoints
		span                the range of values in which to evaluate the given function
		==============  ============================================================================================
		.. code-block:: python
		  fn = lambda x:abs(x-50)  #Triangular waveform
		  self.I.load_waveform('W1',fn,[0,100])
		  #Load triangular wave to wavegen 1
		  #Load sinusoidal wave to wavegen 2
		  self.I.load_waveform('W2',np.sin,[0,2*np.pi])
		'''
        if function == 'sine' or function == np.sin:
            function = np.sin
            span = [0, 2 * np.pi]
            self.WType[chan] = 'sine'
        elif function == 'tria':
            function = lambda x: abs(x % 4 - 2) - 1
            span = [-1, 3]
            self.WType[chan] = 'tria'
        else:
            self.WType[chan] = 'arbit'

        self.__print__('reloaded wave equation for %s : %s' % (chan, self.WType[chan]))
        x1 = np.linspace(span[0], span[1], 512 + 1)[:-1]
        y1 = function(x1)
        self.load_table(chan, y1, self.WType[chan], **kwargs)

    def load_table(self, chan, points, mode='arbit', **kwargs):
        '''
		Load an arbitrary waveform table to the waveform generators
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		chan             The waveform generator to alter. 'W1' or 'W2'
		points          A list of 512 datapoints exactly
		mode			Optional argument. Type of waveform. default value 'arbit'. accepts 'sine', 'tria'
		==============  ============================================================================================
		example::
		  >>> self.I.load_waveform_table(1,range(512))
		  #Load sawtooth wave to wavegen 1
		'''
        self.__print__('reloaded wave table for %s : %s' % (chan, mode))
        self.WType[chan] = mode
        chans = ['W1', 'W2']
        if chan in chans:
            num = chans.index(chan) + 1
        else:
            print('Channel does not exist. Try W2 or W2')
            return

        # Normalize and scale .
        # y1 = array with 512 points between 0 and 512
        # y2 = array with 32 points between 0 and 64

        amp = kwargs.get('amp', 0.95)
        LARGE_MAX = 511 * amp  # A form of amplitude control. This decides the max PWM duty cycle out of 512 clocks
        SMALL_MAX = 63 * amp  # Max duty cycle out of 64 clocks
        y1 = np.array(points)
        y1 -= min(y1)
        y1 = y1 / float(max(y1))
        y1 = 1. - y1
        y1 = list(np.int16(np.round(LARGE_MAX - LARGE_MAX * y1)))

        y2 = np.array(points[::16])
        y2 -= min(y2)
        y2 = y2 / float(max(y2))
        y2 = 1. - y2
        y2 = list(np.int16(np.round(SMALL_MAX - SMALL_MAX * y2)))

        self.H.__sendByte__(CP.WAVEGEN)
        if (num == 1):
            self.H.__sendByte__(CP.LOAD_WAVEFORM1)
        elif (num == 2):
            self.H.__sendByte__(CP.LOAD_WAVEFORM2)

        for a in y1:
            self.H.__sendInt__(a)
        for a in y2:
            self.H.__sendByte__(CP.Byte.pack(a))
        time.sleep(0.01)
        self.H.__get_ack__()

    def sqr1(self, freq, duty_cycle=50, onlyPrepare=False):
        """
		Set the frequency of sqr1
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency
		duty_cycle      Percentage of high time
		==============  ============================================================================================
		"""
        if freq == 0 or duty_cycle == 0: return None
        if freq > 10e6:
            print('Frequency is greater than 10MHz. Please use map_reference_clock for 16 & 32MHz outputs')
            return 0

        p = [1, 8, 64, 256]
        prescaler = 0
        while prescaler <= 3:
            wavelength = int(64e6 / freq / p[prescaler])
            if wavelength < 65525: break
            prescaler += 1
        if prescaler == 4 or wavelength == 0:
            self.__print__('out of range')
            return 0
        high_time = wavelength * duty_cycle / 100.
        self.__print__(wavelength, ':', high_time, ':', prescaler)
        if onlyPrepare: self.set_state(SQR1=False)

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_SQR1)
        self.H.__sendInt__(int(round(wavelength)))
        self.H.__sendInt__(int(round(high_time)))
        if onlyPrepare: prescaler |= 0x4  # Instruct hardware to prepare the square wave, but do not connect it to the output.
        self.H.__sendByte__(prescaler)
        self.H.__get_ack__()

        self.sqrfreq['SQR1'] = 64e6 / wavelength / p[prescaler & 0x3]
        return self.sqrfreq['SQR1']

    def sqr1_pattern(self, timing_array):
        """
		output a preset sqr1 frequency in fixed intervals. Can be used for sending IR signals that are packets
		of 38KHz pulses.
		refer to the example
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		timing_array    A list of on & off times in uS units
		==============  ============================================================================================
		.. code-block:: python
			I.sqr1(38e3 , 50, True )   # Prepare a 38KHz, 50% square wave. Do not output it yet
			I.sqr1_pattern([1000,1000,1000,1000,1000])  #On:1mS (38KHz packet), Off:1mS, On:1mS (38KHz packet), Off:1mS, On:1mS (38KHz packet), Off: indefinitely..
		"""
        self.fill_buffer(self.MAX_SAMPLES / 2, timing_array)  # Load the array to the ADCBuffer(second half)

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SQR1_PATTERN)
        self.H.__sendInt__(len(timing_array))
        time.sleep(sum(timing_array) * 1e-6)  # Sleep for the whole duration
        self.H.__get_ack__()

        return True

    def sqr2(self, freq, duty_cycle):
        """
		Set the frequency of sqr2
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency
		duty_cycle      Percentage of high time
		==============  ============================================================================================
		"""
        p = [1, 8, 64, 256]
        prescaler = 0
        while prescaler <= 3:
            wavelength = 64e6 / freq / p[prescaler]
            if wavelength < 65525: break
            prescaler += 1

        if prescaler == 4 or wavelength == 0:
            self.__print__('out of range')
            return 0

        high_time = wavelength * duty_cycle / 100.
        self.__print__(wavelength, high_time, prescaler)
        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_SQR2)
        self.H.__sendInt__(int(round(wavelength)))
        self.H.__sendInt__(int(round(high_time)))
        self.H.__sendByte__(prescaler)
        self.H.__get_ack__()

        self.sqrfreq['SQR2'] = 64e6 / wavelength / p[prescaler & 0x3]
        return self.sqrfreq['SQR2']

    def set_sqrs(self, wavelength, phase, high_time1, high_time2, prescaler=1):
        """
		Set the frequency of sqr1,sqr2, with phase shift
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		wavelength      Number of 64Mhz/prescaler clock cycles per wave
		phase           Clock cycles between rising edges of SQR1 and SQR2
		high time1      Clock cycles for which SQR1 must be HIGH
		high time2      Clock cycles for which SQR2 must be HIGH
		prescaler       0,1,2. Divides the 64Mhz clock by 8,64, or 256
		==============  ============================================================================================
		"""

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_SQRS)
        self.H.__sendInt__(wavelength)
        self.H.__sendInt__(phase)
        self.H.__sendInt__(high_time1)
        self.H.__sendInt__(high_time2)
        self.H.__sendByte__(prescaler)
        self.H.__get_ack__()

    def sqrPWM(self, freq, h0, p1, h1, p2, h2, p3, h3, **kwargs):
        """
		Initialize phase correlated square waves on SQR1,SQR2,SQR3,SQR4
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		freq            Frequency in Hertz
		h0              Duty Cycle for SQR1 (0-1)
		p1              Phase shift for SQR2 (0-1)
		h1              Duty Cycle for SQR2 (0-1)
		p2              Phase shift for OD1  (0-1)
		h2              Duty Cycle for OD1  (0-1)
		p3              Phase shift for OD2  (0-1)
		h3              Duty Cycle for OD2  (0-1)
		==============  ============================================================================================
		"""
        if freq == 0 or h0 == 0 or h1 == 0 or h2 == 0 or h3 == 0: return 0
        if freq > 10e6:
            print('Frequency is greater than 10MHz. Please use map_reference_clock for 16 & 32MHz outputs')
            return 0

        p = [1, 8, 64, 256]
        prescaler = 0
        while prescaler <= 3:
            wavelength = int(64e6 / freq / p[prescaler])
            if wavelength < 65525: break
            prescaler += 1
        if prescaler == 4 or wavelength == 0:
            self.__print__('out of range')
            return 0

        if not kwargs.get('pulse', False): prescaler |= (1 << 5)

        A1 = int(p1 % 1 * wavelength)
        B1 = int((h1 + p1) % 1 * wavelength)
        A2 = int(p2 % 1 * wavelength)
        B2 = int((h2 + p2) % 1 * wavelength)
        A3 = int(p3 % 1 * wavelength)
        B3 = int((h3 + p3) % 1 * wavelength)

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SQR4)
        self.H.__sendInt__(wavelength - 1)
        self.H.__sendInt__(int(wavelength * h0) - 1)

        self.H.__sendInt__(max(0, A1 - 1))
        self.H.__sendInt__(max(1, B1 - 1))
        self.H.__sendInt__(max(0, A2 - 1))
        self.H.__sendInt__(max(1, B2 - 1))
        self.H.__sendInt__(max(0, A3 - 1))
        self.H.__sendInt__(max(1, B3 - 1))
        self.H.__sendByte__(prescaler)
        self.H.__get_ack__()

        for a in ['SQR1', 'SQR2', 'SQR3', 'SQR4']: self.sqrfreq[a] = 64e6 / wavelength / p[prescaler & 0x3]
        return 64e6 / wavelength / p[prescaler & 0x3]

    def map_reference_clock(self, scaler, *args):
        """
		Map the internal oscillator output  to SQR1,SQR2,SQR3,SQR4 or WAVEGEN
		The output frequency is 128/(1<<scaler) MHz
		scaler [0-15]
			* 0 -> 128MHz
			* 1 -> 64MHz
			* 2 -> 32MHz
			* 3 -> 16MHz
			* .
			* .
			* 15 ->128./32768 MHz
		example::
		>>> I.map_reference_clock(2,'SQR1','SQR2')
		outputs 32 MHz on SQR1, SQR2 pins
		.. note::
			if you change the reference clock for 'wavegen' , the external waveform generator(AD9833) resolution and range will also change.
			default frequency for 'wavegen' is 16MHz. Setting to 1MHz will give you 16 times better resolution, but a usable range of
			0Hz to about 100KHz instead of the original 2MHz.
		"""
        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.MAP_REFERENCE)
        chan = 0
        if 'SQR1' in args: chan |= 1
        if 'SQR2' in args: chan |= 2
        if 'SQR3' in args: chan |= 4
        if 'SQR4' in args: chan |= 8
        if 'WAVEGEN' in args: chan |= 16
        self.H.__sendByte__(chan)
        self.H.__sendByte__(scaler)
        if 'WAVEGEN' in args: self.DDS_CLOCK = 128e6 / (1 << scaler)
        self.H.__get_ack__()

    # -------------------------------------------------------------------------------------------------------------------#

    # |===============================================ANALOG OUTPUTS ====================================================|
    # |This section has commands related to current and voltage sources PV1,PV2,PV3,PCS					            |
    # -------------------------------------------------------------------------------------------------------------------#

    def set_pv1(self, val):
        """
		Set the voltage on PV1
		12-bit DAC...  -5V to 5V
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		val             Output voltage on PV1. -5V to 5V
		==============  ============================================================================================
		"""
        return self.DAC.setVoltage('PV1', val)

    def set_pv2(self, val):
        """
		Set the voltage on PV2.
		12-bit DAC...  0-3.3V
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		val             Output voltage on PV2. 0-3.3V
		==============  ============================================================================================
		:return: Actual value set on pv2
		"""
        return self.DAC.setVoltage('PV2', val)

    def set_pv3(self, val):
        """
		Set the voltage on PV3
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		val             Output voltage on PV3. 0V to 3.3V
		==============  ============================================================================================
		:return: Actual value set on pv3
		"""
        return self.DAC.setVoltage('PV3', val)

    def set_pcs(self, val):
        """
		Set programmable current source
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		val             Output current on PCS. 0 to 3.3mA. Subject to load resistance. Read voltage on PCS to check.
		==============  ============================================================================================
		:return: value attempted to set on pcs
		"""
        return self.DAC.setCurrent(val)

    def get_pv1(self):
        """
		get the last set voltage on PV1
		12-bit DAC...  -5V to 5V
		"""
        return self.DAC.getVoltage('PV1')

    def get_pv2(self):
        return self.DAC.getVoltage('PV2')

    def get_pv3(self):
        return self.DAC.getVoltage('PV3')

    def get_pcs(self):
        return self.DAC.getVoltage('PCS')

    def WS2812B(self, cols, output='CS1'):
        """
		set shade of WS2182 LED on SQR1
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		cols                2Darray [[R,G,B],[R2,G2,B2],[R3,G3,B3]...]
							brightness of R,G,B ( 0-255  )
		==============  ============================================================================================
		example::
			>>> I.WS2812B([[10,0,0],[0,10,10],[10,0,10]])
			#sets red, cyan, magenta to three daisy chained LEDs
		see :ref:`rgb_video`
		"""
        if output == 'CS1':
            pin = CP.SET_RGB1
        elif output == 'CS2':
            pin = CP.SET_RGB2
        elif output == 'SQR1':
            pin = CP.SET_RGB3
        else:
            print('invalid output')
            return

        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(pin)
        self.H.__sendByte__(len(cols) * 3)
        for col in cols:
            R = col[0]
            G = col[1]
            B = col[2]
            self.H.__sendByte__(G)
            self.H.__sendByte__(R)
            self.H.__sendByte__(B)
        self.H.__get_ack__()

    # -------------------------------------------------------------------------------------------------------------------#

    # |======================================READ PROGRAM AND DATA ADDRESSES=============================================|
    # |Direct access to RAM and FLASH		     																		|
    # -------------------------------------------------------------------------------------------------------------------#

    def read_program_address(self, address):
        """
		Reads and returns the value stored at the specified address in program memory
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		address         Address to read from. Refer to PIC24EP64GP204 programming manual
		==============  ============================================================================================
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.READ_PROGRAM_ADDRESS)
        self.H.__sendInt__(address & 0xFFFF)
        self.H.__sendInt__((address >> 16) & 0xFFFF)
        v = self.H.__getInt__()
        self.H.__get_ack__()
        return v

    def device_id(self):
        a = self.read_program_address(0x800FF8)
        b = self.read_program_address(0x800FFa)
        c = self.read_program_address(0x800FFc)
        d = self.read_program_address(0x800FFe)
        val = d | (c << 16) | (b << 32) | (a << 48)
        self.__print__(a, b, c, d, hex(val))
        return val

    def __write_program_address__(self, address, value):
        """
		Writes a value to the specified address in program memory. Disabled in firmware.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		address         Address to write to. Refer to PIC24EP64GP204 programming manual
						Do Not Screw around with this. It won't work anyway.
		==============  ============================================================================================
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.WRITE_PROGRAM_ADDRESS)
        self.H.__sendInt__(address & 0xFFFF)
        self.H.__sendInt__((address >> 16) & 0xFFFF)
        self.H.__sendInt__(value)
        self.H.__get_ack__()

    def read_data_address(self, address):
        """
		Reads and returns the value stored at the specified address in RAM
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		address         Address to read from.  Refer to PIC24EP64GP204 programming manual|
		==============  ============================================================================================
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.READ_DATA_ADDRESS)
        self.H.__sendInt__(address & 0xFFFF)
        v = self.H.__getInt__()
        self.H.__get_ack__()
        return v

    def __write_data_address__(self, address, value):
        """
		Writes a value to the specified address in RAM
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		address         Address to write to.  Refer to PIC24EP64GP204 programming manual|
		==============  ============================================================================================
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.WRITE_DATA_ADDRESS)
        self.H.__sendInt__(address & 0xFFFF)
        self.H.__sendInt__(value)
        self.H.__get_ack__()

    # -------------------------------------------------------------------------------------------------------------------#

    # |==============================================MOTOR SIGNALLING====================================================|
    # |Set servo motor angles via SQ1-4. Control one stepper motor using SQ1-4											|
    # -------------------------------------------------------------------------------------------------------------------#

    def __stepperMotor__(self, steps, delay, direction):
        self.H.__sendByte__(CP.NONSTANDARD_IO)
        self.H.__sendByte__(CP.STEPPER_MOTOR)
        self.H.__sendInt__((steps << 1) | direction)
        self.H.__sendInt__(delay)

        time.sleep(steps * delay * 1e-3)  # convert mS to S

    def stepForward(self, steps, delay):
        """
		Control stepper motors using SQR1-4
		take a fixed number of steps in the forward direction with a certain delay( in milliseconds ) between each step.
		"""
        self.__stepperMotor__(steps, delay, 1)

    def stepBackward(self, steps, delay):
        """
		Control stepper motors using SQR1-4
		take a fixed number of steps in the backward direction with a certain delay( in milliseconds ) between each step.
		"""
        self.__stepperMotor__(steps, delay, 0)

    def servo(self, angle, chan='SQR1'):
        '''
		Output A PWM waveform on SQR1/SQR2 corresponding to the angle specified in the arguments.
		This is used to operate servo motors.  Tested with 9G SG-90 Servo motor.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		angle           0-180. Angle corresponding to which the PWM waveform is generated.
		chan            'SQR1' or 'SQR2'. Whether to use SQ1 or SQ2 to output the PWM waveform used by the servo
		==============  ============================================================================================
		'''
        if chan == 'SQR1':
            self.sqr1(100, 7.5 + 19. * angle / 180)  # 100Hz
        elif chan == 'SQR2':
            self.sqr2(100, 7.5 + 19. * angle / 180)  # 100Hz

    def servo4(self, a1, a2, a3, a4):
        """
		Operate Four servo motors independently using SQR1, SQR2, SQR3, SQR4.
		tested with SG-90 9G servos.
		For high current servos, please use a different power source, and a level convertor for the PWm output signals(if needed)
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		a1              Angle to set on Servo which uses SQR1 as PWM input. [0-180]
		a2              Angle to set on Servo which uses SQR2 as PWM input. [0-180]
		a3              Angle to set on Servo which uses SQR3 as PWM input. [0-180]
		a4              Angle to set on Servo which uses SQR4 as PWM input. [0-180]
		==============  ============================================================================================
		"""
        params = (1 << 5) | 2  # continuous waveform.  prescaler 2( 1:64)
        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SQR4)
        self.H.__sendInt__(10000)  # 10mS wavelength
        self.H.__sendInt__(750 + int(a1 * 1900 / 180))
        self.H.__sendInt__(0)
        self.H.__sendInt__(750 + int(a2 * 1900 / 180))
        self.H.__sendInt__(0)
        self.H.__sendInt__(750 + int(a3 * 1900 / 180))
        self.H.__sendInt__(0)
        self.H.__sendInt__(750 + int(a4 * 1900 / 180))
        self.H.__sendByte__(params)
        self.H.__get_ack__()

    def enableUartPassthrough(self, baudrate, persist=False):
        '''
		All data received by the device is relayed to an external port(SCL[TX],SDA[RX]) after this function is called
		If a period > .5 seconds elapses between two transmit/receive events, the device resets
		and resumes normal mode. This timeout feature has been implemented in lieu of a hard reset option.
		can be used to load programs into secondary microcontrollers with bootloaders such ATMEGA, and ESP8266
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		baudrate        BAUDRATE to use
		persist         If set to True, the device will stay in passthrough mode until the next power cycle.
						Otherwise(default scenario), the device will return to normal operation if no data is sent/
						received for a period greater than one second at a time.
		==============  ============================================================================================
		'''
        self.H.__sendByte__(CP.PASSTHROUGHS)
        self.H.__sendByte__(CP.PASS_UART)
        self.H.__sendByte__(1 if persist else 0)
        self.H.__sendInt__(int(round(((64e6 / baudrate) / 4) - 1)))
        self.__print__('BRGVAL:', int(round(((64e6 / baudrate) / 4) - 1)))
        time.sleep(0.1)
        self.__print__('junk bytes read:', len(self.H.fd.read(100)))

    def estimateDistance(self):
        '''
		Read data from ultrasonic distance sensor HC-SR04/HC-SR05.  Sensors must have separate trigger and output pins.
		First a 10uS pulse is output on SQR1.  SQR1 must be connected to the TRIG pin on the sensor prior to use.
		Upon receiving this pulse, the sensor emits a sequence of sound pulses, and the logic level of its output
		pin(which we will monitor via ID1) is also set high.  The logic level goes LOW when the sound packet
		returns to the sensor, or when a timeout occurs.
		The ultrasound sensor outputs a series of 8 sound pulses at 40KHz which corresponds to a time period
		of 25uS per pulse. These pulses reflect off of the nearest object in front of the sensor, and return to it.
		The time between sending and receiving of the pulse packet is used to estimate the distance.
		If the reflecting object is either too far away or absorbs sound, less than 8 pulses may be received, and this
		can cause a measurement error of 25uS which corresponds to 8mm.
		Ensure 5V supply.  You may set SQR2 to HIGH [ I.set_state(SQR2=True) ] , and use that as the power supply.
		returns 0 upon timeout
		'''
        self.H.__sendByte__(CP.NONSTANDARD_IO)
        self.H.__sendByte__(CP.HCSR04_HEADER)

        timeout_msb = int((0.3 * 64e6)) >> 16
        self.H.__sendInt__(timeout_msb)

        A = self.H.__getLong__()
        B = self.H.__getLong__()
        tmt = self.H.__getInt__()
        self.H.__get_ack__()
        if (tmt >= timeout_msb or B == 0): return 0
        rtime = lambda t: t / 64e6
        return 330. * rtime(B - A + 20) / 2.

    """
	def TemperatureAndHumidity(self):
		'''
		init  AM2302.
		This effort was a waste.  There are better humidity and temperature sensors available which use well documented I2C
		'''
		self.H.__sendByte__(CP.NONSTANDARD_IO)
		self.H.__sendByte__(CP.AM2302_HEADER)
		self.H.__get_ack__()
		self.digital_channels_in_buffer=1
	"""

    def opticalArray(self, SS, delay, channel='CH3', **kwargs):
        '''
		read from 3648 element optical sensor array TCD3648P from Toshiba. Experimental feature.
		Neither Sine waves will be available.
		Connect SQR1 to MS , SQR2 to MS , A0 to CHannel , and CS1(on the expansion slot) to ICG
		delay : ICG low duration
		tp : clock wavelength=tp*15nS,  SS=clock/4
		'''
        samples = 3694
        res = kwargs.get('resolution', 10)
        tweak = kwargs.get('tweak', 1)
        chosa = self.oscilloscope.channels[channel].chosa

        self.H.__sendByte__(CP.NONSTANDARD_IO)
        self.H.__sendByte__(CP.TCD1304_HEADER)
        if res == 10:
            self.oscilloscope.channels[channel].resolution = 10
            self.H.__sendByte__(chosa)  # 10-bit
        else:
            self.oscilloscope.channels[channel].resolution = 12
            self.H.__sendByte__(chosa | 0x80)  # 12-bit
        self.H.__sendByte__(tweak)  # Tweak the SH low to ICG high space. =tweak*delay
        self.H.__sendInt__(delay)
        self.H.__sendInt__(int(SS * 64))
        self.timebase = SS
        self.samples = samples
        self.channels_in_buffer = 1
        time.sleep(2 * delay * 1e-6)
        self.H.__get_ack__()

    def setUARTBAUD(self, BAUD):
        self.H.__sendByte__(CP.UART_2)
        self.H.__sendByte__(CP.SET_BAUD)
        self.H.__sendInt__(int(round(((64e6 / BAUD) / 4) - 1)))
        self.__print__('BRG2VAL:', int(round(((64e6 / BAUD) / 4) - 1)))
        self.H.__get_ack__()

    def writeUART(self, character):
        self.H.__sendByte__(CP.UART_2)
        self.H.__sendByte__(CP.SEND_BYTE)
        self.H.__sendByte__(character)
        self.H.__get_ack__()

    def readUART(self):
        self.H.__sendByte__(CP.UART_2)
        self.H.__sendByte__(CP.READ_BYTE)
        return self.H.__getByte__()

    def readUARTStatus(self):
        '''
		return available bytes in UART buffer
		'''
        self.H.__sendByte__(CP.UART_2)
        self.H.__sendByte__(CP.READ_UART2_STATUS)
        return self.H.__getByte__()

    def readLog(self):
        """
		read hardware debug log.
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.READ_LOG)
        log = self.H.fd.readline().strip()
        self.H.__get_ack__()
        return log
