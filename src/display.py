#
#   The display class is used to show a pygame screen and render the drone and target on it.
#

import pygame
import math

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0,255,0)
DRONE_SIZE = 40  # Size of the drone square
MOTOR_SIZE = 20   # Size of the motor squares

class Display:
    def __init__(self, config: dict, title: str):
        self.width = config["display"]["width"]
        self.height = config["display"]["height"]
        self.update_frequency = config["display"]["update_frequency"]

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

    def _draw_start_point(self, drone):
        # Scale the position to the screen size
        #print(f"Start from display: {drone.start_position}")
        startx = drone.start_position[0]
        starty = drone.start_position[1]
        ax = startx * self.width/2 + self.width/2
        ay = starty * self.height/2 + self.height/2
        pygame.draw.circle(self.screen, GREEN, (ax, ay), 5)  # Green circle for point A

    def _draw_drone(self, drone):
        # Drone state
        state = drone.get_true_state()
        drone_x, _, drone_y, _, rotation, _ = state[:6]

        # drone_x and drone_y are (-1,1) so we need to scale them to the screen size
        drone_x = drone_x * self.width/2 + self.width/2
        drone_y = drone_y * self.height/2 + self.height/2

        drone_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Use SRCALPHA for transparency
        
        # Fill the surface with light gray pixels
        # drone_surface.fill((10, 10, 10))

        # Draw the drone rectangle on the surface
        drone_rect = pygame.Rect(self.width/2 - DRONE_SIZE/2, self.height/2 - DRONE_SIZE/2, DRONE_SIZE, DRONE_SIZE)
        pygame.draw.rect(drone_surface, WHITE, drone_rect)

        action = drone.last_action

        for i, motor in enumerate(drone.motors):
            motor_x, motor_y, _, _ = motor
            # Draw a line from the motor center to the drone center
            pygame.draw.line(drone_surface, WHITE, (motor_x * 100 + self.width/2, motor_y * 100 + self.height/2), (self.width/2, self.height/2), 10)

        for i, motor in enumerate(drone.motors):
            # Calculate the position to blit the motor triangle
            motor_x, motor_y, _, _ = motor

            motor_x_scaled = motor_x * 100 + self.width/2 - MOTOR_SIZE/2
            motor_y_scaled = motor_y * 100 + self.height/2 - MOTOR_SIZE

            # Create a surface for the motor
            motor_surface = pygame.Surface((MOTOR_SIZE, MOTOR_SIZE), pygame.SRCALPHA)  # Use SRCALPHA for transparency

            # Create a triangle for the motor
            color = GREEN if action[i] else RED
            motor_triangle = pygame.draw.polygon(motor_surface, color, [(0, MOTOR_SIZE), (MOTOR_SIZE/2, 0), (MOTOR_SIZE, MOTOR_SIZE)])

            # Create the number for the motor
            font = pygame.font.SysFont(None, 20)
            text_surface = font.render(str(i+1), False, (0, 0, 0)) 
            
            # Blit at the center
            text_x = MOTOR_SIZE/2 - text_surface.get_width()/2
            text_y = MOTOR_SIZE/2 - text_surface.get_height()/4

            motor_surface.blit(text_surface, (text_x, text_y))

            # Rotate the motor triangle
            motor_triangle = pygame.transform.rotate(motor_surface, (-motor[2])) # 0 degrees is right, 90 degrees is down

            # Blit the motor triangle onto the drone surface at the calculated position
            drone_surface.blit(motor_triangle, (motor_x_scaled, motor_y_scaled + MOTOR_SIZE/2))

        # Rotate the combined drone and motors surface
        rotation = rotation * 180 / math.pi
        rotated_drone_surface = pygame.transform.rotate(drone_surface, -rotation)

        # Calculate the center position for blitting
        blit_x = drone_x - rotated_drone_surface.get_width() / 2
        blit_y = drone_y - rotated_drone_surface.get_height() / 2

        # Draw the rotated drone surface on the screen
        self.screen.blit(rotated_drone_surface, (blit_x, blit_y))

    
    def _draw_state(self, drone):
        state = drone.get_true_state()
        font = pygame.font.SysFont(None, 24)
        y_offset = 0  # Starting y position for the first line of text
        x_offset = 20  # Starting x position for the first line of text
        line_height = 25  # Height of each line of text

        state_labels = ["X", "vX", "Y", "vY", "angle", "vAngle"]
        domain_labels = ["mass", "inertia", "gravity"]

        # State
        text = font.render("State:", True, WHITE)
        self.screen.blit(text, (0, y_offset))
        y_offset += line_height
    
        # Draw the state
        for label, value in zip(state_labels, state):
            text = font.render(f"{label}: {round(value, 2)}", True, WHITE)
            self.screen.blit(text, (x_offset, y_offset))
            y_offset += line_height
        
        # Domain parameters
        y_offset += line_height
        text = font.render("Domain parameters:", True, WHITE)
        self.screen.blit(text, (0, y_offset))
        y_offset += line_height

        for label, value in zip(domain_labels, state[6:-len(drone.motors)*2]):
            text = font.render(f"{label}: {round(value, 2)}", True, WHITE)
            self.screen.blit(text, (x_offset, y_offset))
            y_offset += line_height

        # Targets
        y_offset += line_height
        text = font.render("Targets:", True, WHITE)
        self.screen.blit(text, (0, y_offset))

        # Draw the target distances, defined as x and y times the number of targets
        # The targets come in pairs of 2, and they are the last 2*len(targets) elements of the state
        y_offset += line_height
        target_idx = len(state) - len(drone.targets)  # Starting index of targets in the state array
        for i in range(0, len(drone.targets), 2):
            x_target = state[target_idx + i]
            y_target = state[target_idx + i + 1]
            label = f"T{i//2 + 1}"
            text = font.render(f"{label}: ({round(x_target, 2)}, {round(y_target, 2)})", True, WHITE)
            self.screen.blit(text, (x_offset, y_offset))
            y_offset += line_height
        

    def _draw_agent_state(self, agent):
        font = pygame.font.SysFont(None, 24)
        y_offset = 20
        x_offset = 20

        text = font.render(f"Game: {agent.n_games}", True, WHITE)
        self.screen.blit(text, (self.width - text.get_width() - x_offset, y_offset))

        y_offset += 25

        text = font.render(f"Epsilon: {round(agent.epsilon*100, 1)}", True, WHITE)
        self.screen.blit(text, (self.width - text.get_width() - x_offset, y_offset))


    def _draw_action(self, action):
        # Draw at the bottom left
        font = pygame.font.SysFont(None, 24)
        y_offset = self.height - 150
        line_height = 25

        text = font.render("Action:", True, WHITE)
        self.screen.blit(text, (0, y_offset))
        y_offset += line_height

        for i, value in enumerate(action):
            text = font.render(f"{i}: {round(value * 100)}", True, WHITE)
            self.screen.blit(text, (0, y_offset))
            y_offset += line_height

        
    def _draw_targets(self, drone):
        for i in range(0, len(drone.targets), 2):
            target_x = drone.targets[i] * self.width/2 + self.width/2
            target_y = drone.targets[i+1] * self.height/2 + self.height/2

            cross_size = 10  # Size of the cross arms
            pygame.draw.line(self.screen, RED, (target_x - cross_size, target_y - cross_size), (target_x + cross_size, target_y + cross_size), 2)
            pygame.draw.line(self.screen, RED, (target_x + cross_size, target_y - cross_size), (target_x - cross_size, target_y + cross_size), 2)

    def _draw_simulation_stats(self, drone):
        # On the right hand side of the screen
        # Draw the current frame, the frames without target, the last reward
        font = pygame.font.SysFont(None, 24)
        y_offset = 20
        x_offset = 20

        text = font.render(f"Frame: {drone.episode_step}", True, WHITE)
        self.screen.blit(text, (self.width - text.get_width() - x_offset, y_offset))
        y_offset += 25

        text = font.render(f"Frames without target: {drone.episodes_without_target}", True, WHITE)
        self.screen.blit(text, (self.width - text.get_width() - x_offset, y_offset))
        y_offset += 25

        text = font.render(f"Reward: {round(drone.last_reward, 2)}", True, WHITE)
        self.screen.blit(text, (self.width - text.get_width() - x_offset, y_offset))
        y_offset += 25

    def update(self, drone):
        if not drone.enable_rendering:
            return
        self.clock.tick(60)
        self.screen.fill(BLACK)
        self._draw_drone(drone)
        self._draw_targets(drone)
        
        self._draw_start_point(drone)
        self._draw_state(drone)
        self._draw_simulation_stats(drone)
        pygame.display.flip()

        # Handle the event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def close(self):
        pygame.quit()