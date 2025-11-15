# Stage 1: Build
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files (tanpa package-lock.json untuk menghindari masalah kompatibilitas)
COPY package.json ./

# Install dependencies dengan retry mechanism dan tanpa package-lock
# Menggunakan --no-package-lock untuk menghindari masalah dengan lock file
RUN for i in 1 2 3; do \
        npm install --no-package-lock --legacy-peer-deps && \
        test -f node_modules/.bin/vite && break || \
        (echo "Install attempt $i failed, retrying..." && rm -rf node_modules package-lock.json && sleep 5); \
    done

# Verifikasi bahwa vite terinstall
RUN test -f node_modules/.bin/vite || (echo "ERROR: vite not found!" && npm list vite 2>&1 && exit 1)

# Copy source code
COPY . .

# Build application menggunakan npx untuk memastikan menggunakan local vite
RUN npx vite build

# Stage 2: Production dengan Nginx
FROM nginx:alpine

# Tidak perlu install tool tambahan - gunakan healthcheck native
# Healthcheck akan menggunakan sh dan test command yang sudah tersedia di Alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files dari builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create nginx cache directory
RUN mkdir -p /var/cache/nginx/client_temp \
    /var/cache/nginx/proxy_temp \
    /var/cache/nginx/fastcgi_temp \
    /var/cache/nginx/uwsgi_temp \
    /var/cache/nginx/scgi_temp

# Expose port
EXPOSE 80

# Health check sederhana - check nginx process menggunakan ps (pasti tersedia di Alpine)
# Tidak memerlukan tool tambahan, 100% reliable dan tidak tergantung repository Alpine
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ps aux | grep -q '[n]ginx' || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

