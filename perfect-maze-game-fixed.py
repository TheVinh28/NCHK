import pygame
import random
import sys
from collections import deque

# Khởi tạo pygame
pygame.init()

# Hằng số
CELL_SIZE = 40
WALL_THICKNESS = 4
BG_COLOR = (20, 20, 35)  # Màu nền tối
WALL_COLOR = (100, 100, 180)  # Màu tường xanh dương
PLAYER_COLOR = (255, 80, 80)  # Màu đỏ tươi cho người chơi
PATH_COLOR = (40, 40, 60)  # Màu đường đi tối
GOAL_COLOR = (80, 255, 120)  # Màu xanh lá cây
FONT_COLOR = (220, 220, 255)  # Màu chữ sáng
TRAIL_COLOR = (70, 70, 120, 100)  # Màu vết di chuyển với độ trong suốt

# Hiệu ứng
GLOW_COLOR = (120, 120, 255, 50)  # Màu phát sáng xung quanh người chơi

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {"N": True, "E": True, "S": True, "W": True}
        self.visited = False

    def get_neighbors(self, grid, width, height):
        neighbors = []
        # Bắc (N)
        if self.y > 0:
            neighbors.append(("N", grid[self.y - 1][self.x]))
        # Đông (E)
        if self.x < width - 1:
            neighbors.append(("E", grid[self.y][self.x + 1]))
        # Nam (S)
        if self.y < height - 1:
            neighbors.append(("S", grid[self.y + 1][self.x]))
        # Tây (W)
        if self.x > 0:
            neighbors.append(("W", grid[self.y][self.x - 1]))
        return neighbors

    def get_unvisited_neighbors(self, grid, width, height):
        return [(direction, neighbor) for direction, neighbor in self.get_neighbors(grid, width, height) if not neighbor.visited]

def remove_walls(current, next_cell, direction):
    # Loại bỏ tường giữa hai ô
    opposite = {"N": "S", "E": "W", "S": "N", "W": "E"}
    current.walls[direction] = False
    next_cell.walls[opposite[direction]] = False

def generate_perfect_maze(width, height):
    # Khởi tạo lưới các ô
    grid = [[Cell(x, y) for x in range(width)] for y in range(height)]
    
    # Thuật toán Recursive Backtracking
    stack = []
    current = grid[0][0]
    current.visited = True
    stack.append(current)
    
    while stack:
        current = stack[-1]
        unvisited_neighbors = current.get_unvisited_neighbors(grid, width, height)
        
        if unvisited_neighbors:
            direction, next_cell = random.choice(unvisited_neighbors)
            remove_walls(current, next_cell, direction)
            next_cell.visited = True
            stack.append(next_cell)
        else:
            stack.pop()
    
    # Tạo đường vào và ra
    grid[0][0].walls["W"] = False  # Lối vào (trái)
    grid[height-1][width-1].walls["E"] = False  # Lối ra (phải)
    
    return grid

def find_solution(grid, width, height):
    # Thuật toán BFS để tìm đường đi ngắn nhất
    start = (0, 0)
    end = (width-1, height-1)
    
    queue = deque([(start, [])])
    visited = set([start])
    
    while queue:
        (x, y), path = queue.popleft()
        current = grid[y][x]
        
        if (x, y) == end:
            return path + [(x, y)]  # Thêm vị trí cuối cùng vào đường đi
        
        # Kiểm tra tất cả các hướng có thể đi
        if not current.walls["N"] and y > 0 and (x, y-1) not in visited:
            visited.add((x, y-1))
            queue.append(((x, y-1), path + [(x, y)]))
            
        if not current.walls["E"] and x < width-1 and (x+1, y) not in visited:
            visited.add((x+1, y))
            queue.append(((x+1, y), path + [(x, y)]))
            
        if not current.walls["S"] and y < height-1 and (x, y+1) not in visited:
            visited.add((x, y+1))
            queue.append(((x, y+1), path + [(x, y)]))
            
        if not current.walls["W"] and x > 0 and (x-1, y) not in visited:
            visited.add((x-1, y))
            queue.append(((x-1, y), path + [(x, y)]))
    
    return []  # Không tìm thấy đường đi (không nên xảy ra trong mê cung hoàn hảo)

