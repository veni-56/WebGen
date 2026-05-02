#!/usr/bin/env python3
"""
server.py v3 — SaaS Website Builder Backend
SQLite project persistence, publish, multi-project support.
"""
import json, os, sys, shutil, tempfile, zipfile, uuid, sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory

BUILDER_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BUILDER_DIR))
from build import build

app = Flask(__name__, static_folder=str(Path(__file__).parent))
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024

UPLOADS_DIR  = Path(__file__).parent / "uploads"
PUBLISH_DIR  = Path(__file__).parent / "published"
DB_PATH      = Path(__file__).parent / "projects.db"
UPLOADS_DIR.mkdir(exist_ok=True)
PUBLISH_DIR.mkdir(exist_ok=True)

# ── Bridge script injected into every preview page ────────────────────────────
BRIDGE = """<script>
(function(){
  const S={};
  let sel=null;

  // Inject styles
  const st=document.createElement('style');
  st.textContent=`
    [data-wbs]{position:relative;cursor:pointer;transition:outline .12s,box-shadow .12s}
    [data-wbs]:hover{outline:2px dashed rgba(108,99,255,.45);outline-offset:3px}
    [data-wbs].wbs-sel{outline:2.5px solid #6c63ff!important;outline-offset:3px;box-shadow:0 0 0 4px rgba(108,99,255,.12)!important}
    .wbs-label{position:absolute;top:-22px;left:0;background:#6c63ff;color:#fff;font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px 4px 0 0;letter-spacing:.04em;pointer-events:none;z-index:9999;white-space:nowrap}
    .wbs-tb{position:absolute;top:-22px;right:0;display:flex;gap:2px;background:#1e1b4b;border-radius:4px;padding:2px 4px;z-index:9999;opacity:0;transition:opacity .15s;pointer-events:none}
    [data-wbs]:hover .wbs-tb,[data-wbs].wbs-sel .wbs-tb{opacity:1;pointer-events:auto}
    .wbs-tb button{background:none;border:none;color:#c4b5fd;cursor:pointer;font-size:11px;padding:1px 4px;border-radius:3px;line-height:1.4}
    .wbs-tb button:hover{background:rgba(255,255,255,.15);color:#fff}
    [contenteditable]:focus{outline:2px solid #6c63ff;outline-offset:1px;border-radius:2px;background:rgba(108,99,255,.04)}
  `;
  document.head.appendChild(st);

  function tag(){
    let idx={};
    ['section','header','footer','nav','article','aside','main'].forEach(t=>{
      document.querySelectorAll(t).forEach(el=>{
        if(el.dataset.wbs) return;
        idx[t]=(idx[t]||0)+1;
        const id=t+'_'+idx[t];
        el.dataset.wbs=id;
        el.style.position='relative';
        // Label
        const lb=document.createElement('div');
        lb.className='wbs-label';
        lb.textContent=t+(idx[t]>1?' '+idx[t]:'');
        el.appendChild(lb);
        // Toolbar
        const tb=document.createElement('div');
        tb.className='wbs-tb';
        tb.innerHTML=`
          <button title="Edit" onclick="wbsSel(this.closest('[data-wbs]'))">✏</button>
          <button title="Duplicate" onclick="wbsAct('dup',this.closest('[data-wbs]').dataset.wbs)">⧉</button>
          <button title="Toggle" onclick="wbsAct('hide',this.closest('[data-wbs]').dataset.wbs)">👁</button>
          <button title="Delete" onclick="wbsAct('del',this.closest('[data-wbs]').dataset.wbs)">��</button>
        `;
        el.appendChild(tb);
      });
    });
  }

  window.wbsSel=function(el){
    if(sel){sel.classList.remove('wbs-sel');}
    sel=el; el.classList.add('wbs-sel');
    const name=el.id||el.className.split(' ')[0]||el.dataset.wbs;
    parent.postMessage({type:'wbs-select',id:el.dataset.wbs,name},'*');
  };
  window.wbsAct=function(a,id){parent.postMessage({type:'wbs-action',action:a,id},'*');};

  document.addEventListener('click',e=>{
    const el=e.target.closest('[data-wbs]');
    if(el){e.stopPropagation();wbsSel(el);}
    else{if(sel){sel.classList.remove('wbs-sel');sel=null;}parent.postMessage({type:'wbs-deselect'},'*');}
  },true);

  document.addEventListener('dblclick',e=>{
    const el=e.target;
    if(['H1','H2','H3','H4','P','SPAN','A','LI','BUTTON'].includes(el.tagName)){
      el.contentEditable='true'; el.focus();
      el.addEventListener('blur',function f(){
        el.contentEditable='false'; el.removeEventListener('blur',f);
        parent.postMessage({type:'wbs-text',tag:el.tagName,text:el.innerText,
          sec:el.closest('[data-wbs]')?.dataset.wbs},'*');
      });
    }
  });

  document.addEventListener('click',e=>{
    if(e.target.tagName==='IMG'&&e.altKey){
      parent.postMessage({type:'wbs-img',src:e.target.src,
        sec:e.target.closest('[data-wbs]')?.dataset.wbs},'*');
    }
  });

  window.addEventListener('message',e=>{
    if(!e.data?.type) return;
    if(e.data.type==='wbs-theme'){
      let s=document.getElementById('wbs-lt');
      if(!s){s=document.createElement('style');s.id='wbs-lt';document.head.appendChild(s);}
      s.textContent=e.data.css;
    }
    if(e.data.type==='wbs-hl'){
      document.querySelectorAll('[data-wbs]').forEach(x=>x.classList.remove('wbs-sel'));
      const t=document.querySelector('[data-wbs="'+e.data.id+'"]');
      if(t){t.classList.add('wbs-sel');t.scrollIntoView({behavior:'smooth',block:'center'});}
    }
    if(e.data.type==='wbs-replace-img'){
      document.querySelectorAll('img').forEach(img=>{
        if(img.src===e.data.old||img.src.endsWith(e.data.old)) img.src=e.data.new;
      });
    }
  });

  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',tag):tag();
})();
</script>"""


