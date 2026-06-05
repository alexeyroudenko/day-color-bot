# pull official base image
FROM node:24-alpine

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# install app dependencies
COPY package.json yarn.lock ./
# COPY package-lock.json ./
RUN yarn
# RUN npm install --silent
# RUN npm install react-scripts@3.4.1 -g --silent
# RUN npm install react-d3-graph -g --silent

# add app
COPY . ./

# Enable polling for file changes
ENV CHOKIDAR_USEPOLLING=true

EXPOSE 3000

# start app
CMD ["yarn", "start"]