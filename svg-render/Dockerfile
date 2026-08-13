# Build context is this directory, so everything the image contains lives under
# svg-render/ — which is also what release-please watches to decide there is a
# new version worth shipping.
#   docker build -t svg-render svg-render
FROM mcr.microsoft.com/playwright:v1.60.0-noble

# The dev container has exactly three fonts, and the cover repair pass measures
# text with DejaVu metrics. Strip every other family so a render here matches a
# render there instead of quietly resolving Arial to Liberation Sans.
RUN apt-get update \
 && apt-get install -y --no-install-recommends fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/* \
 && mv /usr/share/fonts/truetype/dejavu /tmp/dejavu \
 && rm -rf /usr/share/fonts/* \
 && mkdir -p /usr/share/fonts/truetype \
 && mv /tmp/dejavu /usr/share/fonts/truetype/dejavu \
 && fc-cache -f

WORKDIR /app

COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund

COPY server.mjs ./
COPY lib ./lib

USER pwuser
EXPOSE 8080
CMD ["node", "server.mjs"]
