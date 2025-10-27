#!/bin/bash

# Cursor AI Clean Architecture Pack - Installation Script
# This script installs the clean architecture pack into your project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Cursor AI Clean Architecture Pack - Installer    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running in a git repository
if [ ! -d .git ]; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    echo "Please run this script from the root of your git repository."
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${YELLOW}📦 Installation starting...${NC}"
echo ""

# Function to safely copy file
copy_file() {
    local source=$1
    local dest=$2
    local force=${3:-false}
    
    if [ -f "$dest" ] && [ "$force" = false ]; then
        echo -e "${YELLOW}⚠️  File exists: $dest${NC}"
        read -p "   Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "   ${BLUE}Skipped${NC}"
            return
        fi
    fi
    
    cp "$source" "$dest"
    echo -e "${GREEN}✅ Copied: $dest${NC}"
}

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p .github/workflows
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Copy files
echo -e "${BLUE}📄 Copying configuration files...${NC}"
copy_file "$SCRIPT_DIR/.cursorrules" ".cursorrules"
copy_file "$SCRIPT_DIR/cursor.json" "cursor.json"
copy_file "$SCRIPT_DIR/review_parser.py" "review_parser.py"
echo ""

echo -e "${BLUE}🔧 Copying GitHub workflow files...${NC}"
copy_file "$SCRIPT_DIR/.github/workflows/ai_review.yml" ".github/workflows/ai_review.yml"
copy_file "$SCRIPT_DIR/.github/workflows/ai_merge_guard.yml" ".github/workflows/ai_merge_guard.yml"
echo ""

# Make review_parser.py executable
chmod +x review_parser.py
echo -e "${GREEN}✅ Made review_parser.py executable${NC}"
echo ""

# Copy template (don't overwrite if exists)
if [ ! -f "CODE_REVIEW_SUMMARY.md" ]; then
    cp "$SCRIPT_DIR/CODE_REVIEW_SUMMARY.md" "CODE_REVIEW_SUMMARY.md"
    echo -e "${GREEN}✅ Created CODE_REVIEW_SUMMARY.md template${NC}"
else
    echo -e "${BLUE}ℹ️  CODE_REVIEW_SUMMARY.md already exists, skipping${NC}"
fi
echo ""

# Detect project structure
echo -e "${BLUE}🔍 Analyzing project structure...${NC}"

PROJECT_TYPE="unknown"
if [ -f "package.json" ]; then
    PROJECT_TYPE="node"
    echo -e "   ${GREEN}Detected: Node.js/TypeScript project${NC}"
