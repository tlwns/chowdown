FROM --platform=linux/amd64 node:lts-slim

WORKDIR /client

COPY package.json package-lock.json ./
RUN npm ci --loglevel verbose

COPY . .

EXPOSE 3000

CMD ["bash", "run_test.sh"]

