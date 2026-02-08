"""
Графический интерфейс для игры с шариками (pygame-ce, совместим с Python 3.14).
Использует logic.py для движения, столкновений и смешивания цветов.
"""

import pygame
import sys

from logic import GameLogic

# ============== НАСТРОЙКИ (можно менять в начале кода) ==============
START_BALLS_COUNT = 70         # Стартовое количество шариков
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
DELETE_ZONE_HEIGHT = 60         # Высота зоны удаления внизу (в пикселях)
FPS = 60
# =====================================================================


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Шарики — зажми ЛКМ: всасывание, отпусти: выпуск")
    clock = pygame.time.Clock()

    game = GameLogic(
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
        delete_zone_height=DELETE_ZONE_HEIGHT,
    )
    for _ in range(START_BALLS_COUNT):
        game.add_ball()

    font = pygame.font.Font(None, 28)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.set_mouse_pressed(True)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    game.set_mouse_pressed(False)
                    game.release_ball_from_inventory(*pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEMOTION:
                game.set_mouse_position(*event.pos)

        game.update(dt)

        screen.fill((255, 255, 255))

        dz_x, dz_y, dz_w, dz_h = game.get_delete_zone_bounds()
        pygame.draw.rect(screen, (255, 200, 200), (dz_x, dz_y, dz_w, dz_h))
        pygame.draw.rect(screen, (220, 100, 100), (dz_x, dz_y, dz_w, dz_h), 2)
        label_dz = font.render("Зона удаления — шарики исчезают", True, (150, 50, 50))
        screen.blit(label_dz, (dz_x + 10, dz_y + dz_h // 2 - label_dz.get_height() // 2))

        if game.mouse_pressed:
            mx, my = game.mouse_x, game.mouse_y
            r = game.suction_radius
            suction_surface = pygame.Surface((int(r * 2), int(r * 2)))
            suction_surface.set_alpha(60)
            pygame.draw.circle(suction_surface, (100, 150, 255), (int(r), int(r)), int(r))
            screen.blit(suction_surface, (int(mx - r), int(my - r)))
            pygame.draw.circle(screen, (80, 120, 200), (int(mx), int(my)), int(r), 2)

        for ball in game.get_balls():
            pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), int(ball.radius))
            pygame.draw.circle(screen, (0, 0, 0), (int(ball.x), int(ball.y)), int(ball.radius), 1)

        inv_count = len(game.get_inventory())
        balls_count = len(game.get_balls())
        screen.blit(font.render(f"В инвентаре: {inv_count}", True, (50, 50, 150)), (10, 8))
        screen.blit(font.render(f"На экране: {balls_count}", True, (50, 100, 50)), (10, 34))
        hint = font.render("ЛКМ: зажать — всасывать, отпустить — выпустить шарик", True, (80, 80, 80))
        screen.blit(hint, (SCREEN_WIDTH - hint.get_width() - 10, 8))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
