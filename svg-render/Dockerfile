# Build context is this directory, so everything the image contains lives under
# svg-render/ — which is also what release-please watches to decide there is a
# new version worth shipping.
#   docker build -t svg-render svg-render
FROM mcr.microsoft.com/playwright:v1.60.0-noble

# The dev container has exactly three fonts, and the cover repair pass measures
# text with DejaVu metrics. Strip every other family so a render here matches a
# render there instead of quietly resolving Arial to Liberation Sans.
# The Playwright image is rebuilt on its own schedule, so its Ubuntu packages
# lag the security archive — openssl was two patch releases behind on the first
# build. Take the updates at build time; the Trivy gate is what notices when
# this stops being enough.
RUN apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && apt-get install -y --no-install-recommends fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/* \
 && mv /usr/share/fonts/truetype/dejavu /tmp/dejavu \
 && rm -rf /usr/share/fonts/* \
 && mkdir -p /usr/share/fonts/truetype \
 && mv /tmp/dejavu /usr/share/fonts/truetype/dejavu \
 && fc-cache -f

WORKDIR /app

# npm is a build-time tool here — the container runs `node server.mjs` and
# nothing else. Left in place it is the whole vulnerability surface of this
# image: its bundled tar, sigstore, brace-expansion, ip-address and picomatch
# are what Trivy flags, none of it ever executed. So install, then delete it.
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund \
 && npm cache clean --force \
 && rm -rf /usr/local/lib/node_modules/npm /usr/lib/node_modules/npm \
           /usr/local/lib/node_modules/corepack /usr/lib/node_modules/corepack \
           /usr/local/lib/node_modules/yarn /opt/yarn* \
           /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack \
           /usr/local/bin/yarn /usr/local/bin/yarnpkg \
           /usr/bin/npm /usr/bin/npx /usr/bin/corepack \
           /root/.npm /home/pwuser/.npm \
 && node -e "require('playwright-core'); console.log('playwright-core resolves without npm')"

COPY server.mjs ./
COPY lib ./lib

USER pwuser
EXPOSE 8080
CMD ["node", "server.mjs"]
