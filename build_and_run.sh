#!/bin/bash

# ✅ Use the builder you already created
BUILDER_NAME="cloud-jrob77-cloud-kgnn-ddi-builder"
IMAGE_NAME="ddi-kg-prediction-app"
PORT=5050

echo "🔄 Using builder: $BUILDER_NAME"
docker buildx use "$BUILDER_NAME"

echo "🚀 Starting BuildCloud build with --load..."
docker build -t "$IMAGE_NAME" .



if [ $? -eq 0 ]; then
  echo "✅ Build completed successfully!"
  echo "🧹 Cleaning up any previous container..."
  docker rm -f ddi-container > /dev/null 2>&1

  echo "🏃 Running container on port $PORT..."
  docker run -d --name ddi-container -p $PORT:$PORT "$IMAGE_NAME"

  echo "🌐 App is running at: http://localhost:$PORT"
else
  echo "❌ Build failed. Check Docker logs above."
fi
