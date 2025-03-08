FROM node:23.9.0-alpine

WORKDIR /workdir
# bashをインストール
RUN apk add --no-cache bash

COPY frontend/admin/package*.json ./
RUN npm install

COPY frontend/admin ./

ENV HOSTNAME "0.0.0.0"
ENV PORT 3000

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
