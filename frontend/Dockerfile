#
# REPLACE THIS FILE
# File: peptalk/frontend/Dockerfile
#

# --- Stage 1: Build the React App ---
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files and install dependencies
# We now correctly copy package-lock.json
COPY package.json package-lock.json ./

# Use 'npm ci' which is the fast, clean, reproducible
# way to install dependencies from a lock file in CI/CD
RUN npm ci

# Copy the rest of the frontend source code
COPY . .

# Build the production-ready static files
# Use 'npm run build' as defined in package.json
RUN npm run build

# --- Stage 2: Serve with Nginx ---
FROM nginx:1.27-alpine

# Copy the build output from Stage 1
COPY --from=builder /app/build /usr/share/nginx/html

# Copy our custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (Nginx's default)
EXPOSE 80