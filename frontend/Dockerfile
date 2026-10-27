# Stage 1: Build the React application with Vite
FROM node:20-alpine AS build

WORKDIR /app

# Copy dependency specifications and install packages
COPY package*.json ./
RUN npm install

# Copy source code and build the production bundle
COPY . .
RUN npm run build

# Stage 2: Serve production bundle with Nginx
FROM nginx:alpine

# Copy built static files to Nginx public html directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration for SPA routing & reverse proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