# ── SQLite DB ─────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            config      TEXT NOT NULL,
            published   INTEGER DEFAULT 0,
            publish_url TEXT DEFAULT '',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit(); conn.close()

init_db()

def _inject_bridge(html):
    return html.replace("</body>", BRIDGE + "\n</body>")

def _build_to_dir(cfg, out_dir, visual=False):
    out_dir.mkdir(parents=True, exist_ok=True)
    build(cfg, out_dir, mode="static", minify=False)
    css = (out_dir/"style.css").read_text(encoding="utf-8") if (out_dir/"style.css").exists() else ""
    js  = (out_dir/"script.js").read_text(encoding="utf-8") if (out_dir/"script.js").exists() else ""
    for f in out_dir.glob("*.html"):
        html = f.read_text(encoding="utf-8")
        html = html.replace('<link rel="stylesheet" href="style.css"/>', f"<style>{css}</style>")
        html = html.replace('<script src="script.js"></script>', f"<script>{js}</script>")
        if visual:
            html = _inject_bridge(html)
        f.write_text(html, encoding="utf-8")

# ── Serve UI ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(str(Path(__file__).parent), "index.html")

@app.route("/uploads/<path:fn>")
def serve_upload(fn):
    return send_from_directory(str(UPLOADS_DIR), fn)

@app.route("/published/<pid>/<path:fn>")
def serve_published(pid, fn):
    return send_from_directory(str(PUBLISH_DIR / pid), fn)

@app.route("/preview/<pid>/<path:fn>")
def serve_preview(pid, fn):
    d = Path(tempfile.gettempdir()) / f"wbs_{pid}"
    return send_from_directory(str(d), fn)

# ── Projects CRUD ─────────────────────────────────────────────────────────────

@app.route("/api/projects", methods=["GET"])
def list_projects():
    conn = get_db()
    rows = conn.execute("SELECT id,name,published,publish_url,created_at,updated_at FROM projects ORDER BY updated_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/projects", methods=["POST"])
def create_project():
    data = request.get_json(silent=True) or {}
    pid  = uuid.uuid4().hex[:12]
    name = data.get("name", "Untitled Project")
    cfg  = data.get("config", {})
    conn = get_db()
    conn.execute("INSERT INTO projects (id,name,config) VALUES (?,?,?)", (pid, name, json.dumps(cfg)))
    conn.commit(); conn.close()
    return jsonify({"ok": True, "id": pid, "name": name})

@app.route("/api/projects/<pid>", methods=["GET"])
def get_project(pid):
    conn = get_db()
    row  = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    conn.close()
    if not row: return jsonify({"error": "Not found"}), 404
    d = dict(row); d["config"] = json.loads(d["config"])
    return jsonify(d)

