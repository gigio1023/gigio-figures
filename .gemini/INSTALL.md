# Install these skills for Gemini CLI

## Preferred

```bash
npx skills add gigio1023/gigio-figures@technical-diagram --agent gemini-cli
npx skills add gigio1023/gigio-figures@drawio-diagram --agent gemini-cli
npx skills add gigio1023/gigio-figures@data-chart --agent gemini-cli
npx skills add gigio1023/gigio-figures@eli5-figure --agent gemini-cli
```

Install only the skills you want; each command is independent.

## Manual install

```bash
git clone https://github.com/gigio1023/gigio-figures.git ~/.gemini/gigio-figures
mkdir -p ~/.gemini/skills/technical-diagram ~/.gemini/skills/drawio-diagram ~/.gemini/skills/data-chart ~/.gemini/skills/eli5-figure
cp -R ~/.gemini/gigio-figures/skills/technical-diagram/. ~/.gemini/skills/technical-diagram/
cp -R ~/.gemini/gigio-figures/skills/drawio-diagram/. ~/.gemini/skills/drawio-diagram/
cp -R ~/.gemini/gigio-figures/skills/data-chart/. ~/.gemini/skills/data-chart/
cp -R ~/.gemini/gigio-figures/skills/eli5-figure/. ~/.gemini/skills/eli5-figure/
```

Restart Gemini CLI after copying.
