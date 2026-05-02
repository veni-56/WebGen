"""
app/services/ai_engine.py — AI Engine Service Layer
Orchestrates the full 4-step pipeline:
  Step 1: NLP Intent Parsing     (nlp.parse_prompt)
  Step 2: Intent Analysis        (planner.analyze_intent)
  Step 3: Auto Design + Arch     (planner.auto_design + build_architecture)
  Step 4: Code Generation        (generator.build_project)

This is the single entry point for all AI generation in the platform.
"""
import json
import uuid
from pathlib import Path

# Import from root-level modules
from nlp     import parse_prompt, list_themes, get_theme
from planner import full_plan
from codegen import generate_structured, slugify
from generator import build_project, read_file, project_exists, make_zip


class AIEngine:
    """
    Stateless AI engine service.
    All methods are static — instantiate or use class directly.
    """

    @staticmethod
    def parse(prompt: str) -> dict:
        """
        Step 1+2+3: Parse prompt → full config + plan.
        Returns enriched config dict ready for code generation.
        """
        config = parse_prompt(prompt)
        plan   = full_plan(prompt, config)
        config["_plan"] = plan
        return config

    @staticmethod
    def generate(prompt: str, project_id: str = None) -> dict:
        """
        Full pipeline: prompt → structured output with all files.
        Returns the complete structured result dict.
        """
        if not project_id:
            project_id = str(uuid.uuid4())[:8]
        return generate_structured(prompt, project_id)

    @staticmethod
    def generate_from_config(config: dict, project_id: str = None) -> dict:
        """
        Generate from an existing config dict (e.g. from wizard).
        Returns {"files": [...], "type": "..."}
        """
        if not project_id:
            project_id = str(uuid.uuid4())[:8]
        return build_project(project_id, config)

    @staticmethod
    def preview_html(config: dict) -> str:
        """
        Generate a temporary project and return inlined HTML for preview.
        Cleans up temp files after reading.
        """
        import shutil
        from pathlib import Path
        from generator import GENERATED_DIR

        tmp_id = "preview_" + str(uuid.uuid4())[:6]
        try:
            build_project(tmp_id, config)
            html = read_file(tmp_id, "index.html") or ""
            css  = read_file(tmp_id, "style.css")  or ""
            js   = read_file(tmp_id, "script.js")  or ""
            html = html.replace('<link rel="stylesheet" href="style.css"/>',
                                f"<style>{css}</style>")
            html = html.replace('<script src="script.js"></script>',
                                f"<script>{js}</script>")
            return html
        finally:
            tmp_path = GENERATED_DIR / tmp_id
            if tmp_path.exists():
                shutil.rmtree(tmp_path)

    @staticmethod
    def read_file(project_id: str, filepath: str) -> str | None:
        return read_file(project_id, filepath)

    @staticmethod
    def project_exists(project_id: str) -> bool:
        return project_exists(project_id)

    @staticmethod
    def make_zip(project_id: str) -> Path:
        return make_zip(project_id)

    @staticmethod
    def inline_preview(project_id: str) -> str | None:
        """Inline CSS/JS into a saved project's index.html for iframe preview."""
        html = read_file(project_id, "index.html") or ""
        css  = read_file(project_id, "style.css")  or ""
        js   = read_file(project_id, "script.js")  or ""
        if not html:
            return None
        html = html.replace('<link rel="stylesheet" href="style.css"/>',
                            f"<style>{css}</style>")
        html = html.replace('<script src="script.js"></script>',
                            f"<script>{js}</script>")
        return html
