# Используем Node.js образ
FROM node:20-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и yarn.lock
COPY package.json yarn.lock ./

# Устанавливаем зависимости
RUN yarn install --network-timeout 100000

# Копируем исходный код
COPY . .

# Устанавливаем переменные окружения для продакшн
ENV REACT_APP_BACKEND_URL=https://german-letterai-assistant.onrender.com
ENV REACT_APP_GOOGLE_CLIENT_ID=364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com

# Собираем приложение для продакшн
RUN yarn build

# Устанавливаем глобально serve для статических файлов
RUN npm install -g serve

# Открываем порт 3000
EXPOSE 3000

# Запускаем приложение с поддержкой SPA роутинга
CMD ["serve", "-s", "build", "-l", "3000", "--single"]