FROM node:16.19.1

ENV PORT=3000

COPY . /frontend-react-js
WORKDIR /frontend-react-js
RUN npm i
EXPOSE ${PORT}
CMD ["npm", "start"]