@app.route("/api/projects/<pid>", methods=["PUT"])
def update_project(pid):
    data = request.get_json(silent=True) or {}
    cfg  = data.get("config")
    name = data.get("name")
    conn = get_db()
    if cfg and name:
        conn.execute("UPDATE projects SET config=?,name=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                     (json.dumps(cfg), name, pid))
    elif cfg:
        conn.execute("UPDATE projects SET config=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                     (json.dumps(cfg), pid))
    elif name:
        conn.execute("UPDATE projects SET name=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (name, pid))
    conn.commit(); conn.close()
    return jsonify({"ok": True})

@app.route("/api/projects/<pid>", methods=["DELETE"])
def delete_project(pid):
    conn = get_db()
    conn.execute("DELETE FROM projects WHERE id=?", (pid,))
    conn.commit(); conn.close()
    return jsonify({"ok": True})

# ── Preview (srcdoc) ──────────────────────────────────────────────────────────

@app.route("/api/preview", methods=["POST"])
def api_preview():
    data   = request.get_json(silent=True) or {}
    cfg    = data.get("config")
    page   = data.get("page", "home")
    visual = data.get("visual", True)
    if not cfg: return jsonify({"error": "No config"}), 400
    try:
        tmp = Path(tempfile.gettempdir()) / "wbs_srcdoc"
        _build_to_dir(cfg, tmp, visual=visual)
        pages    = cfg.get("pages", {})
        filename = pages.get(page, {}).get("file", "index.html")
        f = tmp / filename
        if not f.exists(): f = tmp / "index.html"
        return jsonify({"html": f.read_text(encoding="utf-8"), "ok": True})
    except Exception as e:
        return jsonify({"error": str(e), "ok": False}), 500

# ── Preview URL ───────────────────────────────────────────────────────────────

@app.route("/api/preview-url", methods=["POST"])
def api_preview_url():
    data = request.get_json(silent=True) or {}
    cfg  = data.get("config")
    pid  = data.get("project_id", "default")
    if not cfg: return jsonify({"error": "No config"}), 400
    try:
        out = Path(tempfile.gettempdir()) / f"wbs_{pid}"
        _build_to_dir(cfg, out, visual=True)
        pages = cfg.get("pages", {})
        urls  = {k: f"/preview/{pid}/{v.get('file','index.html')}" for k,v in pages.items()}
        return jsonify({"ok": True, "pages": urls, "base": f"/preview/{pid}/"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Publish ───────────────────────────────────────────────────────────────────

@app.route("/api/publish/<pid>", methods=["POST"])
def api_publish(pid):
    conn = get_db()
    row  = conn.execute("SELECT config FROM projects WHERE id=?", (pid,)).fetchone()
    if not row: conn.close(); return jsonify({"error": "Project not found"}), 404
    cfg = json.loads(row["config"])
    try:
        out = PUBLISH_DIR / pid
        _build_to_dir(cfg, out, visual=False)
        url = f"/published/{pid}/index.html"
        conn.execute("UPDATE projects SET published=1,publish_url=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (url, pid))
        conn.commit(); conn.close()
        return jsonify({"ok": True, "url": url})
    except Exception as e:
        conn.close(); return jsonify({"error": str(e)}), 500

# ── Export ZIP ────────────────────────────────────────────────────────────────

@app.route("/api/export", methods=["POST"])
def api_export():
    data   = request.get_json(silent=True) or {}
    cfg    = data.get("config")
    mode   = data.get("mode", "static")
    if not cfg: return jsonify({"error": "No config"}), 400
    try:
        out  = Path(tempfile.gettempdir()) / "wbs_export"
        build(cfg, out, mode=mode, minify=False)
        name = cfg.get("site_name","website").lower().replace(" ","_")
        zp   = Path(tempfile.gettempdir()) / f"{name}.zip"
        import zipfile as zf
        with zf.ZipFile(zp,"w",zf.ZIP_DEFLATED) as z:
            for f in out.rglob("*"):
                if f.is_file(): z.write(f, f.relative_to(out))
        return send_file(str(zp), as_attachment=True, download_name=f"{name}.zip", mimetype="application/zip")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Upload ────────────────────────────────────────────────────────────────────

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files: return jsonify({"error": "No file"}), 400
    f = request.files["file"]
    ext = f.filename.rsplit(".",1)[-1].lower() if "." in f.filename else "png"
    if ext not in {"png","jpg","jpeg","gif","webp","svg"}: return jsonify({"error":"Invalid type"}),400
    name = uuid.uuid4().hex + "." + ext
    f.save(str(UPLOADS_DIR / name))
    return jsonify({"ok": True, "url": f"/uploads/{name}"})

# ── Legacy save/config ────────────────────────────────────────────────────────

@app.route("/api/save", methods=["POST"])
def api_save():
    data = request.get_json(silent=True) or {}
    cfg  = data.get("config")
    if not cfg: return jsonify({"error":"No config"}),400
    (BUILDER_DIR/"config.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
    return jsonify({"ok":True})

@app.route("/api/config", methods=["GET"])
def api_config():
    p = BUILDER_DIR/"config.json"
    if p.exists(): return jsonify(json.loads(p.read_text(encoding="utf-8")))
    return jsonify({"error":"Not found"}),404

if __name__ == "__main__":
    print("🚀 Website Builder → http://localhost:4000")
    app.run(host="0.0.0.0", port=4000, debug=True)
