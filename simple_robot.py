import numpy as np
from shapely.geometry import Point, box, Polygon
from shapely.affinity import translate, rotate

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