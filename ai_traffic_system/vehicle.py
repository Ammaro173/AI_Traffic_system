class vehicle:
    def __init__(self, straight_direction, turn_direction, speed, gap):
        self.straight_direction = straight_direction  # vehicle directon depends on the value of self.green of the straight traffic light != 0 in traffic class object
        self.turn_direction = turn_direction
        self.speed = speed  # speed will be 0 when self.red != 0 , speed will != 0 when self.red = 0 // note: def Accelration
        self.gap = gap
