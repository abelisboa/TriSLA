#!/usr/bin/env bash
set -euo pipefail

# TriSLA Docker & GHCR Setup Script
# Author: Abel Lisboa <abelisboa@gmail.com>
# Date: 2025-10-23

echo "🔧 TriSLA Docker & GHCR Setup"
echo "=============================="
echo ""

# Check if running on Windows with WSL
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
    echo "🪟 Detected Windows environment"
    echo "📋 Please ensure Docker Desktop is installed and running"
    echo ""
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker installation
echo "🔍 Checking Docker installation..."
if command_exists docker; then
    echo "✅ Docker is installed"
    docker --version
else
    echo "❌ Docker is not installed or not in PATH"
    echo ""
    echo "📥 Please install Docker:"
    echo "  Windows: Download Docker Desktop from https://www.docker.com/products/docker-desktop"
    echo "  Linux: sudo apt-get install docker.io"
    echo "  macOS: brew install --cask docker"
    echo ""
    exit 1
fi

# Check Docker daemon
echo ""
echo "🔍 Checking Docker daemon..."
if docker info >/dev/null 2>&1; then
    echo "✅ Docker daemon is running"
else
    echo "❌ Docker daemon is not running"
    echo ""
    echo "🚀 Please start Docker Desktop or Docker daemon"
    echo "  Windows/macOS: Start Docker Desktop application"
    echo "  Linux: sudo systemctl start docker"
    echo ""
    exit 1
fi

# Check GitHub CLI for authentication
echo ""
echo "🔍 Checking GitHub CLI..."
if command_exists gh; then
    echo "✅ GitHub CLI is installed"
    gh --version
else
    echo "⚠️  GitHub CLI is not installed (optional but recommended)"
    echo ""
    echo "📥 To install GitHub CLI:"
    echo "  Windows: winget install GitHub.cli"
    echo "  Linux: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    echo "  macOS: brew install gh"
fi

# GitHub Container Registry Authentication
echo ""
echo "🔐 Setting up GitHub Container Registry authentication..."
echo ""

# Check if already logged in
if docker info 2>/dev/null | grep -q "ghcr.io"; then
    echo "✅ Already authenticated with GHCR"
else
    echo "🔑 Please authenticate with GitHub Container Registry:"
    echo ""
    echo "Option 1 - Using GitHub CLI (recommended):"
    echo "  gh auth login"
    echo "  gh auth token | docker login ghcr.io -u abelisboa --password-stdin"
    echo ""
    echo "Option 2 - Using Personal Access Token:"
    echo "  1. Go to https://github.com/settings/tokens"
    echo "  2. Generate a new token with 'write:packages' and 'read:packages' scopes"
    echo "  3. Run: docker login ghcr.io -u abelisboa"
    echo "  4. Enter your token as password"
    echo ""
    echo "Option 3 - Using Docker login directly:"
    echo "  docker login ghcr.io -u abelisboa"
    echo ""
    
    read -p "Press Enter after completing authentication..."
fi

# Verify authentication
echo ""
echo "🔍 Verifying GHCR authentication..."
if docker pull ghcr.io/abelisboa/hello-world:latest >/dev/null 2>&1 || docker login ghcr.io --username abelisboa >/dev/null 2>&1; then
    echo "✅ Successfully authenticated with GHCR"
else
    echo "❌ Authentication failed. Please check your credentials."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  1. Verify your GitHub username is 'abelisboa'"
    echo "  2. Check that your token has 'write:packages' permission"
    echo "  3. Ensure Docker is running"
    echo ""
    exit 1
fi

# Create .dockerignore files if they don't exist
echo ""
echo "📝 Creating .dockerignore files..."

for dir in src/semantic src/ai src/blockchain src/integration src/monitoring trisla-portal/apps/api trisla-portal/apps/ui; do
    if [[ -d "$dir" ]]; then
        dockerignore_file="$dir/.dockerignore"
        if [[ ! -f "$dockerignore_file" ]]; then
            cat > "$dockerignore_file" << EOF
# Git
.git
.gitignore

# Documentation
README.md
*.md

# IDE
.vscode
.idea
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
EOF
            echo "✅ Created $dockerignore_file"
        else
            echo "ℹ️  $dockerignore_file already exists"
        fi
    fi
done

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Run: ./build_all.sh"
echo "  2. Run: ./push_all.sh"
echo ""
echo "🔍 To test individual modules:"
echo "  docker run -p 8080:8080 ghcr.io/abelisboa/trisla-semantic:latest"
echo "  docker run -p 8080:8080 ghcr.io/abelisboa/trisla-ai:latest"
echo "  docker run -p 8000:8000 ghcr.io/abelisboa/trisla-api:latest"
echo "  docker run -p 80:80 ghcr.io/abelisboa/trisla-ui:latest"












