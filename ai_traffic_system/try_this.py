import random
import time
import threading
import pygame
import sys


# Default values of signal timers
defaultGreen = {0: 9, 1: 3, 2: 9, 3: 3}
defaultRed = 25
defaultYellow = 1

signals = []
noOfSignals = 4
currentGreen = 0  # Indicates which signal is green currently

nextGreen = (
    currentGreen + 1
) % noOfSignals  # Indicates which signal will turn green next

currentYellow = 0  # Indicates whether yellow signal is on or off initial condition

speeds = {"car": 5}  # average speeds of vehicles


# Coordinates of vehicles' start
x = {
    "right": [0, 0, 0],
    "down": [542, 563, 637],
    "left": [1400, 1400, 1400],
    "up": [680, 723, 819],
}
y = {
    "right": [380, 410, 465],
    "down": [0, 0, 0],
    "left": [258, 315, 365],
    "up": [800, 800, 800],
}

vehicles = {
    "right": {0: [], 1: [], 2: [], "crossed": 0},
    "down": {0: [], 1: [], 2: [], "crossed": 0},
    "left": {0: [], 1: [], 2: [], "crossed": 0},
    "up": {0: [], 1: [], 2: [], "crossed": 0},
}
vehicleTypes = {0: "car"}
directionNumbers = {0: "right", 1: "down", 2: "left", 3: "up"}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(400, 430), (690, 110), (970, 305), (690, 610)]
signalTimerCoods = [(450, 480), (760, 160), (1020, 355), (740, 660)]

# Coordinates of stop lines
stopLines = {"right": 350, "down": 197, "left": 1050, "up": 603}
defaultStop = {"right": 340, "down": 187, "left": 1060, "up": 610}

# Gap between vehicles
stoppingGap = 25  # stopping gap
movingGap = 25  # moving gap

# set allowed vehicle types here

allowedVehicleTypes = {"car": True}

allowedVehicleTypesList = []

vehiclesTurned = {
    "right": {1: [], 2: []},
    "down": {1: [], 2: []},
    "left": {1: [], 2: []},
    "up": {1: [], 2: []},
}
vehiclesNotTurned = {
    "right": {1: [], 2: []},
    "down": {1: [], 2: []},
    "left": {1: [], 2: []},
    "up": {1: [], 2: []},
}

rotationAngle = 3  # rotate & drifting facrtor; 2 or 3 is best


mid = {
    "right": {"x": 560, "y": 465},
    "down": {"x": 560, "y": 310},
    "left": {"x": 860, "y": 310},
    "up": {"x": 815, "y": 495},
}
# set random or default green signal time here
randomGreenSignalTimer = False
# set random green signal time range here
randomGreenSignalTimerRange = [10, 20]

pygame.init()
simulation = pygame.sprite.Group()


