import numpy as np
from shapely.geometry import Point, box, Polygon
from shapely.affinity import translate, rotate
import matplotlib.pyplot as plt

class SimpleRobot():
    def __init__(self, pos_x, pos_y, phi):
        self.set_robot_position(pos_x, pos_y, phi)
        self.wheel_distance = 2.0 #distance between 2 wheels 
        self.wheel_radius = 0.8 
        self.init_robot_body = []
        self.init_robot_body.append(Point(0,0).buffer(1.5)) #outer circle body
        self.init_robot_body.append(box(-1.1, -self.wheel_radius, -0.9, self.wheel_radius)) #left wheel
        self.init_robot_body.append(box( 0.9, -self.wheel_radius,  1.1, self.wheel_radius)) #right wheel
        self.init_robot_body.append(Polygon([(-0.6, 1),(0, 1.3),(0.6, 1)]))
        
        # Robot sensor
        self.camera_near_clipping = 1.5 #in meters
        self.camera_far_clipping  = 3.5 #in meters
        self.sensing_range        = self.camera_far_clipping - self.camera_near_clipping
        self.camera_fov_angle     = 90.0# degree
        self.n_direction          = 5
        self.direction_list       = np.linspace(-self.camera_fov_angle, self.camera_fov_angle, self.n_direction+1)
        self.obstacle_map = []
        self.obstacle_distances = np.ones((self.n_direction))*self.camera_far_clipping
        for i in range(self.n_direction):
            self.obstacle_map.append(Polygon([
                                    [self.camera_near_clipping*np.sin(np.radians(self.direction_list[i])),  self.camera_near_clipping*np.cos(np.radians(self.direction_list[i]))],
                                    [self.camera_near_clipping*np.sin(np.radians(self.direction_list[i+1])),self.camera_near_clipping*np.cos(np.radians(self.direction_list[i+1]))],
                                    [self.camera_far_clipping*np.sin(np.radians(self.direction_list[i+1])),self.camera_far_clipping*np.cos(np.radians(self.direction_list[i+1]))],
                                    [self.camera_far_clipping*np.sin(np.radians(self.direction_list[i])),  self.camera_far_clipping*np.cos(np.radians(self.direction_list[i]))]]))
        #Rotating for init
        angle_correction = -np.pi/2
        for i in range(len(self.init_robot_body)):
            self.init_robot_body[i] = rotate(self.init_robot_body[i], angle_correction, use_radians=True, origin=Point(0, 0))
        for i in range(len(self.obstacle_map)):
            self.obstacle_map[i] = rotate(self.obstacle_map[i], angle_correction, use_radians=True, origin=Point(0, 0))
            
    def set_robot_position(self, pos_x, pos_y, phi):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.phi = phi
        
    def move(self, linear_speed, angular_speed, timestep):
        self.pos_x += linear_speed*np.cos(self.phi)*timestep
        self.pos_y += linear_speed*np.sin(self.phi)*timestep
        self.phi   += angular_speed*timestep
        return self.pos_x, self.pos_y, self.phi
    
    def get_parts(self, part_list):
        moved_parts = []
        for part in part_list:
            rotated_part =  rotate(part, self.phi, use_radians=True, origin=Point(0, 0))
            translated_part = translate(rotated_part, self.pos_x, self.pos_y)
            moved_parts.append(translated_part)
        return moved_parts
    
    def get_robot_body(self):
        self.robot_body = self.get_parts(self.init_robot_body)
        return self.robot_body
    
    def get_robot_sensors(self):
        self.robot_sensors = self.get_parts(self.obstacle_map)
        return self.robot_sensors
    
class SimpleRobotEnv():
    def __init__(self):
        # timestep
        self.dt = .1

        self.fig = None
        self.ax = None

        self.xlim = [-15, 15]
        self.ylim = [-2.5, 27.5]
        
        self.obstacles = []
        outer_wall_thick = 0.001
        self.obstacles.append(box(self.xlim[0], self.ylim[0], self.xlim[1]+outer_wall_thick, self.ylim[0]+outer_wall_thick)) #outer wall
        self.obstacles.append(box(self.xlim[0], self.ylim[0], self.xlim[0]+outer_wall_thick, self.ylim[1]+outer_wall_thick)) #outer wall
        self.obstacles.append(box(self.xlim[0], self.ylim[1], self.xlim[1]+outer_wall_thick, self.ylim[1]+outer_wall_thick)) #outer wall
        self.obstacles.append(box(self.xlim[1], self.ylim[0], self.xlim[1]+outer_wall_thick, self.ylim[1]+outer_wall_thick)) #outer wall
        
        self.obstacles.append(Polygon([(0,2.5),(-5,5),(5,5)]))
        self.obstacles.append(box(-12,13,-5,14))
        self.obstacles.append(box(  0,20,10,21))
        self.obstacles.append(Point(3,12.5).buffer(2))
        
        self.target_list = [[-10,2.5], [10,7.5], [-10, 20], [10,25]]
        
    def render(self, hold=False):
        if self.fig is None:
            assert self.ax is None
            self.fig, self.ax = plt.subplots()
        if not self.ax.lines:
            self.ax.plot([], [], "C0", linewidth=3)
            for _ in range(4):
                self.ax.plot([], [], "C1", linewidth=3)
            self.ax.plot([], [], "C2o", markersize=6)

            self.ax.grid()
            self.ax.set_xlim(self.xlim)
            self.ax.set_aspect("equal")
            self.ax.set_ylim(self.ylim)
        
            for obstacle in self.obstacles:
                x,y = obstacle.exterior.xy
                self.ax.plot(x, y)
        
        self.ax.relim()
        self.ax.autoscale_view()
        plt.draw()
        plt.pause(1e-07)
        if hold:
            plt.show()


    
    