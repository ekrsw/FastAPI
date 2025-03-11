FROM node:23.9.0-alpine

WORKDIR /workdir

# bashをインストール
RUN apk add --no-cache bash

# 依存関係のインストール（開発環境用）
COPY frontend/nextadmin/package*.json ./
RUN rm -rf node_modules package-lock.json && \
    npm install --legacy-peer-deps && \
    npm install @types/react @types/node && \
    npm install @mui/material @emotion/react @emotion/styled && \
    npm cache clean --force

# アプリケーションコードのコピー
COPY frontend/nextadmin ./

# 初回ビルドの実行
RUN npm run build

ENV HOSTNAME "0.0.0.0"
ENV PORT 3000
ENV NODE_ENV development

# 非rootユーザーを作成して実行（セキュリティ向上）時間がかかるのでコメントアウト
# RUN adduser -D nextuser && \
#     chown -R nextuser:nextuser /workdir

EXPOSE 3000

# 開発環境用のコマンド
CMD ["npm", "run", "dev"]
