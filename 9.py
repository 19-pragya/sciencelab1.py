def countPulses(self, channel='SEN'):
        """
		Count pulses on a digital input. Retrieve total pulses using readPulseCount
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		channel         The input pin to measure rising edges on : ['ID1','ID2','ID3','ID4','SEN','EXT','CNTR']
		==============  ============================================================================================
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.START_COUNTING)
        self.H.__sendByte__(self.__calcDChan__(channel))
        self.H.__get_ack__()

    def readPulseCount(self):
        """
		Read pulses counted using a digital input. Call countPulses before using this.
		.. tabularcolumns:: |p{3cm}|p{11cm}|
		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		==============  ============================================================================================
		"""
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.FETCH_COUNT)
        count = self.H.__getInt__()
        self.H.__get_ack__()
        return count

    def __charge_cap__(self, state, t):
        self.H.__sendByte__(CP.ADC)
        self.H.__sendByte__(CP.SET_CAP)
        self.H.__sendByte__(state)
        self.H.__sendInt__(t)
        self.H.__get_ack__()

    def __capture_capacitance__(self, samples, tg):
        raise NotImplementedError
#        from PSL.analyticsClass import analyticsClass
#        self.AC = analyticsClass()
#        self.__charge_cap__(1, 50000)
#        x, y = self.capture_fullspeed_hr('CAP', samples, tg, 'READ_CAP')
#        fitres = self.AC.fit_exp(x * 1e-6, y)
#        if fitres:
#            cVal, newy = fitres
#            # from PSL import *
#            # plot(x,newy)
#            # show()
#            return x, y, newy, cVal
#        else:
#            return None

    def capacitance_via_RC_discharge(self):
        cap = self.get_capacitor_range()[1]
        T = 2 * cap * 20e3 * 1e6  # uS
        samples = 500
        if T > 5000 and T < 10e6:
            if T > 50e3: samples = 250
            RC = self.__capture_capacitance__(samples, int(T / samples))[3][1]
            return RC / 10e3
        else:
            self.__print__('cap out of range %f %f' % (T, cap))
            return 0

    def __get_capacitor_range__(self, ctime):
        self.__charge_cap__(0, 30000)
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.GET_CAP_RANGE)
        self.H.__sendInt__(ctime)
        V_sum = self.H.__getInt__()
        self.H.__get_ack__()
        V = V_sum * 3.3 / 16 / 4095
        C = -ctime * 1e-6 / 1e4 / np.log(1 - V / 3.3)
        return V, C

    def get_capacitor_range(self):
        """
		Charges a capacitor connected to IN1 via a 20K resistor from a 3.3V source for a fixed interval
		Returns the capacitance calculated using the formula Vc = Vs(1-exp(-t/RC))
		This function allows an estimation of the parameters to be used with the :func:`get_capacitance` function.
		"""
        t = 10
        P = [1.5, 50e-12]
        for a in range(4):
            P = list(self.__get_capacitor_range__(50 * (10 ** a)))
            if (P[0] > 1.5):
                if a == 0 and P[0] > 3.28:  # pico farads range. Values will be incorrect using this method
                    P[1] = 50e-12
                break
        return P

    def get_capacitance(self):  # time in uS
        """
		measures capacitance of component connected between CAP and ground
		:return: Capacitance (F)
		Constant Current Charging
		.. math::
			Q_{stored} = C*V
			I_{constant}*time = C*V
			C = I_{constant}*time/V_{measured}
		Also uses Constant Voltage Charging via 20K resistor if required.
		"""
        GOOD_VOLTS = [2.5, 2.8]
        CT = 10
        CR = 1
        iterations = 0
        start_time = time.time()

        while (time.time() - start_time) < 1:
            # self.__print__('vals',CR,',',CT)
            if CT > 65000:
                self.__print__('CT too high')
                return self.capacitance_via_RC_discharge()
            V, C = self.__get_capacitance__(CR, 0, CT)
            # print(CR,CT,V,C)
            if CT > 30000 and V < 0.1:
                self.__print__('Capacitance too high for this method')
                return 0

            elif V > GOOD_VOLTS[0] and V < GOOD_VOLTS[1]:
                return C
            elif V < GOOD_VOLTS[0] and V > 0.01 and CT < 40000:
                if GOOD_VOLTS[0] / V > 1.1 and iterations < 10:
                    CT = int(CT * GOOD_VOLTS[0] / V)
                    iterations += 1
                    self.__print__('increased CT ', CT)
                elif iterations == 10:
                    return 0
                else:
                    return C
            elif V <= 0.1 and CR < 3:
                CR += 1
            elif CR == 3:
                self.__print__('Capture mode ')
                return self.capacitance_via_RC_discharge()

    def __get_capacitance__(self, current_range, trim, Charge_Time):  # time in uS
        self.__charge_cap__(0, 30000)
        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.GET_CAPACITANCE)
        self.H.__sendByte__(current_range)
        if (trim < 0):
            self.H.__sendByte__(int(31 - abs(trim) / 2) | 32)
        else:
            self.H.__sendByte__(int(trim / 2))
        self.H.__sendInt__(Charge_Time)
        time.sleep(Charge_Time * 1e-6 + .02)
        VCode = self.H.__getInt__()
        V = 3.3 * VCode / 4095
        self.H.__get_ack__()
        Charge_Current = self.currents[current_range] * (100 + trim) / 100.0
        if V:
            C = (Charge_Current * Charge_Time * 1e-6 / V - self.SOCKET_CAPACITANCE) / self.currentScalers[
                current_range]
        else:
            C = 0
        return V, C

    def get_temperature(self):
        """
		return the processor's temperature
		:return: Chip Temperature in degree Celcius
		"""
        cs = 3
        V = self.get_ctmu_voltage(0b11110, cs, 0)

        if cs == 1:
            return (646 - V * 1000) / 1.92  # current source = 1
        elif cs == 2:
            return (701.5 - V * 1000) / 1.74  # current source = 2
        elif cs == 3:
            return (760 - V * 1000) / 1.56  # current source = 3

    def get_ctmu_voltage(self, channel, Crange, tgen=1):
        """
		get_ctmu_voltage(5,2)  will activate a constant current source of 5.5uA on IN1 and then measure the voltage at the output.
		If a diode is used to connect IN1 to ground, the forward voltage drop of the diode will be returned. e.g. .6V for a 4148diode.
		If a resistor is connected, ohm's law will be followed within reasonable limits
		channel=5 for IN1
		CRange=0   implies 550uA
		CRange=1   implies 0.55uA
		CRange=2   implies 5.5uA
		CRange=3   implies 55uA
		:return: Voltage
		"""
        if channel == 'CAP': channel = 5

        self.H.__sendByte__(CP.COMMON)
        self.H.__sendByte__(CP.GET_CTMU_VOLTAGE)
        self.H.__sendByte__((channel) | (Crange << 5) | (tgen << 7))

        v = self.H.__getInt__()  # 16*voltage across the current source

        self.H.__get_ack__()
        V = 3.3 * v / 16 / 4095.
        return V
