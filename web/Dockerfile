FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
ENV NITRO_HOST=0.0.0.0 NITRO_PORT=3000
CMD ["npm", "run", "start"]
