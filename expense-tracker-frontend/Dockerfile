# Step 1: Use official Node.js image as a base image
FROM node:16

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy package.json and package-lock.json to the container
COPY package*.json ./

# Step 4: Install dependencies
RUN npm install

# Step 5: Copy the rest of the application code
COPY . .

# Step 6: Build the React app
RUN npm run build

# Step 7: Serve the built React app using a static file server
RUN npm install -g serve

# Step 8: Expose the port the app runs on
EXPOSE 3000

# Step 9: Start the app
CMD ["serve", "-s", "build", "-l", "3000"]
