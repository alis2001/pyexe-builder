# pyexe-builder

CLI and Flask tool to package Python projects into native executables with PyInstaller.

Works on Linux and Windows. The output matches the OS where the build runs (Linux binary on Linux, `.exe` on Windows).

## Install

```bash
python -m pip install -r requirements.txt
python run.py check
python run.py info
```

## Build a project

```bash
python run.py build /path/to/project -n myapp -e main.py
```

Optional flags when PyInstaller needs help:

```bash
--hidden-import MODULE
--collect-all PACKAGE
--data image.png
--onefile
```

Example (stampantepy):

```bash
python run.py build .. -n stampantepy -e main.py \
  --hidden-import escpos --hidden-import usb --collect-all escpos \
  --data logo.jpg --data logoOspedale.png
```

Output:

```
.build/<platform>/myapp/dist/myapp/
```

## Commands

| Command | Purpose |
|---------|---------|
| `python run.py check` | verify builder dependencies |
| `python run.py info` | show current platform and output type |
| `python run.py build ...` | create executable |
| `python run.py serve` | run Flask API on port 5080 |

## GitHub

Push this folder as its own repository. GitHub Actions builds on every push (example app) and provides a manual workflow to build any project in the repo.

### Push to a new GitHub repo

```bash
cd pyexe-builder
git init
git add .
git commit -m "initial pyexe-builder"
git branch -M main
git remote add origin git@github.com:alis2001/pyexe-builder.git
git push -u origin main
```

### CI

- **ci.yml** — runs on push/PR, builds `examples/hello` on Linux and Windows
- **build-project.yml** — manual run from Actions tab (choose project path, name, entry file)

Download artifacts from the Actions run (`.build/` folder with the binary).

### Build stampantepy from GitHub

Either include stampantepy inside the repo or use a second checkout in your own workflow. Simplest for your team: keep stampantepy on GitLab and run pyexe-builder locally or copy stampantepy into the GitHub repo under `projects/stampantepy/`.

## Notes

- Windows `.exe` must be built on Windows (local PC, VM, or `windows-latest` on GitHub Actions).
- Linux builds on `ubuntu-latest` or any Linux machine.
- Production totems install the artifact from `dist/`, not this tool.
