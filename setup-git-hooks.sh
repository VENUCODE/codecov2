#!/bin/bash
#
# Setup script to configure Git to use hooks from .githooks directory
#
# This script configures Git to use the hooks stored in .githooks/
# Run this once after cloning the repository or when setting up a new machine.

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Git hooks...${NC}"

# Check if .githooks directory exists
if [ ! -d ".githooks" ]; then
    echo "Error: .githooks directory not found!"
    exit 1
fi

# Make hooks executable
echo "Making hooks executable..."
chmod +x .githooks/pre-push

# Configure Git to use .githooks as hooks path
echo "Configuring Git hooks path..."
git config core.hooksPath .githooks

echo -e "${GREEN}✓ Git hooks configured successfully!${NC}"
echo ""
echo "The pre-push hook will now run tests before allowing pushes."
echo "To bypass the hook (not recommended): git push --no-verify"

