# Build stage - OneClick Reels AI Frontend
# Cache bust: 2026-01-13
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Install envsubst for environment variable substitution
RUN apk add --no-cache gettext

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration template
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Expose port (Railway will override with $PORT)
EXPOSE 80

# Set default PORT if not provided
ENV PORT=80

# Start nginx with environment variable substitution
CMD ["/bin/sh", "-c", "envsubst '$PORT $BACKEND_URL' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
