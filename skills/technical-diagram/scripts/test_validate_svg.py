import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from validate_svg import validate_svg

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TOKENS = Path(__file__).resolve().parents[1] / "assets" / "editorial-tokens.json"
TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "direct-svg-template.svg"


def write(directory: str, name: str, content: str) -> Path:
    path = Path(directory) / name
    path.write_text(content, encoding="utf-8")
    return path


class StructureTests(unittest.TestCase):
    def test_accepts_svg_with_positive_viewbox_and_unique_ids(self):
        with TemporaryDirectory() as directory:
            path = write(
                directory,
                "valid.svg",
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 10">'
                '<rect id="node" width="20" height="10"/></svg>',
            )
            report = validate_svg(path)
            self.assertEqual(report.errors, [])
            self.assertEqual(report.warnings, [])

    def test_rejects_missing_viewbox_and_duplicate_ids(self):
        with TemporaryDirectory() as directory:
            path = write(
                directory,
                "invalid.svg",
                '<svg xmlns="http://www.w3.org/2000/svg"><g id="same"/><g id="same"/></svg>',
            )
            self.assertEqual(validate_svg(path).errors, ["SVG has no viewBox", "duplicate ids: same"])


class LegibilityTests(unittest.TestCase):
    WIDE = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 300">'
        '<text x="100" y="50" font-size="14">USER</text></svg>'
    )

    def test_fails_when_scaled_label_drops_below_minimum(self):
        with TemporaryDirectory() as directory:
            report = validate_svg(write(directory, "wide.svg", self.WIDE), target_width=720)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("renders at 7.0px", report.errors[0])

    def test_passes_when_delivery_width_matches_or_gate_is_disabled(self):
        with TemporaryDirectory() as directory:
            path = write(directory, "wide.svg", self.WIDE)
            self.assertEqual(validate_svg(path, target_width=1440).errors, [])
            self.assertEqual(validate_svg(path, target_width=0).errors, [])

    def test_resolves_font_size_from_css_classes_and_inline_styles(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 100">'
            "<style>text{font-size:15px} .small{font-size:9px} .note text{font-size:10px}</style>"
            '<text x="10" y="20">fine</text>'
            '<text x="10" y="40" class="small">tiny</text>'
            '<g class="note"><text x="10" y="60">nested</text></g>'
            '<text x="10" y="80" style="font-size:11px">inline</text></svg>'
        )
        with TemporaryDirectory() as directory:
            report = validate_svg(write(directory, "css.svg", svg))
            self.assertEqual(len(report.errors), 1)
            self.assertIn("'tiny' 9px", report.errors[0])
            self.assertIn("'nested' 10px", report.errors[0])
            self.assertIn("'inline' 11px", report.errors[0])
            self.assertNotIn("'fine'", report.errors[0])


class LabelFitTests(unittest.TestCase):
    def test_warns_when_estimated_label_width_crowds_its_box(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100">'
            '<rect x="10" y="10" width="80" height="40"/>'
            '<text x="50" y="35" font-size="14" text-anchor="middle">APPLICATION SERVER</text>'
            '<rect x="200" y="10" width="160" height="40"/>'
            '<text x="280" y="35" font-size="14" text-anchor="middle">USER</text></svg>'
        )
        with TemporaryDirectory() as directory:
            report = validate_svg(write(directory, "fit.svg", svg))
            self.assertEqual(report.errors, [])
            self.assertEqual(len(report.warnings), 1)
            self.assertIn("'APPLICATION SERVER'", report.warnings[0])
            self.assertNotIn("'USER'", report.warnings[0])

    def test_sans_serif_labels_are_measured_narrower_than_monospace(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100">'
            "<style>.note{font-family:Helvetica,Arial,sans-serif}</style>"
            '<rect x="10" y="10" width="120" height="40"/>'
            '<text x="70" y="35" font-size="14" text-anchor="middle" class="note">Terminal launch</text>'
            '<rect x="200" y="10" width="120" height="40"/>'
            '<text x="260" y="35" font-size="14" text-anchor="middle" font-family="Menlo, monospace">Terminal launch</text></svg>'
        )
        with TemporaryDirectory() as directory:
            report = validate_svg(write(directory, "sans.svg", svg))
            self.assertEqual(len(report.warnings), 1)
            self.assertIn("~126px in a 120px box", report.warnings[0])

    def test_hangul_counts_as_full_width(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100">'
            '<rect x="10" y="10" width="100" height="40"/>'
            '<text x="60" y="35" font-size="14" text-anchor="middle">애플리케이션 서버</text></svg>'
        )
        with TemporaryDirectory() as directory:
            report = validate_svg(write(directory, "ko.svg", svg))
            self.assertEqual(len(report.warnings), 1)
            self.assertIn("~120px", report.warnings[0])


class TokenTests(unittest.TestCase):
    def test_flags_off_palette_colors_and_geometry_but_accepts_var_fallbacks(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">'
            "<style>.muted{fill:#555}</style>"
            '<rect x="0" y="0" width="50" height="20" rx="8" fill="var(--c-blue, #EAF1FE)" stroke="#0D0D0D" stroke-width="2"/>'
            '<rect x="60" y="0" width="50" height="20" rx="16" fill="#123456" stroke-width="1.2"/>'
            '<text x="5" y="15" font-size="14" fill="var(--c-ink)">ok</text></svg>'
        )
        with TemporaryDirectory() as directory:
            report = validate_svg(write(directory, "tokens.svg", svg), tokens_path=TOKENS)
            joined = "\n".join(report.warnings)
            self.assertIn("#123456", joined)
            self.assertIn("#555555", joined)
            self.assertNotIn("#eaf1fe", joined)
            self.assertIn("corner radii outside the tokens: 8", joined)
            self.assertIn("stroke widths outside the tokens: 2", joined)

    def test_mask_contents_are_not_treated_as_painted_colors(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">'
            '<mask id="m"><rect width="200" height="100" fill="white"/>'
            '<rect x="10" y="10" width="40" height="16" fill="rgba(0,0,0,0.75)"/></mask>'
            '<path d="M0 50 H200" stroke="#0D0D0D" fill="none" mask="url(#m)"/></svg>'
        )
        with TemporaryDirectory() as directory:
            report = validate_svg(write(directory, "mask.svg", svg), tokens_path=TOKENS)
            self.assertEqual(report.warnings, [])

    def test_tala_output_passes_the_default_column_cleanly(self):
        report = validate_svg(FIXTURES / "d2-tala-example.svg", tokens_path=TOKENS)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_d2_output_is_checked_by_painted_attributes_only(self):
        report = validate_svg(FIXTURES / "d2-elk-example.svg", target_width=1100, tokens_path=TOKENS)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])


class RealFigureTests(unittest.TestCase):
    def test_d2_elk_example_fails_the_default_column_but_passes_its_own_width(self):
        wide = validate_svg(FIXTURES / "d2-elk-example.svg")
        self.assertEqual(len(wide.errors), 1)
        self.assertIn("at 720px delivery width", wide.errors[0])
        self.assertEqual(validate_svg(FIXTURES / "d2-elk-example.svg", target_width=1027).errors, [])

    def test_direct_svg_template_is_clean_at_the_default_width(self):
        report = validate_svg(TEMPLATE, tokens_path=TOKENS)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])


if __name__ == "__main__":
    unittest.main()
