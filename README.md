Install steps

- Python 3.10.15

```bash
    python3 -m venv venv
```
   - Activate the virtual environment:
     
```bash
     source venv/bin/activate
```
3. **Install Python Dependencies**:
   - Create a `requirements.txt` file if it doesn't exist and list your Python dependencies there.
   - Install the dependencies:
     
```bash
     pip install -r requirements.txt
```
4. **Install TeX Live Manager (tlmgr)**:
   - Install MacTeX, which includes `tlmgr`, from [tug.org/mactex](https://www.tug.org/mactex/).
   - After installation, ensure `tlmgr` is in your PATH. You can add it by adding the following line to your `.bash_profile` or `.zshrc`:
     
```bash
     export PATH="/usr/local/texlive/2023/bin/x86_64-darwin:$PATH"
```
   - Source the profile to update the PATH:
     
```bash
     source ~/.bash_profile  # or source ~/.zshrc
```

5. **Install LaTeX Packages using tlmgr**:
   - Run the following command to install the required LaTeX packages:
     
```bash
     tlmgr install moderncv geometry babel fontawesome5 multibib graphicx
```

```
docker buildx build --platform linux/amd64 -t resume-builder:latest .
```

By following these steps, you will set up your Python environment and install the necessary LaTeX packages using `tlmgr`. install moderncv geometry babel fontawesome5 multibib graphicx