class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        # self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "ai_traffic_system/images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)

        if (
            len(vehicles[direction][lane]) > 1
            and vehicles[direction][lane][self.index - 1].crossed == 0
        ):
            if direction == "right":
                self.stop = vehicles[direction][lane][self.index - 1].stop
                -vehicles[direction][lane][self.index - 1].image.get_rect().width
                -stoppingGap
            elif direction == "left":
                self.stop = vehicles[direction][lane][self.index - 1].stop
                +vehicles[direction][lane][self.index - 1].image.get_rect().width
                +stoppingGap
            elif direction == "down":
                self.stop = vehicles[direction][lane][self.index - 1].stop
                -vehicles[direction][lane][self.index - 1].image.get_rect().height
                -stoppingGap
            elif direction == "up":
                self.stop = vehicles[direction][lane][self.index - 1].stop
                +vehicles[direction][lane][self.index - 1].image.get_rect().height
                +stoppingGap
        else:
            self.stop = defaultStop[direction]

        # Set new starting and stopping coordinate
        if direction == "right":
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif direction == "left":
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif direction == "down":
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif direction == "up":
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):

        if self.direction == "right":
            if (
                self.crossed == 0
                and self.x + self.image.get_rect().width > stopLines[self.direction]
            ):
                self.crossed = 1
                vehicles[self.direction]["crossed"] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = (
                        len(vehiclesNotTurned[self.direction][self.lane]) - 1
                    )
            if self.willTurn == 1:
                if self.lane == 1:
                    if (
                        self.crossed == 0
                        or self.x + self.image.get_rect().width
                        < stopLines[self.direction] + 365
                    ):
                        if (
                            self.x + self.image.get_rect().width <= self.stop
                            or (currentGreen == 0 and currentYellow == 0)
                            or self.crossed == 1
                        ) and (
                            self.index == 0
                            or self.x + self.image.get_rect().width
                            < (
                                vehicles[self.direction][self.lane][self.index - 1].x
                                - movingGap
                            )
                            or vehicles[self.direction][self.lane][
                                self.index - 1
                            ].turned
                            == 1
                        ):
                            self.x += self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(
                                self.originalImage, self.rotateAngle
                            )
                            self.x += 2.4  # 2.4 drift factor
                            self.y -= 2.8  # 2.8
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = (
                                    len(vehiclesTurned[self.direction][self.lane]) - 1
                                )
                        else:
                            if self.crossedIndex == 0 or (
                                self.y
                                > (
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ].y
                                    + vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ]
                                    .image.get_rect()
                                    .height
                                    + movingGap
                                )
                            ):
                                self.y -= self.speed
                elif self.lane == 2:
                    if (
                        self.crossed == 0
                        or self.x + self.image.get_rect().width
                        < mid[self.direction]["x"]
                    ):
                        if (
                            self.x + self.image.get_rect().width <= self.stop
                            or (currentGreen == 0 and currentYellow == 0)
                            or self.crossed == 1
                        ) and (
                            self.index == 0
                            or self.x + self.image.get_rect().width
                            < (
                                vehicles[self.direction][self.lane][self.index - 1].x
                                - movingGap
                            )
                            or vehicles[self.direction][self.lane][
                                self.index - 1
                            ].turned
                            == 1
                        ):
                            self.x += self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(
                                self.originalImage, -self.rotateAngle
                            )
                            self.x += 2
                            self.y += 1.8
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                            self.crossedIndex = (
                                len(vehiclesTurned[self.direction][self.lane]) - 1
                            )
                        else:
                            if self.crossedIndex == 0 or (
                                (self.y + self.image.get_rect().height)
                                < (
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ].y
                                    - movingGap
                                )
                            ):
                                self.y += self.speed
            else:
                if self.crossed == 0:
                    if (
                        self.x + self.image.get_rect().width <= self.stop
                        or (currentGreen == 0 and currentYellow == 0)
                    ) and (
                        self.index == 0
                        or self.x + self.image.get_rect().width
                        < (
                            vehicles[self.direction][self.lane][self.index - 1].x
                            - movingGap
                        )
                    ):
                        self.x += self.speed
                else:
                    if (self.crossedIndex == 0) or (
                        self.x + self.image.get_rect().width
                        < (
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1
                            ].x
                            - movingGap
                        )
                    ):
                        self.x += self.speed
        elif self.direction == "down":
            if (
                self.crossed == 0
                and self.y + self.image.get_rect().height > stopLines[self.direction]
            ):
                self.crossed = 1
                vehicles[self.direction]["crossed"] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = (
                        len(vehiclesNotTurned[self.direction][self.lane]) - 1
                    )
            if self.willTurn == 1:
                if self.lane == 2:
                    if (
                        self.crossed == 0
                        or self.y + self.image.get_rect().height
                        < stopLines[self.direction] + 210
                    ):
                        if (
                            self.y + self.image.get_rect().height <= self.stop
                            or (currentGreen == 1 and currentYellow == 0)
                            or self.crossed == 1
                        ) and (
                            self.index == 0
                            or self.y + self.image.get_rect().height
                            < (
                                vehicles[self.direction][self.lane][self.index - 1].y
                                - movingGap
                            )
                            or vehicles[self.direction][self.lane][
                                self.index - 1
                            ].turned
                            == 1
                        ):
                            self.y += self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(
                                self.originalImage, self.rotateAngle
                            )
                            self.x += 1.2
                            self.y += 1.8
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = (
                                    len(vehiclesTurned[self.direction][self.lane]) - 1
                                )
                        else:
                            if self.crossedIndex == 0 or (
                                (self.x + self.image.get_rect().width)
                                < (
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ].x
                                    - movingGap
                                )
                            ):
                                self.x += self.speed
                elif self.lane == 1:
                    if (
                        self.crossed == 0
                        or self.y + self.image.get_rect().height
                        < mid[self.direction]["y"]
                    ):
                        if (
                            self.y + self.image.get_rect().height <= self.stop
                            or (currentGreen == 1 and currentYellow == 0)
                            or self.crossed == 1
                        ) and (
                            self.index == 0
                            or self.y + self.image.get_rect().height
                            < (
                                vehicles[self.direction][self.lane][self.index - 1].y
                                - movingGap
                            )
                            or vehicles[self.direction][self.lane][
                                self.index - 1
                            ].turned
                            == 1
                        ):
                            self.y += self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(
                                self.originalImage, -self.rotateAngle
                            )
                            self.x -= 2.5
                            self.y += 2
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = (
                                    len(vehiclesTurned[self.direction][self.lane]) - 1
                                )
                        else:
                            if self.crossedIndex == 0 or (
                                self.x
                                > (
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ].x
                                    + vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ]
                                    .image.get_rect()
                                    .width
                                    + movingGap
                                )
                            ):
                                self.x -= self.speed
            else:
                if self.crossed == 0:
                    if (
                        self.y + self.image.get_rect().height <= self.stop
                        or (currentGreen == 1 and currentYellow == 0)
                    ) and (
                        self.index == 0
                        or self.y + self.image.get_rect().height
                        < (
                            vehicles[self.direction][self.lane][self.index - 1].y
                            - movingGap
                        )
                    ):
                        self.y += self.speed
                else:
                    if (self.crossedIndex == 0) or (
                        self.y + self.image.get_rect().height
                        < (
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1
                            ].y
                            - movingGap
                        )
                    ):
                        self.y += self.speed
        elif self.direction == "left":
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]["crossed"] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = (
                        len(vehiclesNotTurned[self.direction][self.lane]) - 1
                    )
            if self.willTurn == 1:
                if self.lane == 2:
                    if self.crossed == 0 or self.x > stopLines[self.direction] - 440:
                        if (
                            self.x >= self.stop
                            or (currentGreen == 2 and currentYellow == 0)
                            or self.crossed == 1
                        ) and (
                            self.index == 0
                            or self.x
                            > (
                                vehicles[self.direction][self.lane][self.index - 1].x
                                + vehicles[self.direction][self.lane][self.index - 1]
                                .image.get_rect()
                                .width
                                + movingGap
                            )
                            or vehicles[self.direction][self.lane][
                                self.index - 1
                            ].turned
                            == 1
                        ):
                            self.x -= self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(
                                self.originalImage, self.rotateAngle
                            )
                            self.x -= 1
                            self.y += 1.2
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = (
                                    len(vehiclesTurned[self.direction][self.lane]) - 1
                                )
                        else:
                            if self.crossedIndex == 0 or (
                                (self.y + self.image.get_rect().height)
                                < (
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ].y
                                    - movingGap
                                )
                            ):
                                self.y += self.speed
                elif self.lane == 1:
                    if self.crossed == 0 or self.x > mid[self.direction]["x"]:
                        if (
                            self.x >= self.stop
                            or (currentGreen == 2 and currentYellow == 0)
                            or self.crossed == 1
                        ) and (
                            self.index == 0
                            or self.x
                            > (
                                vehicles[self.direction][self.lane][self.index - 1].x
                                + vehicles[self.direction][self.lane][self.index - 1]
                                .image.get_rect()
                                .width
                                + movingGap
                            )
                            or vehicles[self.direction][self.lane][
                                self.index - 1
                            ].turned
                            == 1
                        ):
                            self.x -= self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(
                                self.originalImage, -self.rotateAngle
                            )
                            self.x -= 1.8
                            self.y -= 2.5
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = (
                                    len(vehiclesTurned[self.direction][self.lane]) - 1
                                )
                        else:
                            if self.crossedIndex == 0 or (
                                self.y
                                > (
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ].y
                                    + vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ]
                                    .image.get_rect()
                                    .height
                                    + movingGap
                                )
                            ):
                                self.y -= self.speed
            else:
                if self.crossed == 0:
                    if (
                        self.x >= self.stop
                        or (currentGreen == 2 and currentYellow == 0)
                    ) and (
                        self.index == 0
                        or self.x
                        > (
                            vehicles[self.direction][self.lane][self.index - 1].x
                            + vehicles[self.direction][self.lane][self.index - 1]
                            .image.get_rect()
                            .width
                            + movingGap
                        )
                    ):
                        self.x -= self.speed
                else:
                    if (self.crossedIndex == 0) or (
                        self.x
                        > (
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1
                            ].x
                            + vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1
                            ]
                            .image.get_rect()
                            .width
                            + movingGap
                        )
                    ):
                        self.x -= self.speed
        elif self.direction == "up":
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]["crossed"] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = (
                        len(vehiclesNotTurned[self.direction][self.lane]) - 1
                    )
            if self.willTurn == 1:
                if self.lane == 1:
                    if self.crossed == 0 or self.y > stopLines[self.direction] - 200:
                        if (
                            self.y >= self.stop
                            or (currentGreen == 3 and currentYellow == 0)
                            or self.crossed == 1
                        ) and (
                            self.index == 0
                            or self.y
                            > (
                                vehicles[self.direction][self.lane][self.index - 1].y
                                + vehicles[self.direction][self.lane][self.index - 1]
                                .image.get_rect()
                                .height
                                + movingGap
                            )
                            or vehicles[self.direction][self.lane][
                                self.index - 1
                            ].turned
                            == 1
                        ):
                            self.y -= self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(
                                self.originalImage, self.rotateAngle
                            )
                            self.x -= 2
                            self.y -= 1.2
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = (
                                    len(vehiclesTurned[self.direction][self.lane]) - 1
                                )
                        else:
                            if self.crossedIndex == 0 or (
                                self.x
                                > (
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ].x
                                    + vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ]
                                    .image.get_rect()
                                    .width
                                    + movingGap
                                )
                            ):
                                self.x -= self.speed
                elif self.lane == 2:
                    if self.crossed == 0 or self.y > mid[self.direction]["y"]:
                        if (
                            self.y >= self.stop
                            or (currentGreen == 3 and currentYellow == 0)
                            or self.crossed == 1
                        ) and (
                            self.index == 0
                            or self.y
                            > (
                                vehicles[self.direction][self.lane][self.index - 1].y
                                + vehicles[self.direction][self.lane][self.index - 1]
                                .image.get_rect()
                                .height
                                + movingGap
                            )
                            or vehicles[self.direction][self.lane][
                                self.index - 1
                            ].turned
                            == 1
                        ):
                            self.y -= self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(
                                self.originalImage, -self.rotateAngle
                            )
                            self.x += 1
                            self.y -= 1
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = (
                                    len(vehiclesTurned[self.direction][self.lane]) - 1
                                )
                        else:
                            if self.crossedIndex == 0 or (
                                self.x
                                < (
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ].x
                                    - vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1
                                    ]
                                    .image.get_rect()
                                    .width
                                    - movingGap
                                )
                            ):
                                self.x += self.speed
            else:
                if self.crossed == 0:
                    if (
                        self.y >= self.stop
                        or (currentGreen == 3 and currentYellow == 0)
                    ) and (
                        self.index == 0
                        or self.y
                        > (
                            vehicles[self.direction][self.lane][self.index - 1].y
                            + vehicles[self.direction][self.lane][self.index - 1]
                            .image.get_rect()
                            .height
                            + movingGap
                        )
                    ):
                        self.y -= self.speed
                else:
                    if (self.crossedIndex == 0) or (
                        self.y
                        > (
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1
                            ].y
                            + vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1
                            ]
                            .image.get_rect()
                            .height
                            + movingGap
                        )
                    ):
                        self.y -= self.speed


