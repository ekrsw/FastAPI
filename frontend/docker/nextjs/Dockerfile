FROM node:23.9.0-alpine

WORKDIR /workdir

# bashをインストール
RUN apk add --no-cache bash

# 依存関係のインストール（キャッシュを効率化するために分離）
COPY frontend/admin/package*.json ./
RUN npm ci --only=production && \
    npm cache clean --force

# アプリケーションコードのコピー
COPY frontend/admin ./

ENV HOSTNAME "0.0.0.0"
ENV PORT 3000
ENV NODE_ENV production

# 非rootユーザーを作成して実行（セキュリティ向上）
RUN adduser -D nextuser && \
    chown -R nextuser:nextuser /workdir

EXPOSE 3000

# 本番環境用のコマンド
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
