#!/bin/bash

# Secret Scanner Script using Gitleaks
# Safe, open-source secret detection

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Secret Scanner - Powered by Gitleaks             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if gitleaks is installed
if [ ! -f "./gitleaks" ]; then
    echo -e "${YELLOW}Installing Gitleaks...${NC}"
    curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.18.4/gitleaks_8.18.4_linux_x64.tar.gz -o gitleaks.tar.gz
    tar -xzf gitleaks.tar.gz
    chmod +x gitleaks
    rm gitleaks.tar.gz
    echo -e "${GREEN}✅ Gitleaks installed${NC}"
fi

# Menu
echo "Select scan type:"
echo "1. Quick scan (current directory, no git history)"
echo "2. Full git history scan"
echo "3. Pre-commit scan (staged files only)"
echo "4. Generate baseline (allowlist current secrets)"
echo "5. Check specific file"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo -e "\n${BLUE}Running quick scan...${NC}\n"
        ./gitleaks detect --source . --config .gitleaks.toml --no-git --report-format json --report-path gitleaks-report.json
        ;;
    2)
        echo -e "\n${BLUE}Running full git history scan...${NC}\n"
        ./gitleaks detect --source . --config .gitleaks.toml --report-format json --report-path gitleaks-report.json
        ;;
    3)
        echo -e "\n${BLUE}Scanning staged files...${NC}\n"
        ./gitleaks protect --source . --config .gitleaks.toml --staged
        ;;
    4)
        echo -e "\n${BLUE}Generating baseline...${NC}\n"
        ./gitleaks detect --source . --config .gitleaks.toml --baseline-path gitleaks-baseline.json --report-path gitleaks-baseline.json
        echo -e "${GREEN}Baseline saved to gitleaks-baseline.json${NC}"
        echo "Add this to your .gitleaks.toml to ignore these findings"
        ;;
    5)
        read -p "Enter file path: " filepath
        echo -e "\n${BLUE}Scanning $filepath...${NC}\n"
        ./gitleaks detect --source "$filepath" --config .gitleaks.toml --no-git
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Check results
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ No secrets detected!${NC}"
else
    echo -e "\n${YELLOW}⚠️  Potential secrets found!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review the findings above"
    echo "2. For false positives, add to .gitleaks.toml allowlist"
    echo "3. For real secrets:"
    echo "   - Remove from code"
    echo "   - Rotate the credentials"
    echo "   - Clean git history if needed"
    
    if [ -f "gitleaks-report.json" ]; then
        echo ""
        echo -e "${BLUE}Detailed report saved to: gitleaks-report.json${NC}"
        echo ""
        
        # Show summary
        count=$(jq '. | length' gitleaks-report.json 2>/dev/null || echo "0")
        echo -e "${YELLOW}Total findings: $count${NC}"
        
        # Group by file
        echo ""
        echo "Files with potential secrets:"
        jq -r '.[].File' gitleaks-report.json 2>/dev/null | sort | uniq -c | sort -rn | head -10
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Offer to install as pre-commit hook
echo "Would you like to install Gitleaks as a pre-commit hook? (y/n)"
read -p "> " install_hook

if [ "$install_hook" = "y" ] || [ "$install_hook" = "Y" ]; then
    mkdir -p .git/hooks
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Gitleaks pre-commit hook

echo "🔍 Scanning for secrets..."

# Run gitleaks on staged files
./gitleaks protect --source . --config .gitleaks.toml --staged

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Commit blocked: potential secrets detected!"
    echo "Fix the issues or add false positives to .gitleaks.toml"
    exit 1
fi

echo "✅ No secrets detected in staged files"
EOF
    
    chmod +x .git/hooks/pre-commit
    echo -e "${GREEN}✅ Pre-commit hook installed!${NC}"
    echo "Gitleaks will now scan before every commit"
fi