# Initialization of signals with default values
def initialize():
    minTime = randomGreenSignalTimerRange[0]
    maxTime = randomGreenSignalTimerRange[1]
    if randomGreenSignalTimer:
        ts1 = TrafficSignal(0, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts1)
        ts2 = TrafficSignal(
            ts1.red + ts1.yellow + ts1.green,
            defaultYellow,
            random.randint(minTime, maxTime),
        )
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts4)
    else:
        ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
        signals.append(ts4)
    repeat()


def repeat():
    global currentGreen, currentYellow, nextGreen
    while (
        signals[currentGreen].green > 0
    ):  # while the timer of current green signal is not zero
        updateValues()
        time.sleep(
            1
        )  # sleep for 1 seconds following real Time ratios ! , if you give 0.5 sec time ratio will be doubled
    currentYellow = 1  # set yellow signal on
    # reset stop coordinates of lanes and vehicles
    for i in range(0, 3):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while (
        signals[currentGreen].yellow > 0
    ):  # while the timer of current yellow signal is not zero
        updateValues()
        time.sleep(
            1
        )  # sleep for 1 seconds following real Time ratios ! , if you give 0.5 sec time ratio will be doubled
    currentYellow = 0  # set yellow signal off

    # reset all signal times of current signal to default/random times
    if randomGreenSignalTimer:
        signals[currentGreen].green = random.randint(
            randomGreenSignalTimerRange[0], randomGreenSignalTimerRange[1]
        )
    else:
        signals[currentGreen].green = defaultGreen[currentGreen]
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    currentGreen = nextGreen  # set next signal as green signal
    nextGreen = (currentGreen + 1) % noOfSignals  # set next green signal
    signals[nextGreen].red = (
        signals[currentGreen].yellow + signals[currentGreen].green
    )  # set the red time of next to next signal as (yellow time + green time) of next signal
    repeat()


