FROM node:22-alpine AS build

WORKDIR /app
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
COPY frontend/package.json frontend/package-lock.json frontend/tsconfig.json frontend/index.html /app/
COPY frontend/src /app/src
RUN npm ci && npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
