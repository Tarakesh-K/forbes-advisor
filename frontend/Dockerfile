# Frontend Dockerfile (Next.js app)
FROM node:20-alpine

# Install pnpm globally
RUN npm install -g pnpm

WORKDIR /app

# Copy package manifests first for caching
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy app sources
COPY . .

# Build app
RUN pnpm build

# Expose port
EXPOSE 3000

# Start in development mode with host binding for container
CMD ["pnpm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]