elif [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    PROJECT_TYPE="python"
    echo -e "   ${GREEN}Detected: Python project${NC}"
elif [ -f "Cargo.toml" ]; then
    PROJECT_TYPE="rust"
    echo -e "   ${GREEN}Detected: Rust project${NC}"
else
    echo -e "   ${YELLOW}Could not auto-detect project type${NC}"
fi
echo ""

# Check for common layer directories
echo -e "${BLUE}📂 Checking for Clean Architecture layers...${NC}"
LAYERS_FOUND=0

check_layer() {
    local layer=$1
    shift
    local paths=("$@")
    
    for path in "${paths[@]}"; do
        if [ -d "$path" ]; then
            echo -e "   ${GREEN}✓ Found $layer layer: $path${NC}"
            LAYERS_FOUND=$((LAYERS_FOUND + 1))
            return
        fi
    done
    echo -e "   ${YELLOW}✗ $layer layer not found${NC}"
}

check_layer "Domain" "src/domain" "domain" "lib/domain" "pkg/domain"
check_layer "Application" "src/application" "application" "src/use-cases" "lib/application" "pkg/application"
check_layer "Infrastructure" "src/infrastructure" "infrastructure" "lib/infrastructure" "pkg/infrastructure"
check_layer "Presentation" "src/presentation" "presentation" "src/api" "src/controllers" "lib/presentation"

echo ""

if [ $LAYERS_FOUND -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: No Clean Architecture layers detected${NC}"
    echo -e "   Consider organizing your code into layers:"
    echo -e "   - domain/         (business logic)"
    echo -e "   - application/    (use cases)"
    echo -e "   - infrastructure/ (database, APIs)"
    echo -e "   - presentation/   (controllers, UI)"
    echo ""
fi

# Check for GitHub secrets
echo -e "${BLUE}🔐 Checking GitHub repository setup...${NC}"

if command -v gh &> /dev/null; then
    echo -e "   ${GREEN}GitHub CLI detected${NC}"
    
    # Check if secrets exist
    if gh secret list &> /dev/null; then
        HAS_ANTHROPIC=$(gh secret list | grep ANTHROPIC_API_KEY || echo "")
        HAS_OPENAI=$(gh secret list | grep OPENAI_API_KEY || echo "")
        
        if [ -n "$HAS_ANTHROPIC" ]; then
            echo -e "   ${GREEN}✓ ANTHROPIC_API_KEY is configured${NC}"
        elif [ -n "$HAS_OPENAI" ]; then
            echo -e "   ${GREEN}✓ OPENAI_API_KEY is configured${NC}"
        else
            echo -e "   ${YELLOW}✗ No AI API keys found${NC}"
            echo -e "   ${YELLOW}  You'll need to add ANTHROPIC_API_KEY or OPENAI_API_KEY${NC}"
        fi
    fi
else
    echo -e "   ${YELLOW}GitHub CLI not installed - skipping secret check${NC}"
    echo -e "   ${BLUE}Install with: brew install gh${NC}"
fi
echo ""

# Configuration recommendations
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo -e "1. ${YELLOW}Configure API Keys${NC} (if not already done)"
echo -e "   • Go to: GitHub repo → Settings → Secrets and variables → Actions"
echo -e "   • Add either ANTHROPIC_API_KEY or OPENAI_API_KEY"
echo -e "   • Get Claude API key: https://console.anthropic.com/"
echo -e "   • Get OpenAI API key: https://platform.openai.com/"
echo ""

echo -e "2. ${YELLOW}Customize cursor.json${NC}"
echo -e "   • Update layer paths to match your project structure"
echo -e "   • Adjust quality thresholds as needed"
echo -e "   • Configure language-specific rules"
echo ""

echo -e "3. ${YELLOW}Review .cursorrules${NC}"
echo -e "   • Add project-specific architecture rules"
echo -e "   • Define team coding standards"
echo -e "   • Document design patterns to use/avoid"
echo ""

echo -e "4. ${YELLOW}Test the Setup${NC}"
echo -e "   • Create a test branch and PR"
echo -e "   • Verify workflows run successfully"
echo -e "   • Check that review comments appear on PR"
echo ""

echo -e "5. ${YELLOW}Enable Branch Protection${NC}"
echo -e "   • Go to: Settings → Branches → Add rule"
echo -e "   • Require status checks: 'Clean Architecture Guard'"
echo -e "   • This prevents merging with violations"
echo ""

# Offer to customize cursor.json
echo -e "${BLUE}🎯 Customization Options:${NC}"
echo ""
read -p "Would you like help customizing cursor.json for your project? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}Please specify your layer paths (press Enter to skip):${NC}"
    
    read -p "Domain layer path (e.g., src/domain): " DOMAIN_PATH
    read -p "Application layer path (e.g., src/application): " APP_PATH
    read -p "Infrastructure layer path (e.g., src/infrastructure): " INFRA_PATH
    read -p "Presentation layer path (e.g., src/api): " PRESENT_PATH
    
    if [ -n "$DOMAIN_PATH" ] || [ -n "$APP_PATH" ] || [ -n "$INFRA_PATH" ] || [ -n "$PRESENT_PATH" ]; then
        echo -e "${BLUE}Updating cursor.json...${NC}"
        
        # Note: This is a simple replacement. For production, use a proper JSON parser
        if [ -n "$DOMAIN_PATH" ]; then
            sed -i.bak "s|\"src/domain/\*\*\"|\"$DOMAIN_PATH/**\"|g" cursor.json
        fi
        if [ -n "$APP_PATH" ]; then
            sed -i.bak "s|\"src/application/\*\*\"|\"$APP_PATH/**\"|g" cursor.json
        fi
        if [ -n "$INFRA_PATH" ]; then
            sed -i.bak "s|\"src/infrastructure/\*\*\"|\"$INFRA_PATH/**\"|g" cursor.json
        fi
        if [ -n "$PRESENT_PATH" ]; then
            sed -i.bak "s|\"src/presentation/\*\*\"|\"$PRESENT_PATH/**\"|g" cursor.json
        fi
        
        rm -f cursor.json.bak
        echo -e "${GREEN}✅ cursor.json updated${NC}"
    fi
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Installation Complete! 🎉                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📚 Documentation: See README.md for detailed usage${NC}"
echo -e "${BLUE}🐛 Issues? Visit: https://github.com/your-repo/issues${NC}"
echo ""
echo -e "${YELLOW}Remember to commit these changes:${NC}"
echo -e "  git add .cursorrules cursor.json review_parser.py .github/"
echo -e "  git commit -m 'Add Clean Architecture review pack'"
echo -e "  git push"
echo ""

