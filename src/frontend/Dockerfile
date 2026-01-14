FROM node:20-alpine as frontend_build
ARG BACKEND_URL
WORKDIR /app

COPY ./package.json ./pnpm-lock.yaml ./tsconfig.json ./vite.config.ts ./index.html ./tailwind.config.js ./postcss.config.js ./prettier.config.js /app/
RUN corepack enable && corepack prepare pnpm@latest --activate && pnpm install
COPY ./src /app/src
RUN pnpm run build

FROM nginx
COPY --from=frontend_build /app/build/ /usr/share/nginx/html
COPY /nginx.conf /etc/nginx/conf.d/default.conf
COPY start-nginx.sh /start-nginx.sh
RUN chmod +x /start-nginx.sh
ENV BACKEND_URL=$BACKEND_URL
CMD ["/start-nginx.sh"]