class MazeGame:
    def __init__(self, width, height):
        self.maze_width = width
        self.maze_height = height
        self.grid = generate_perfect_maze(width, height)
        self.screen_width = width * CELL_SIZE + WALL_THICKNESS
        self.screen_height = height * CELL_SIZE + WALL_THICKNESS
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Perfect Maze Game")
        
        # Tính toán kích thước đầy đủ cho các hình dáng
        self.cell_inner_size = CELL_SIZE - WALL_THICKNESS
        
        # Vị trí người chơi (bắt đầu tại lối vào)
        self.player_x = 0
        self.player_y = 0
        
        # Vị trí đích (lối ra)
        self.goal_x = width - 1
        self.goal_y = height - 1
        
        # Trạng thái trò chơi
        self.game_won = False
        self.moves = 0
        self.trail = []  # Lưu lại dấu vết di chuyển
        
        # Hiệu ứng
        self.glowing = True
        self.glow_radius = CELL_SIZE // 2
        
        # Tìm đường đi tối ưu
        self.solution = find_solution(self.grid, width, height)
        self.show_solution = False
        
        # Font để hiển thị thông báo
        self.font = pygame.font.SysFont('Arial', 20)
        self.big_font = pygame.font.SysFont('Arial', 36, bold=True)
        
        # Tạo surface cho hiệu ứng trong suốt
        self.trail_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.glow_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
    
    def draw_maze(self):
        self.screen.fill(BG_COLOR)
        self.trail_surface.fill((0, 0, 0, 0))  # Xóa vết đi cũ
        
        # Vẽ các ô và tường
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                cell = self.grid[y][x]
                cell_x = x * CELL_SIZE
                cell_y = y * CELL_SIZE
                
                # Vẽ ô
                pygame.draw.rect(
                    self.screen,
                    PATH_COLOR,
                    (cell_x + WALL_THICKNESS//2, cell_y + WALL_THICKNESS//2, 
                     self.cell_inner_size, self.cell_inner_size)
                )
                
                # Vẽ tường
                if cell.walls["N"]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (cell_x, cell_y),
                        (cell_x + CELL_SIZE, cell_y),
                        WALL_THICKNESS
                    )
                if cell.walls["E"]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (cell_x + CELL_SIZE, cell_y),
                        (cell_x + CELL_SIZE, cell_y + CELL_SIZE),
                        WALL_THICKNESS
                    )
                if cell.walls["S"]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (cell_x, cell_y + CELL_SIZE),
                        (cell_x + CELL_SIZE, cell_y + CELL_SIZE),
                        WALL_THICKNESS
                    )
                if cell.walls["W"]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (cell_x, cell_y),
                        (cell_x, cell_y + CELL_SIZE),
                        WALL_THICKNESS
                    )
        
        # Vẽ đích đến
        goal_x_pos = self.goal_x * CELL_SIZE + CELL_SIZE // 2
        goal_y_pos = self.goal_y * CELL_SIZE + CELL_SIZE // 2
        
        pygame.draw.rect(
            self.screen,
            GOAL_COLOR,
            (self.goal_x * CELL_SIZE + WALL_THICKNESS//2, 
             self.goal_y * CELL_SIZE + WALL_THICKNESS//2,
             self.cell_inner_size, self.cell_inner_size)
        )
        
        # Vẽ đường đi tối ưu nếu được kích hoạt
        if self.show_solution and self.solution:
            for x, y in self.solution:
                hint_x = x * CELL_SIZE + CELL_SIZE // 2
                hint_y = y * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(
                    self.screen,
                    (150, 150, 255, 180),
                    (hint_x, hint_y),
                    5
                )
        
        # Vẽ dấu vết di chuyển
        for x, y in self.trail:
            trail_x = x * CELL_SIZE + CELL_SIZE // 2
            trail_y = y * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(
                self.trail_surface,
                TRAIL_COLOR,
                (trail_x, trail_y),
                8
            )
        self.screen.blit(self.trail_surface, (0, 0))
        
        # Vẽ hiệu ứng phát sáng cho người chơi
        if self.glowing:
            self.glow_surface.fill((0, 0, 0, 0))
            player_x_center = self.player_x * CELL_SIZE + CELL_SIZE // 2
            player_y_center = self.player_y * CELL_SIZE + CELL_SIZE // 2
            
            for radius in range(self.glow_radius, 1, -5):
                alpha = 150 - radius * 2
                if alpha > 0:
                    pygame.draw.circle(
                        self.glow_surface,
                        (*GLOW_COLOR[:3], alpha),
                        (player_x_center, player_y_center),
                        radius
                    )
            self.screen.blit(self.glow_surface, (0, 0))
        
        # Vẽ người chơi (hình tròn)
        player_x_pos = self.player_x * CELL_SIZE + CELL_SIZE // 2
        player_y_pos = self.player_y * CELL_SIZE + CELL_SIZE // 2
        
        pygame.draw.circle(
            self.screen,
            PLAYER_COLOR,
            (player_x_pos, player_y_pos),
            self.cell_inner_size // 2 - 2
        )
        
        # Hiển thị số bước di chuyển
        moves_text = self.font.render(f"Bước đi: {self.moves}", True, FONT_COLOR)
        self.screen.blit(moves_text, (10, 10))
        
        # Hiển thị hướng dẫn
        hint_text = self.font.render("H: Hiện gợi ý | R: Chơi lại | ESC: Thoát", True, FONT_COLOR)
        hint_rect = hint_text.get_rect(bottomright=(self.screen_width - 10, self.screen_height - 10))
        self.screen.blit(hint_text, hint_rect)
        
        # Hiển thị thông báo chiến thắng
        if self.game_won:
            # Tạo nền mờ
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            win_text = self.big_font.render("Chúc mừng! Bạn đã chiến thắng!", True, (255, 255, 255))
            moves_info = self.font.render(f"Số bước đi: {self.moves}", True, (200, 200, 255))
            restart_text = self.font.render("Nhấn R để chơi lại", True, (180, 255, 180))
            
            win_rect = win_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 30))
            moves_rect = moves_info.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 10))
            restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 40))
            
            self.screen.blit(win_text, win_rect)
            self.screen.blit(moves_info, moves_rect)
            self.screen.blit(restart_text, restart_rect)
    
    def move_player(self, direction):
        if self.game_won:
            return
        
        cell = self.grid[self.player_y][self.player_x]
        
        # Kiểm tra xem có thể di chuyển theo hướng đó không (không có tường)
        if not cell.walls[direction]:
            # Lưu vị trí hiện tại vào dấu vết
            self.trail.append((self.player_x, self.player_y))
            if len(self.trail) > 50:  # Giới hạn độ dài vết đi
                self.trail.pop(0)
            
            # Di chuyển người chơi
            if direction == "N":
                self.player_y -= 1
            elif direction == "E":
                self.player_x += 1
            elif direction == "S":
                self.player_y += 1
            elif direction == "W":
                self.player_x -= 1
            
            self.moves += 1
            
            # Kiểm tra nếu người chơi đến đích
            if self.player_x == self.goal_x and self.player_y == self.goal_y:
                self.game_won = True
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.move_player("N")
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.move_player("S")
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.move_player("W")
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.move_player("E")
                    elif event.key == pygame.K_r:  # Khởi động lại trò chơi
                        self.__init__(self.maze_width, self.maze_height)
                    elif event.key == pygame.K_h:  # Bật/tắt gợi ý
                        self.show_solution = not self.show_solution
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # Cập nhật hiệu ứng phát sáng
            self.glow_radius = 25 + 5 * abs(pygame.time.get_ticks() % 1000 - 500) / 500
            
            # Vẽ mọi thứ
            self.draw_maze()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

# Hàm chính
def main():
    # Kích thước mê cung (có thể điều chỉnh)
    width, height = 15, 12
    game = MazeGame(width, height)
    game.run()

if __name__ == "__main__":
    main()
