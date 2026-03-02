# stgen-cli

A small command-line tool that generates static HTML from **YAML config** and **`.stg`** template files. Use a shared layout (header, footer, includes) and per-page content to build a static site.

---

## Features

- **Layout from YAML** — Define header/footer and includes in `.gen/layout.yml`
- **Per-page config** — Title, CSS/JS dependencies, and template folder in `.gen/page.yml`
- **Simple templates** — One `.stg` file per page; content is wrapped in `<main>`
- **Prettified output** — Generated HTML is formatted for readability

---

## Prerequisites

- **Python 3.7+**
- Dependencies: **PyYAML**, **BeautifulSoup4**

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Quick start

1. **Create the config directory** (e.g. `.gen`) and add `page.yml` and `layout.yml`.
2. **Create an `includes` folder** with header/footer HTML fragments.
3. **Create a template folder** (e.g. `templates`) and add `.stg` files (one per page).
4. **Run the generator:**

```bash
# Build all pages (all .stg files in the template folder)
python stgen-cli.py

# Build only specific pages
python stgen-cli.py index about contact
```

Output is written to the `compiled` directory by default.

---

## Project structure

Use this layout (folder names can vary; set `template_dir` in `page.yml` accordingly):

```
project/
├── .gen/
│   ├── layout.yml      # Layout: header/footer includes
│   └── page.yml        # Site title, template_dir, CSS/JS deps
├── includes/           # Header/footer fragments (path configurable)
│   ├── header.html
│   ├── sidebar.html
│   └── footer.html
├── templates/          # One .stg file per page (dir from page.yml)
│   ├── index.stg
│   ├── about.stg
│   └── contact.stg
├── compiled/           # Generated HTML (default output dir)
│   ├── index.html
│   ├── about.html
│   └── contact.html
├── stgen-cli.py
└── requirements.txt
```

---

## Configuration

### `.gen/page.yml`

- **`title`** — Used in `<title>` for all pages.
- **`template_dir`** — Folder that contains `.stg` page templates (e.g. `templates`).
- **`dependencies`** — Optional CSS, JS, and extra HTML:
  - **`styles`** — List of CSS URLs → `<link rel="stylesheet" href="...">`
  - **`scripts`** — List of JS URLs → `<script src="..." defer></script>`
  - **`html`** — Optional string (e.g. extra `<link>` or `<script>` tags).

Example:

```yaml
title: "My Site"
template_dir: "templates"
dependencies:
  styles:
    - "/css/style.css"
  scripts:
    - "/js/app.js"
  html: ''
```

### `.gen/layout.yml`

Defines which files are included in **header** and **footer**. Paths are relative to the **includes** directory (default: `includes/`).

Example:

```yaml
layout:
  header:
    include:
      - header.html
      - sidebar.html
  footer:
    include:
      - footer.html
```

---

## Usage

| Command | Description |
|--------|-------------|
| `python stgen-cli.py` | Build all pages (every `.stg` in `template_dir`) |
| `python stgen-cli.py index about` | Build only `index` and `about` (expects `index.stg`, `about.stg`) |
| `python stgen-cli.py -o build` | Write HTML to `build/` instead of `compiled/` |
| `python stgen-cli.py -i partials` | Use `partials/` as the includes directory |
| `python stgen-cli.py -g .config` | Use `.config/` instead of `.gen/` for config |
| `python stgen-cli.py -q` | Quiet: only print errors |

---

## Step-by-step guide: your first page

1. **Install and prepare**

   ```bash
   pip install -r requirements.txt
   mkdir .gen includes templates compiled
   ```

2. **Create `.gen/page.yml`**

   ```yaml
   title: "My Site"
   template_dir: "templates"
   dependencies:
     scripts: []
     styles: []
     html: ''
   ```

3. **Create `.gen/layout.yml`**

   ```yaml
   layout:
     header:
       include: ["header.html"]
     footer:
       include: ["footer.html"]
   ```

4. **Create `includes/header.html`**

   ```html
   <header>
     <a href="index.html">Home</a>
     <a href="about.html">About</a>
   </header>
   ```

5. **Create `includes/footer.html`**

   ```html
   <footer><p>© My Site</p></footer>
   ```

6. **Create `templates/index.stg`**

   ```html
   <h1>Welcome</h1>
   <p>This is the home page.</p>
   ```

7. **Build**

   ```bash
   python stgen-cli.py
   ```

8. **Open `compiled/index.html`** in a browser.

To add another page, create e.g. `templates/about.stg` and run `python stgen-cli.py` again (or `python stgen-cli.py about`).

---

## Contributing

1. Fork the project  
2. Create a branch for your changes  
3. Commit and push  
4. Open a Pull Request  

Thank you for contributing.
