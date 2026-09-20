"""連作漫画の検査手順が入口・既存Skill・作品雛形から外れないことを検査する。

画像の表情・構図・面白さを判定するテストではない。
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "manga-series-variation"
SKILL = ROOT / "skills" / SKILL_NAME / "SKILL.md"
TEMPLATE = ROOT / "templates/manga-project/docs/production/PAGE-VARIATION.md"


def read(path):
    return path.read_text(encoding="utf-8-sig")


class MangaSeriesVariationContractTests(unittest.TestCase):
    def test_skill_frontmatter_is_discoverable(self):
        text = read(SKILL)
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: " + SKILL_NAME, text)
        self.assertRegex(text, r"(?m)^description: .+")

    def test_root_and_project_entrypoints_require_variation(self):
        for path in (ROOT / "AGENTS.md", ROOT / "templates/manga-project/AGENTS.md"):
            with self.subTest(path=str(path)):
                text = read(path)
                self.assertIn(SKILL_NAME, text)
                self.assertIn("PAGE-VARIATION.md", text)
                self.assertIn("必須", text)

    def test_existing_roles_route_to_variation_skill(self):
        for name in ("manga-script-writing", "manga-art-direction",
                     "manga-ai-production", "manga-readability-review"):
            with self.subTest(skill=name):
                text = read(ROOT / "skills" / name / "SKILL.md")
                self.assertIn(SKILL_NAME, text)
                self.assertIn("PAGE-VARIATION.md", text)

    def test_skill_has_separate_planning_and_image_gates(self):
        text = read(SKILL)
        for marker in ("PLAN GATE", "VISUAL GATE", "LAYOUT COPY BAN",
                       "PAGE DIVERSITY LOCK", "EXPRESSION / ACTING LOCK",
                       "BEAT VARIATION LOCK", "意図した反復", "未確認", "実画像"):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_template_starts_unreviewed_and_covers_page_design(self):
        text = read(TEMPLATE)
        for field in ("ページ機能", "因果と接続", "コマ設計", "主ビジュアル",
                      "視点・距離・配置", "感情と演技", "会話の働き", "情報提示",
                      "まとめ欄の必要性", "前ページとの差分", "意図した反復",
                      "PLAN GATE: 未確認", "VISUAL GATE: 未確認"):
            with self.subTest(field=field):
                self.assertIn(field, text)
        self.assertNotRegex(text, r"(?:PLAN|VISUAL) GATE: PASS")

    def test_project_template_skill_reference_resolves(self):
        # New-MangaProject copies skills/ to .agents/skills/.
        targets = re.findall(r"`(\.agents/skills/[^`]+)`", read(TEMPLATE))
        self.assertTrue(targets)
        for target in targets:
            with self.subTest(target=target):
                source = ROOT / target.replace(".agents/skills/", "skills/", 1)
                self.assertTrue(source.is_file(), target)

    def test_existing_scaffold_mapping_covers_new_markdown(self):
        script = read(ROOT / "scripts/New-MangaProject.ps1")
        for source in ("Source = 'skills'", "Target = '.agents\\skills'",
                       "Source = 'templates\\manga-project'"):
            self.assertIn(source, script)
        self.assertEqual(SKILL.suffix, ".md")
        self.assertEqual(TEMPLATE.suffix, ".md")

    def test_rules_preserve_fixed_formats_and_honest_review(self):
        text = read(SKILL)
        self.assertIn("4コマ", text)
        self.assertIn("同じコマ数だけでFAILにはしない", text)
        self.assertIn("自動では変わらない", text)
        self.assertIn("実画像による検査を別に行い", text)


if __name__ == "__main__":
    unittest.main()
