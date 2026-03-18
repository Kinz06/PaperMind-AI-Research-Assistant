echo "Setting up PaperMind with Docker..."
echo ""

if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose is not installed. Please install docker-compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "Docker found!"
echo ""

if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env and configure your settings"
fi

echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting PaperMind..."
docker-compose up -d

echo ""
echo "Waiting for Ollama to start..."
sleep 10

echo "Downloading Llama model (this may take a few minutes)..."
docker exec papermind-ollama ollama pull llama3.2:3b

echo ""
echo "Setup complete!"
echo ""
echo "Access PaperMind at: http://localhost:8501"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f papermind"
echo "  Stop services:    docker-compose down"
echo "  Restart:          docker-compose restart"
echo "  Shell access:     docker exec -it papermind-app bash"
echo ""