# Update values of the signal timers after every second
def updateValues():
    for i in range(0, noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1


# Generating vehicles in the simulation
def generateVehicles():

    while True:
        vehicle_type = random.choice(allowedVehicleTypesList)
        lane_number = random.randint(1, 2)
        will_turn = 0

        if lane_number == 1:
            temp = random.randint(0, 99)
            if temp < 35:
                will_turn = 1
        elif lane_number == 2:
            temp = random.randint(0, 99)
            if temp < 35:
                will_turn = 1

        # temp1 = random.randint(0,11)
        # temp2 = random.randint(12,31)
        # temp3 = random.randint(32, 63)
        # temp4 = random.randint(64, 105)
        # temp = random.randint(0, 99)
        temp = random.randint(0, 100)

        direction_number = 0
        # dist = [25, 50, 75, 105]
        dist = [1, 5, 60, 101]
        if temp < dist[0]:
            direction_number = 1  # west to east (Right)
            # count_Leg1 += 1
        elif temp < dist[1]:
            direction_number = 3  # north to south (Down)
            # count_Leg2 += 1
        elif temp < dist[2]:
            direction_number = 0  # east to west  (Left)
        elif temp < dist[3]:
            direction_number = 2  # south to north (Up)
        Vehicle(
            lane_number,
            vehicleTypes[vehicle_type],
            direction_number,
            directionNumbers[direction_number],
            will_turn,
        )
        # y5=Vehicle
        # y4 = []
        # y4.append(y5)
        # print(y4)
        time.sleep(0.2)
        # flow_sum += 1


class Main:
    global allowedVehicleTypesList
    i = 0
    for vehicleType in allowedVehicleTypes:
        if allowedVehicleTypes[vehicleType]:
            allowedVehicleTypesList.append(i)
        i += 1
    thread1 = threading.Thread(
        name="initialization", target=initialize, args=()
    )  # initialization
    thread1.daemon = True
    thread1.start()

    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load("ai_traffic_system/images/intersection2.png")
    # background = pygame.transform.scale(background, (1600, 920))
    # background = pygame.transform.scale(background, (1400, 800)) OR Resize with google`s help
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load("ai_traffic_system/images/signals/red.png")
    yellowSignal = pygame.image.load("ai_traffic_system/images/signals/yellow.png")
    greenSignal = pygame.image.load("ai_traffic_system/images/signals/green.png")
    font = pygame.font.Font(None, 30)
    thread2 = threading.Thread(
        name="generateVehicles", target=generateVehicles, args=()
    )  # Generating vehicles
    # thread3 = threading.Thread(
    #     name="generateVehicles", target=generateVehicles, args=()
    # )
    # thread4 = threading.Thread(
    #     name="generateVehicles", target=generateVehicles, args=()
    # )
    thread2.daemon = True
    thread2.start()
    # thread3.start()
    # thread4.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background, (0, 0))  # display background in simulation
        for i in range(
            0, noOfSignals
        ):  # display signal and set timer according to current status: green, yellow, or red
            if i == currentGreen:
                if currentYellow == 1:
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                signals[i].signalText = signals[i].red
                screen.blit(redSignal, signalCoods[i])
                if signals[i].red <= 10:
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["", "", "", ""]

        # display signal timer
        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])

        # display the vehicles
        for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()
        # updateValues() update Values of TrafficSignal Timers
        # time.sleep(0.5) # will break the code dont use  it here :D
        # print(signals[0].green)


Main()
