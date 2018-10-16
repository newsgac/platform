FROM node:8-alpine
RUN mkdir /ws-celery-monitor
WORKDIR /ws-celery-monitor
COPY package.json /ws-celery-monitor
COPY yarn.lock /ws-celery-monitor
RUN yarn install
COPY index.js /ws-celery-monitor
CMD node index.js