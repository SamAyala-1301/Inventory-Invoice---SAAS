#!/bin/bash

cd "$(dirname "$0")"

echo "🚀 Setting up Inventory SaaS - Sprint 1"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    
    # Generate Django secret key
    DJANGO_SECRET=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    sed -i "s/your-secret-key-here-generate-with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'/$DJANGO_SECRET/" .env
    
    # Generate JWT secret
    JWT_SECRET=$(openssl rand -base64 32)
    sed -i "s/your-jwt-secret-key-here/$JWT_SECRET/" .env
    
    # Generate password
    POSTGRES_PASS=$(openssl rand -base64 16)
    sed -i "s/your_secure_password_here/$POSTGRES_PASS/" .env
    
    echo -e "${GREEN}✓ .env file created with generated secrets${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Start Docker services
echo -e "\n${YELLOW}Starting Docker services...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Run migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
docker-compose exec -T api python manage.py migrate

# Seed roles and permissions
echo -e "\n${YELLOW}Seeding roles and permissions...${NC}"
docker-compose exec -T api python manage.py seed_roles

# Create superuser (optional)
echo -e "\n${YELLOW}Would you like to create a superuser? (y/n)${NC}"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    docker-compose exec api python manage.py createsuperuser
fi

# Setup frontend
echo -e "\n${YELLOW}Setting up frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

# Create .env for frontend
if [ ! -f .env ]; then
    echo "VITE_API_URL=http://localhost:8000/api" > .env
    echo -e "${GREEN}✓ Frontend .env created${NC}"
fi

cd ..

echo -e "\n${GREEN}========================================="
echo "✓ Setup Complete!"
echo "=========================================${NC}"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Start frontend development server:"
echo "   cd frontend && npm run dev"
echo ""
echo "2. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000/api"
echo "   - API Docs: http://localhost:8000/api/docs"
echo "   - Admin Panel: http://localhost:8000/admin"
echo ""
echo "3. View logs:"
echo "   docker-compose logs -f api"
echo ""
echo "4. Stop services:"
echo "   docker-compose down"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"