import ast
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "dev-flow"
PHASES = ["frame", "discover", "specify", "plan", "implement", "verify", "review", "close"]
PHASE_SECTIONS = [
    "Result",
    "Required when",
    "Entry conditions",
    "Inputs",
    "Produce",
    "Mechanical exit checks",
    "Semantic exit checks",
    "Allowed mutations",
    "Allowed transitions",
    "Blocking conditions",
]


def frontmatter(text):
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


class SkillStructureTest(unittest.TestCase):
    def test_frontmatter_has_only_portable_activation_fields(self):
        fields = frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8"))

        self.assertIsNotNone(fields)
        self.assertEqual(set(fields), {"name", "description"})
        self.assertEqual(fields["name"], "dev-flow")
        self.assertTrue(fields["description"].startswith("Use when "))
        self.assertLessEqual(len(fields["description"]), 500)

    def test_skill_routes_every_phase_to_one_reference(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for phase in PHASES:
            link = f"references/phase-{phase}.md"
            self.assertEqual(text.count(link), 1, link)
            self.assertTrue((SKILL / link).is_file(), link)

    def test_phase_references_use_one_contract_shape(self):
        for phase in PHASES:
            path = SKILL / "references" / f"phase-{phase}.md"
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"# Phase: {phase}\n"), path.name)
            headings = re.findall(r"^## (.+)$", text, re.MULTILINE)
            self.assertEqual(headings, PHASE_SECTIONS, path.name)

    def test_markdown_links_inside_skill_are_not_broken(self):
        markdown_files = [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]
        for source in markdown_files:
            text = source.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (source.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(resolved.exists(), f"{source}: broken link {target}")

    def test_runtime_script_imports_only_standard_library(self):
        path = SKILL / "scripts" / "flowctl.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
        self.assertLessEqual(imports, sys.stdlib_module_names)

    def test_runtime_instructions_do_not_require_external_workflow_products(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]
        ).lower()
        for forbidden in ("beads", "openspec", "superpowers:", "tasks.md tracker"):
            self.assertNotIn(forbidden, text)

    def test_openai_metadata_matches_skill_name(self):
        text = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        prompt = re.search(r'^\s*default_prompt:\s*"([^"]+)"$', text, re.MULTILINE)
        short = re.search(r'^\s*short_description:\s*"([^"]+)"$', text, re.MULTILINE)

        self.assertIsNotNone(prompt)
        self.assertIn("$dev-flow", prompt.group(1))
        self.assertIsNotNone(short)
        self.assertGreaterEqual(len(short.group(1)), 25)
        self.assertLessEqual(len(short.group(1)), 64)


if __name__ == "__main__":
    unittest.main()
