# Install these skills for Cursor

## Preferred

```bash
npx skills add gigio1023/gigio-figures@technical-figure --agent cursor
npx skills add gigio1023/gigio-figures@drawio-diagram --agent cursor
npx skills add gigio1023/gigio-figures@eli5-figure --agent cursor
```

Install only the skills you want; each command is independent.

`technical-figure` and `eli5-figure` render with Node.js 20+ and a Chromium-family browser. Before the first figure, run `bash scripts/setup.sh` from the installed skill directory; it installs pinned npm packages and OFL fonts into `~/.cache/technical-figure` and never installs a browser.

## Manual install

```bash
git clone https://github.com/gigio1023/gigio-figures.git ~/.cursor/gigio-figures
mkdir -p ~/.cursor/skills/technical-figure ~/.cursor/skills/drawio-diagram ~/.cursor/skills/eli5-figure
cp -R ~/.cursor/gigio-figures/skills/technical-figure/. ~/.cursor/skills/technical-figure/
cp -R ~/.cursor/gigio-figures/skills/drawio-diagram/. ~/.cursor/skills/drawio-diagram/
cp -R ~/.cursor/gigio-figures/skills/eli5-figure/. ~/.cursor/skills/eli5-figure/
```

Restart Cursor after copying.
