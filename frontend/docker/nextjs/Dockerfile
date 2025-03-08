FROM node:23-alpine

# 作業ディレクトリの設定
WORKDIR /workdir

COPY ./frontend /workdir

RUN npm install
RUN npm run build

CMD ["npm", "start"]