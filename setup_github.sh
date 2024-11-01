#!/bin/bash
# setup_github.sh

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Erstelle .github Struktur
echo -e "${GREEN}Creating .github structure...${NC}"
mkdir -p .github/workflows
mkdir -p .github/ISSUE_TEMPLATE

# Erstelle stargazers.yml
cat > .github/workflows/stargazers.yml << 'EOL'
name: Update Stargazers

on:
  schedule:
    - cron: "0 0 * * *"  # Täglich um Mitternacht
  workflow_dispatch:

jobs:
  update-stargazers:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Update Stargazers list
        uses: actions/github-script@v6
        with:
          script: |
            const { repo, owner } = context.repo;
            const stargazers = await github.paginate(
              github.rest.activity.listStargazersForRepo,
              { owner, repo }
            );
            
            const stargazersList = stargazers.map(user => ({
              login: user.login,
              avatar_url: user.avatar_url,
              html_url: user.html_url
            }));
            
            const fs = require('fs');
            const path = require('path');
            
            const content = `# ⭐ Stargazers\n\nThanks to all our stargazers! ✨\n\n${
              stargazersList.map(user => (
                `[![${user.login}](${user.avatar_url}&s=64)](${user.html_url})`
              )).join(' ')
            }\n\nLast updated: ${new Date().toISOString().split('T')[0]}\n`;
            
            fs.writeFileSync('STARGAZERS.md', content);
EOL

# Git Befehle
echo -e "${YELLOW}Executing Git commands...${NC}"

# Initialisiere Git falls noch nicht geschehen
if [ ! -d .git ]; then
    git init
fi

# Füge Dateien hinzu
git add .github/
git commit -m "Add GitHub Actions and templates"

# Prüfe ob Remote existiert
if ! git remote | grep -q origin; then
    echo -e "${YELLOW}Please add your GitHub remote with:${NC}"
    echo "git remote add origin https://github.com/ju1-eu/wahlergebnisse_visualization.git"
else
    git push origin main
fi

echo -e "${GREEN}Setup completed!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Push to GitHub if not done automatically"
echo "2. Go to your repository settings"
echo "3. Enable GitHub Actions under 'Actions > General'"
echo "4. Your stargazers list will update daily"