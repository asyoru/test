# Игра «Шарики» — графическое окно через X11
# Сборка: docker build -t balls-game .
# Запуск (Linux, с доступом к дисплею): см. README.md

FROM python:3.12-slim-bookworm

# Системные зависимости для pygame-ce (SDL2 и X11)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libx11-6 \
    libxext6 \
    libxrandr2 \
    libxcursor1 \
    libxi6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY logic.py game_gui.py gui.py ./

ENV PYTHONUNBUFFERED=1

# Запуск игры (окно появится на дисплее хоста при правильном -e DISPLAY и -v X11)
CMD ["python", "gui.py"]
