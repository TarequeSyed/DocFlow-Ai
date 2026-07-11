FROM node:20-slim

ENV NODE_ENV=development

WORKDIR /app

# Install dependencies using clean install (npm ci) for lockfiles
COPY package*.json ./
RUN npm ci

# Copy source tree (skips items in .dockerignore)
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
