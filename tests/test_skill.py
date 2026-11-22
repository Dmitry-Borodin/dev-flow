import re
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "dev-flow"
SKILL = SKILL_DIR / "SKILL.md"
ROLES = sorted((SKILL_DIR / "roles").glob("*.md"))
MAX_SKILL_LINES = 500
MAX_ROLE_LINES = 200
MAX_WIDTH = 100
PROJECT_SPECIFIC = re.compile(
    r"\b(subyard|yard|claude|codex|opus|sonnet|haiku|fable|gpt|gh|github|container"
    r"|agents\.md|claude\.md)\b",
    re.IGNORECASE,
)


def body(lines):
    """Lines after the frontmatter, if any."""
    if lines and lines[0].strip() == "---":
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
        return lines[end + 1 :]
    return lines


def slug(heading):
    """Markdown heading anchor: lowercase, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


class SkillStructureTest(unittest.TestCase):
    def setUp(self):
        self.files = [SKILL, *ROLES]
        self.text = {path: path.read_text(encoding="utf-8") for path in self.files}

    def test_frontmatter(self):
        lines = self.text[SKILL].splitlines()
        self.assertEqual(lines[0].strip(), "---")
        fields = {}
        for line in lines[1:]:
            if line.strip() == "---":
                break
            key, sep, value = line.partition(":")
            if sep:
                fields[key.strip()] = value.strip().strip("\"'")
        self.assertEqual(fields.get("name"), "dev-flow")
        self.assertTrue(fields.get("description"))

    def test_line_budgets(self):
        self.assertLessEqual(len(self.text[SKILL].splitlines()), MAX_SKILL_LINES)
        for path in ROLES:
            with self.subTest(path=path.name):
                self.assertLessEqual(len(self.text[path].splitlines()), MAX_ROLE_LINES)

    def test_width(self):
        for path in self.files:
            lines = self.text[path].splitlines()
            offset = len(lines) - len(body(lines))
            wide = [offset + i + 1 for i, line in enumerate(body(lines)) if len(line) > MAX_WIDTH]
            with self.subTest(path=path.name):
                self.assertEqual(wide, [])

    def test_generic(self):
        for path in self.files:
            with self.subTest(path=path.name):
                self.assertEqual(PROJECT_SPECIFIC.findall(self.text[path]), [])

    def test_skill_anchors_exist(self):
        anchors = {slug(h) for h in re.findall(r"^#+ (.+)$", self.text[SKILL], re.MULTILINE)}
        linked = set(re.findall(r"\]\(#([^)]+)\)", self.text[SKILL]))
        for path in ROLES:
            linked |= set(re.findall(r"\]\(\.\./SKILL\.md#([^)]+)\)", self.text[path]))
        self.assertTrue(linked)
        self.assertEqual(sorted(linked - anchors), [])

    def test_role_links_exist(self):
        links = set(re.findall(r"\]\((roles/[^)#]+\.md)", self.text[SKILL]))
        self.assertTrue(links)
        for link in sorted(links):
            with self.subTest(link=link):
                self.assertTrue((SKILL_DIR / link).is_file())


if __name__ == "__main__":
    unittest.main()
