"""
ui.py — NiceGUI frontend for the bank statement normalizer.

Setup:
    pip install nicegui

Run from your project root:
    python ui.py

Then open http://localhost:8080
"""

import tempfile
from pathlib import Path

from nicegui import ui

# ── Try to import project modules ─────────────────────────────────────────────
try:
    from banks import register_all
    from normalizer.registry import BankRegistry
    from normalizer.writers import write_statement, write_unmapped
    from normalizer.read_existing import load_existing_records
    from main import run, merge_records

    register_all()
    BANK_OPTIONS = sorted(BankRegistry.all_keys())
    PROJECT_LOADED = True
    LOAD_ERROR = ""
except Exception as exc:
    BANK_OPTIONS = ["wells_fargo", "citibank", "usaa", "norm"]
    PROJECT_LOADED = False
    LOAD_ERROR = str(exc)

# ── Mutable UI state ──────────────────────────────────────────────────────────
state = {
    "bank":            BANK_OPTIONS[0] if BANK_OPTIONS else "",
    "input":           None,   # path to temp file
    "input_name":      "",     # original filename for display
    "categories":      r"D:\data\statement-data\mapping.txt",
    "categories_name": "mapping.txt",
    "output":          r"D:\data\statement-data\data",
    "credit":          False,
    "override":        False,
}

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  body, .nicegui-content { background:#0d1117 !important; }

  .shell {
    min-height:100vh; background:#0d1117;
    font-family:'IBM Plex Sans',sans-serif; color:#c9d1d9;
    padding:2.5rem 2rem; max-width:820px; margin:0 auto;
  }

  /* header */
  .hdr { display:flex; align-items:baseline; gap:.85rem;
         border-bottom:1px solid #1e2d3d; padding-bottom:1.2rem; margin-bottom:2.25rem; }
  .hdr-title { font-family:'IBM Plex Mono',monospace; font-size:1.3rem;
               font-weight:600; color:#58a6ff; }
  .hdr-sub   { font-family:'IBM Plex Mono',monospace; font-size:.72rem; color:#3a4f63; }

  /* field label */
  .flabel { font-family:'IBM Plex Mono',monospace; font-size:.68rem; font-weight:500;
            text-transform:uppercase; letter-spacing:.1em; color:#4d6278; margin-bottom:.45rem; }

  /* file display */
  .file-row { display:flex; gap:.5rem; align-items:stretch; width:100%; }
  .file-disp {
    flex:1; background:#161b22; border:1px solid #21303f; border-radius:6px;
    padding:.5rem .85rem; font-family:'IBM Plex Mono',monospace; font-size:.8rem;
    color:#58a6ff; min-height:2.4rem; display:flex; align-items:center;
    overflow:hidden; white-space:nowrap; text-overflow:ellipsis;
  }
  .file-disp.empty { color:#3a4f63; font-style:italic; }

  /* select */
  .bank-sel .q-field__control {
    background:#161b22 !important; border:1px solid #21303f !important;
    border-radius:6px !important; font-family:'IBM Plex Mono',monospace !important;
    font-size:.85rem !important; color:#c9d1d9 !important;
  }

  /* path input */
  .path-inp .q-field__control {
    background:#161b22 !important; border:1px solid #21303f !important;
    border-radius:6px !important; font-family:'IBM Plex Mono',monospace !important;
    font-size:.8rem !important; min-height:2.4rem !important;
  }
  .path-inp .q-field__native, .path-inp input { color:#58a6ff !important; }
  .path-inp .q-placeholder { color:#3a4f63 !important; }

  /* browse upload button */
  .browse .q-btn {
    background:#161b22 !important; border:1px solid #21303f !important;
    border-radius:6px !important; color:#8b949e !important;
    font-family:'IBM Plex Mono',monospace !important; font-size:.75rem !important;
    padding:0 1rem !important; height:2.4rem !important;
    transition:border-color .15s,color .15s;
  }
  .browse .q-btn:hover { border-color:#58a6ff !important; color:#58a6ff !important; }

  /* divider */
  .divider { border:none; border-top:1px solid #1e2d3d; margin:1.5rem 0; }

  /* toggles */
  .toggle-row  { display:flex; gap:2.5rem; margin-bottom:1.75rem; align-items:center; }
  .toggle-item { display:flex; align-items:center; gap:.6rem; }
  .toggle-lbl  { font-family:'IBM Plex Mono',monospace; font-size:.8rem; color:#8b949e; }
  .toggle-desc { font-size:.7rem; color:#3a4f63; font-family:'IBM Plex Mono',monospace; }

  /* run button */
  .run-btn {
    background:#1a7f37 !important; color:#fff !important;
    font-family:'IBM Plex Mono',monospace !important; font-weight:600 !important;
    font-size:.9rem !important; border-radius:6px !important; border:none !important;
    padding:0 2.25rem !important; height:2.75rem !important;
    letter-spacing:.04em; transition:background .15s;
  }
  .run-btn:hover   { background:#238636 !important; }
  .run-btn[disabled] { background:#21303f !important; color:#4d6278 !important; }

  /* log panel */
  .log-panel {
    background:#0a0e13; border:1px solid #1e2d3d; border-radius:8px;
    padding:1.2rem 1.5rem; min-height:140px;
    font-family:'IBM Plex Mono',monospace; font-size:.82rem; line-height:1.8;
    margin-top:1.75rem; width:100%;
  }
  .ll  { display:flex; gap:.75rem; }
  .lk  { color:#4d6278; min-width:210px; }
  .lv  { color:#58a6ff; }
  .lok { color:#3fb950; }
  .lwn { color:#d29922; }
  .ler { color:#f87171; }

  /* warn banner */
  .warn-banner {
    background:#2d1a00; border:1px solid #7d4e00; border-radius:6px;
    padding:.75rem 1rem; font-family:'IBM Plex Mono',monospace;
    font-size:.78rem; color:#d29922; margin-bottom:1.5rem; line-height:1.6;
  }
</style>
"""


# ── Parser execution ──────────────────────────────────────────────────────────
def execute(log: ui.html, status: ui.html, btn: ui.button):

    # Validate
    errors = []
    if not state["bank"]:
        errors.append("No bank selected.")
    if not state["input"]:
        errors.append("No input file selected.")
    elif not Path(state["input"]).exists():
        errors.append(f"Input file missing: {state['input']}")
    if state["output"] and not Path(state["output"]).is_dir():
        errors.append(f"Output directory does not exist: {state['output']}")

    if errors:
        log.set_content(
            "".join(f"<div class='ler'>✗ {e}</div>" for e in errors)
        )
        return

    if not PROJECT_LOADED:
        log.set_content(
            f"<div class='ler'>Cannot load project modules — "
            f"run ui.py from your project root.<br>{LOAD_ERROR}</div>"
        )
        return

    btn.disable()
    status.set_content("<span style='color:#d29922'>Running…</span>")
    log.set_content("<div style='color:#4d6278'>Starting…</div>")

    try:
        input_path    = Path(state["input"])
        category_path = Path(state["categories"]) if state["categories"] else None
        output_dir    = Path(state["output"]) if state["output"] else Path.cwd() / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path   = output_dir / "Normalized_Statement.txt"

        existing_records             = load_existing_records(output_path)
        parsed_records, unmapped     = run(
            state["bank"], input_path, category_path,
            state["credit"], existing_records,
        )
        merged, added, replaced      = merge_records(existing_records, parsed_records)
        write_statement(output_path, merged)

        parsed_count = len(parsed_records)

        def row(key, val, cls="lv"):
            return f"<div class='ll'><span class='lk'>{key}</span><span class='{cls}'>{val}</span></div>"

        html  = row("Parsed records",  str(parsed_count))
        html += row("Added records",   str(added),    "lok" if added   else "lv")
        html += row("Updated records", str(replaced), "lok" if replaced else "lv")
        html += row("Unmapped categories",
                    str(len(unmapped)) if unmapped else "none",
                    "lwn" if unmapped else "lv")
        html += row("Output file", str(output_path))

        if unmapped:
            unmapped_path = output_dir / "Unmapped_Categories.txt"
            write_unmapped(unmapped_path, sorted(unmapped))
            html += row("Unmapped file", str(unmapped_path), "lwn")

        log.set_content(html)
        status.set_content("<span style='color:#3fb950'>Done ✓</span>")

    except Exception as exc:
        log.set_content(f"<div class='ler'>✗ {exc}</div>")
        status.set_content("<span style='color:#f87171'>Failed ✗</span>")
    finally:
        btn.enable()


# ── Page ──────────────────────────────────────────────────────────────────────
@ui.page("/")
def index():
    ui.add_head_html(CSS)

    with ui.element("div").classes("shell"):

        # Header
        with ui.element("div").classes("hdr"):
            ui.html("<span class='hdr-title'>statement-normalizer</span>")
            ui.html("<span class='hdr-sub'>local · v1.0</span>")

        # Module load warning
        if not PROJECT_LOADED:
            ui.html(
                f"<div class='warn-banner'>⚠ Project modules not found. "
                f"Run <code>python ui.py</code> from your project root.<br>"
                f"<span style='color:#8b949e'>{LOAD_ERROR}</span></div>"
            )

        # Bank selector
        with ui.element("div").style("margin-bottom:1.35rem"):
            ui.html("<div class='flabel'>Bank</div>")
            bank_sel = (
                ui.select(options=BANK_OPTIONS, value=state["bank"],
                          on_change=lambda e: state.update(bank=e.value))
                .classes("bank-sel")
                .style("width:100%")
            )

        # Input file
        with ui.element("div").style("margin-bottom:1.35rem"):
            ui.html("<div class='flabel'>Input Statement &nbsp;(.csv or .tsv)</div>")
            with ui.element("div").classes("file-row"):
                input_disp = ui.html("No file selected…").classes("file-disp empty")

                async def on_input(e):
                    name = getattr(e, 'name', None) or e.file.name
                    content = getattr(e, 'content', None) or e.file
                    suffix = Path(name).suffix or ".csv"
                    tmp = tempfile.NamedTemporaryFile(
                        delete=False, suffix=suffix, prefix="stmt_"
                    )
                    tmp.write(await content.read())
                    tmp.close()
                    state["input"] = tmp.name
                    input_disp.classes(remove="empty").set_content(name)

                (
                    ui.upload(label="Browse…", on_upload=on_input, auto_upload=True)
                    .props('accept=".csv,.tsv,.txt" flat dense')
                    .classes("browse")
                )

        # Categories file
        with ui.element("div").style("margin-bottom:1.35rem"):
            ui.html("<div class='flabel'>Categories File &nbsp;(optional · tab-delimited)</div>")
            with ui.element("div").classes("file-row"):
                cat_disp = ui.html(state["categories"]).classes("file-disp")

                async def on_cat(e):
                    name = getattr(e, 'name', None) or e.file.name
                    content = getattr(e, 'content', None) or e.file
                    suffix = Path(name).suffix or ".txt"
                    tmp = tempfile.NamedTemporaryFile(
                        delete=False, suffix=suffix, prefix="cat_"
                    )
                    tmp.write(await content.read())
                    tmp.close()
                    state["categories"] = tmp.name
                    cat_disp.classes(remove="empty").set_content(name)

                (
                    ui.upload(label="Browse…", on_upload=on_cat, auto_upload=True)
                    .props('accept=".txt,.tsv,.csv" flat dense')
                    .classes("browse")
                )

        # Output directory
        with ui.element("div").style("margin-bottom:1.35rem"):
            ui.html("<div class='flabel'>Output Directory</div>")
            (
                ui.input(value=r"D:\data\statement-data\data",
                         placeholder="Paste a directory path, or leave blank for ./output/",
                         on_change=lambda e: state.update(output=e.value.strip().strip('"\'')))
                .classes("path-inp")
                .style("width:100%")
            )

        ui.element("hr").classes("divider")

        # Toggles
        with ui.element("div").classes("toggle-row"):
            with ui.element("div").classes("toggle-item"):
                sw_credit = ui.switch(value=False,
                                      on_change=lambda e: state.update(credit=e.value)
                                      ).props("color=blue-5")

                with ui.element("div"):
                    ui.html("<div class='toggle-lbl'>--credit</div>")
                    ui.html("<div class='toggle-desc'>treat as credit card statement</div>")

            with ui.element("div").classes("toggle-item"):
                sw_override = ui.switch(value=False,
                                        on_change=lambda e: state.update(override=e.value)
                                        ).props("color=blue-5")
                with ui.element("div"):
                    ui.html("<div class='toggle-lbl'>--override</div>")
                    ui.html("<div class='toggle-desc'>override protected categories</div>")

        # Run row
        with ui.row().style("align-items:center;gap:0"):
            run_btn    = ui.button("▶  Run").classes("run-btn")
            status_lbl = ui.html(
                "<span style='color:#4d6278'>Ready</span>"
            ).style("padding-left:1rem;font-family:'IBM Plex Mono',monospace;font-size:.78rem")

        # Log panel
        log_panel = ui.html(
            "<span style='color:#3a4f63'>"
            "Output will appear here after you click Run."
            "</span>"
        ).classes("log-panel")

        run_btn.on("click", lambda: execute(log_panel, status_lbl, run_btn))


ui.run(
    title="Statement Normalizer",
    host="127.0.0.1",
    port=8080,
    reload=False,
    dark=True,
    favicon="💰",
)