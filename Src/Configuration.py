from Src.Constants import *

class Configuration():
    
    def __init__(self, **kwargs) -> None:
        self.WEIGHT_EMP = kwargs.get(c_weight_emp, 165.0) # kg
        self.WEIGHT_FUEL = kwargs.get(c_weight_fuel, 420.0)  # kg
        self.WEIGHT_FULL = self.WEIGHT_EMP + self.WEIGHT_FUEL # kg
        self.MAIN_ENG_F = kwargs.get(c_main_eng_f, 430.0)  # N
        self.SECOND_ENG_F = kwargs.get(c_second_eng_f, 25.0)  # N
        self.MAIN_BURN = kwargs.get(c_main_burn, 0.15)  # liter per sec, 12 liter per m'
        self.SECOND_BURN = kwargs.get(c_second_burn, 0.009)  # liter per sec 0.6 liter per m'
        self.ALL_BURN = self.MAIN_BURN + 8 * self.SECOND_BURN
        # self.dt = kwargs.get(c_time_change, 1.0)  # sec
        self.vs = kwargs.get(c_vertical_speed, 24.8)
        self.hs = kwargs.get(c_horizontal_speed, 932)
        self.angle = kwargs.get(c_angle, 58.3)  # zero is vertical (as in landing)
        self.lat = kwargs.get(c_latitude, 181 * 1000) # horizontal distance from target
        self.alt = kwargs.get(c_altitude, 13748)  # 2:25:40 (as in the simulation) # https://www.youtube.com/watch?v=JJ0VfRL9AMs
        self.acc = kwargs.get(c_acceleration, 0)  # Acceleration rate (m/s^2)
        self.fuel = kwargs.get(c_fuel, 121)  #     
        self.weight = self.WEIGHT_EMP + self.fuel # initial weight
        self.thrust = kwargs.get(c_engine_power, 0.7)  # engine power rate (in the range [0,1]), higher = more braking power
        self.is_player = False
        self.time = 0

    def update(self, **kwargs):
        valid_attributes = set(vars(self).keys())
        for key, value in kwargs.items():
            if key is c_dt: # special case for time change
                setattr(self,c_time, self.time + value)
            if key in valid_attributes:
                setattr(self, key, value)

    def save(self, path = None) -> None:
        '''
            if no path is provided default is CWD!
        '''
        pass

    def load(self, path = None) -> None:
        
        '''
            if no path is provided default is CWD!
        '''
        pass