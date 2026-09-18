# Install these skills for Codex

## Preferred

```bash
npx skills add gigio1023/gigio-figures@technical-diagram --agent codex
npx skills add gigio1023/gigio-figures@drawio-diagram --agent codex
npx skills add gigio1023/gigio-figures@data-chart --agent codex
npx skills add gigio1023/gigio-figures@eli5-figure --agent codex
```

Install only the skills you want; each command is independent.

## Manual install

1. Clone the repo:

```bash
mkdir -p ~/.local/share
git clone https://github.com/gigio1023/gigio-figures.git ~/.local/share/gigio-figures
```

2. Symlink each skill directory into the Codex skill directory:

```bash
mkdir -p ~/.agents/skills
ln -s ~/.local/share/gigio-figures/skills/technical-diagram ~/.agents/skills/technical-diagram
ln -s ~/.local/share/gigio-figures/skills/drawio-diagram ~/.agents/skills/drawio-diagram
ln -s ~/.local/share/gigio-figures/skills/data-chart ~/.agents/skills/data-chart
ln -s ~/.local/share/gigio-figures/skills/eli5-figure ~/.agents/skills/eli5-figure
```

3. Restart Codex.
