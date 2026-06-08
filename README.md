# pyexe-builder

Tool to package Python projects into executables with PyInstaller.

Build on Linux and you get a Linux binary. Build on Windows (or GitHub `windows-latest`) and you get a `.exe`.

## Clone

```bash
git clone git@github.com:alis2001/pyexe-builder.git
cd pyexe-builder
```

## Run the builder (local)

Requires Python 3.10+.

**Linux:**

```bash
python3 -m pip install -r requirements.txt
python3 run.py check
python3 run.py info
```

**Windows:**

```bat
python -m pip install -r requirements.txt
python run.py check
python run.py info
```

### Commands

| Command | What it does |
|---------|----------------|
| `python run.py check` | Install/check PyInstaller dependencies |
| `python run.py info` | Show current OS and output type |
| `python run.py build ...` | Build an executable |
| `python run.py serve` | Start Flask API on port 5080 |

---

## Build a Python project (local)

Put projects under `projects/` or point `build` at any folder.

**Minimal build:**

```bash
python run.py build projects/myapp -n myapp -e main.py
```

| Flag | Required | Description |
|------|----------|-------------|
| `project` | yes | Path to the Python project folder |
| `-n` / `--name` | yes | Output executable name |
| `-e` / `--entry` | no | Entry file (default: `main.py`) |
| `--hidden-import` | no | Module PyInstaller misses (repeatable) |
| `--collect-all` | no | Bundle all files from a package (repeatable) |
| `--data` | no | Extra file to include (repeatable) |
| `--onefile` | no | Single file instead of a folder |

**Output location:**

```
.build/<platform>/<name>/dist/<name>/
```

Linux: run `./<name>` inside that folder.  
Windows: run `<name>.exe`.  
Copy the whole `dist/<name>/` folder to the target machine.

### Example: stampantepy

```bash
python run.py build projects/stampantepy -n stampantepy -e main.py \
  --hidden-import escpos \
  --hidden-import usb \
  --hidden-import flask \
  --collect-all escpos \
  --data logo.jpg \
  --data logoOspedale.png
```

### Example: hello

```bash
python run.py build examples/hello -n hello -e main.py --hidden-import flask
```

---

## Add a new project to this repo

1. Clone the repo (once per machine).
2. Copy your project into `projects/your-app/`.
3. Commit and push:

```bash
git add projects/your-app
git commit -m "add your-app"
git push
```

4. Use GitHub Actions to build (see below) or build locally.

Existing projects:

- `examples/hello/` — minimal sample
- `projects/stampantepy/` — printer service for totems

---

## GitHub Actions

Open: **https://github.com/alis2001/pyexe-builder/actions**

### 1. build-stampantepy (stampantepy)

**Runs automatically** when files change under `projects/stampantepy/`.

**Manual run:**

1. Actions → **build-stampantepy**
2. **Run workflow** → branch `main` → **Run workflow**
3. Wait for both jobs (`ubuntu-latest` and `windows-latest`) to finish
4. Open the run → scroll to **Artifacts**
5. Download:
   - `stampantepy-windows-latest` → `.exe` for totems
   - `stampantepy-ubuntu-latest` → Linux binary

Inside the zip:

```
dist-artifact/stampantepy/stampantepy.exe   (Windows)
dist-artifact/stampantepy/stampantepy       (Linux)
```

Artifacts are kept for 30 days.

### 2. ci (hello example)

**Runs automatically** on every push to `main`.

Builds `examples/hello` on Linux and Windows. Download artifacts `hello-ubuntu-latest` and `hello-windows-latest`.

### 3. build-project (any project in the repo)

**Manual only.**

1. Actions → **build-project**
2. **Run workflow**
3. Fill in:

| Input | Example |
|-------|---------|
| project_path | `projects/stampantepy` |
| app_name | `stampantepy` |
| entry_point | `main.py` |
| hidden_imports | `flask,escpos,usb` |

4. Download artifact `<app_name>-ubuntu-latest` or `<app_name>-windows-latest`

---

## Run the built application

The built app is not pyexe-builder. It is your packaged project.

Example for stampantepy:

```bash
./stampantepy          # Linux
stampantepy.exe        # Windows
```

Then test:

```bash
curl http://localhost:5050/checkStatus/
```

---

## Notes

- You do not need pyexe-builder installed on the totem. Only copy the `dist/` output folder.
- For a Windows `.exe` without a local Windows PC, use GitHub Actions and download `stampantepy-windows-latest`.
- Node.js deprecation notices in Actions logs are from GitHub runner images and do not block builds.
