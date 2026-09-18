# Install these skills for Cursor

## Preferred

```bash
npx skills add gigio1023/gigio-figures@technical-diagram --agent cursor
npx skills add gigio1023/gigio-figures@drawio-diagram --agent cursor
npx skills add gigio1023/gigio-figures@data-chart --agent cursor
npx skills add gigio1023/gigio-figures@eli5-figure --agent cursor
```

Install only the skills you want; each command is independent.

## Manual install

```bash
git clone https://github.com/gigio1023/gigio-figures.git ~/.cursor/gigio-figures
mkdir -p ~/.cursor/skills/technical-diagram ~/.cursor/skills/drawio-diagram ~/.cursor/skills/data-chart ~/.cursor/skills/eli5-figure
cp -R ~/.cursor/gigio-figures/skills/technical-diagram/. ~/.cursor/skills/technical-diagram/
cp -R ~/.cursor/gigio-figures/skills/drawio-diagram/. ~/.cursor/skills/drawio-diagram/
cp -R ~/.cursor/gigio-figures/skills/data-chart/. ~/.cursor/skills/data-chart/
cp -R ~/.cursor/gigio-figures/skills/eli5-figure/. ~/.cursor/skills/eli5-figure/
```

Restart Cursor after copying.
