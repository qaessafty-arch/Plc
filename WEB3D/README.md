# SPM-420 web viewer (NULL-TECH)

Static site: interactive 3D model of the line plus a project overview and downloads.
No build step. Deployed on Vercel with root directory `WEB3D`.

- `index.html`, `style.css`, `app.js`: page and viewer (three.js 0.160.0, bundled in `vendor/three`, MIT licence).
- `model/spm420.glb`, `model/parts.json`: regenerate with `python3 CAD/SCRIPTS/export_web.py` after `build_cad.py`.
- `downloads/`, `img/`: copies of the PDF overview, component sheets, STEP assembly and drawings.

Local preview: `cd WEB3D && python3 -m http.server 8000`, then open http://localhost:8000.
