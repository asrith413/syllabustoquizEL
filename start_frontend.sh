#!/bin/bash

# Start Frontend Server
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Run the development server
echo "Starting frontend server on http://localhost:3000"
npm run dev
