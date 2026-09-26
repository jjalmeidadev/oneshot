FROM node:24-alpine AS build

WORKDIR /workspace
COPY src/frontend/package.json src/frontend/package-lock.json ./
RUN npm ci
COPY src/frontend/ ./
RUN npm run build

FROM nginx:1.29-alpine AS runtime

COPY --from=build --chown=nginx:nginx /workspace/dist /usr/share/nginx/html
COPY --chown=nginx:nginx src/frontend/nginx.conf /etc/nginx/nginx.conf

USER 101:101
EXPOSE 8080
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
