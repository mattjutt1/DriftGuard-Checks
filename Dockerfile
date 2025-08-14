# DriftGuard Production Docker Image
# Multi-stage build for optimized production deployment

# Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++ git

# Copy package files
COPY package*.json ./

# Install dependencies (including devDependencies for building)
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Remove development dependencies
RUN npm prune --production

# Production stage
FROM node:18-alpine AS production

# Install security updates and runtime dependencies
RUN apk update && apk upgrade && \
    apk add --no-cache \
    dumb-init \
    tini \
    curl \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Create non-root user for security
RUN addgroup -g 1001 -S driftguard && \
    adduser -S driftguard -u 1001 -G driftguard

# Set working directory
WORKDIR /app

# Copy built application from build stage
COPY --from=builder --chown=driftguard:driftguard /app/dist ./dist
COPY --from=builder --chown=driftguard:driftguard /app/node_modules ./node_modules
COPY --from=builder --chown=driftguard:driftguard /app/package*.json ./

# Copy other necessary files
COPY --chown=driftguard:driftguard app/ ./app/
COPY --chown=driftguard:driftguard scripts/validate-config.js ./scripts/

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp && \
    chown -R driftguard:driftguard /app

# Switch to non-root user
USER driftguard

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Use tini as init system for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Start the application
CMD ["node", "dist/index.js"]

# Labels for metadata
LABEL maintainer="DriftGuard Team <team@driftguard.dev>" \
      version="1.0.0" \
      description="Enterprise-grade automated pull request checks and intelligent code analysis" \
      org.opencontainers.image.title="DriftGuard" \
      org.opencontainers.image.description="Enterprise-grade automated pull request checks and intelligent code analysis" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="DriftGuard" \
      org.opencontainers.image.source="https://github.com/mattjutt1/DriftGuard-Checks" \
      org.opencontainers.image.documentation="https://github.com/mattjutt1/DriftGuard-Checks#readme" \
      org.opencontainers.image.licenses="MIT"