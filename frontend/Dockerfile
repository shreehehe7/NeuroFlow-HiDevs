# Stage 1: Build
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime (Nginx)
FROM nginx:alpine AS runtime
COPY --from=builder /app/.next/standalone /app
COPY --from=builder /app/.next/static /app/.next/static
COPY --from=builder /app/public /app/public
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
