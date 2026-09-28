from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR = Path(__file__).with_name("validate_drawio_layout.py")
TEMPLATE = """\
<mxfile>
  <diagram name="Page-1">
    <mxGraphModel adaptiveColors="auto">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="a" value="A" style="rounded=1;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="200" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="mid" value="Obstacle" style="rounded=1;html=1;" vertex="1" parent="1">
          <mxGeometry x="300" y="200" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="b" value="B" style="rounded=1;html=1;" vertex="1" parent="1">
          <mxGeometry x="560" y="200" width="120" height="60" as="geometry" />
        </mxCell>
{edges}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


def run_validator(edges: str) -> subprocess.CompletedProcess[str]:
    xml = TEMPLATE.format(edges=edges)
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "fixture.drawio"
        path.write_text(xml, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            check=False,
            capture_output=True,
            text=True,
        )


class ValidateDrawioLayoutEdgeTest(unittest.TestCase):
    def test_dangling_edge_fails(self) -> None:
        edge = """\
        <mxCell id="e1" style="html=1;" edge="1" parent="1" source="a">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
"""
        result = run_validator(edge)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no target and no explicit targetPoint", result.stderr)

    def test_unknown_terminal_fails(self) -> None:
        edge = """\
        <mxCell id="e1" style="html=1;" edge="1" parent="1" source="missing" target="b">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
"""
        result = run_validator(edge)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("references unknown source missing", result.stderr)

    def test_object_wrapped_terminals_are_audited(self) -> None:
        edges = """\
        <object id="wrapped-a" label="A">
          <mxCell style="rounded=1;html=1;" vertex="1" parent="1">
            <mxGeometry x="40" y="400" width="120" height="60" as="geometry" />
          </mxCell>
        </object>
        <object id="wrapped-obstacle" label="Obstacle">
          <mxCell style="rounded=1;html=1;" vertex="1" parent="1">
            <mxGeometry x="300" y="400" width="120" height="60" as="geometry" />
          </mxCell>
        </object>
        <UserObject id="wrapped-b" label="B">
          <mxCell style="rounded=1;html=1;" vertex="1" parent="1">
            <mxGeometry x="560" y="400" width="120" height="60" as="geometry" />
          </mxCell>
        </UserObject>
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" parent="1" source="wrapped-a" target="wrapped-b">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
"""
        result = run_validator(edges)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("likely crosses component(s) wrapped-obstacle", result.stderr)

    def test_edge_to_inner_id_of_wrapped_cell_fails(self) -> None:
        # draw.io takes a wrapped cell's id from its <object>; an inner mxCell id is not addressable.
        edges = """\
        <object id="wrapped-c" label="C">
          <mxCell id="inner-c" style="rounded=1;html=1;" vertex="1" parent="1">
            <mxGeometry x="40" y="400" width="120" height="60" as="geometry" />
          </mxCell>
        </object>
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" parent="1" source="inner-c" target="b">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
"""
        result = run_validator(edges)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("edge e1 references unknown source inner-c", result.stderr)

    def test_container_and_child_corner_recipes_are_not_compared(self) -> None:
        shapes = """\
        <mxCell id="panel" value="Panel" style="rounded=1;absoluteArcSize=1;arcSize=12;container=1;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="400" width="640" height="200" as="geometry" />
        </mxCell>
        <mxCell id="card" value="Card" style="rounded=1;arcSize=18;html=1;" vertex="1" parent="panel">
          <mxGeometry x="20" y="40" width="160" height="80" as="geometry" />
        </mxCell>
"""
        result = run_validator(shapes)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("inconsistent rounded-rectangle", result.stderr)

    def test_figure_radius_scale_peers_are_consistent(self) -> None:
        shapes = """\
        <mxCell id="layer2" parent="0" />
        <mxCell id="chip" value="bf16" style="rounded=1;absoluteArcSize=1;arcSize=8;html=1;" vertex="1" parent="layer2">
          <mxGeometry x="40" y="400" width="60" height="24" as="geometry" />
        </mxCell>
        <mxCell id="one-line" value="router" style="rounded=1;absoluteArcSize=1;arcSize=12;html=1;" vertex="1" parent="layer2">
          <mxGeometry x="140" y="400" width="120" height="36" as="geometry" />
        </mxCell>
        <mxCell id="two-line" value="planner" style="rounded=1;absoluteArcSize=1;arcSize=16;html=1;" vertex="1" parent="layer2">
          <mxGeometry x="300" y="400" width="120" height="52" as="geometry" />
        </mxCell>
"""
        result = run_validator(shapes)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("figure-radius-scale", result.stderr)
        self.assertNotIn("rounded:absolute", result.stderr)

    def test_off_scale_radius_among_figure_scale_peers_warns(self) -> None:
        shapes = """\
        <mxCell id="layer2" parent="0" />
        <mxCell id="pill" value="pill" style="rounded=1;absoluteArcSize=1;arcSize=24;html=1;" vertex="1" parent="layer2">
          <mxGeometry x="40" y="400" width="120" height="36" as="geometry" />
        </mxCell>
        <mxCell id="node" value="node" style="rounded=1;absoluteArcSize=1;arcSize=12;html=1;" vertex="1" parent="layer2">
          <mxGeometry x="200" y="400" width="120" height="36" as="geometry" />
        </mxCell>
"""
        result = run_validator(shapes)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rounded:absolute:24", result.stderr)

    def test_ellipse_peer_is_exempt_from_corner_consistency(self) -> None:
        shapes = """\
        <mxCell id="chip" value="" style="ellipse;html=1;fillColor=#FFFFFF;" vertex="1" parent="1">
          <mxGeometry x="40" y="100" width="12" height="12" as="geometry" />
        </mxCell>
"""
        result = run_validator(shapes)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("inconsistent rounded-rectangle", result.stderr)

    def test_edge_through_obstacle_warns(self) -> None:
        edge = """\
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" parent="1" source="a" target="b">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
"""
        result = run_validator(edge)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("likely crosses component(s) mid", result.stderr)

    def test_edge_routed_around_obstacle_is_clean(self) -> None:
        edge = """\
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;exitX=0.5;exitY=0;entryX=0.5;entryY=0;" edge="1" parent="1" source="a" target="b">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="100" y="140" />
              <mxPoint x="620" y="140" />
            </Array>
          </mxGeometry>
        </mxCell>
"""
        result = run_validator(edge)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("likely crosses", result.stderr)

    def test_wrong_side_port_warns(self) -> None:
        edge = """\
        <mxCell id="e1" style="html=1;exitX=0;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="a" target="b">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
"""
        result = run_validator(edge)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("exits the left side but the other terminal is to the right", result.stderr)

    def test_floating_edge_pair_warns(self) -> None:
        edges = """\
        <mxCell id="e1" style="html=1;" edge="1" parent="1" source="mid" target="b">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e2" style="html=1;" edge="1" parent="1" source="b" target="mid">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
"""
        result = run_validator(edges)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("are all floating; they will overlap", result.stderr)

    def test_fixed_ports_on_pair_is_clean(self) -> None:
        edges = """\
        <mxCell id="e1" style="html=1;exitX=1;exitY=0.25;entryX=0;entryY=0.25;" edge="1" parent="1" source="mid" target="b">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e2" style="html=1;exitX=0;exitY=0.75;entryX=1;entryY=0.75;" edge="1" parent="1" source="b" target="mid">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
"""
        result = run_validator(edges)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("are all floating", result.stderr)

    def test_edge_label_without_opaque_background_warns(self) -> None:
        edge = """\
        <mxCell id="e1" value="review" style="edgeStyle=orthogonalEdgeStyle;html=1;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="mid" target="b">
          <mxGeometry x="0" y="0" relative="1" as="geometry">
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
"""
        result = run_validator(edge)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("label has no opaque background", result.stderr)

    def test_edge_label_with_opaque_background_is_clean(self) -> None:
        edge = """\
        <mxCell id="e1" value="review" style="edgeStyle=orthogonalEdgeStyle;html=1;labelBackgroundColor=#FFFFFF;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="mid" target="b">
          <mxGeometry x="0" y="-10" relative="1" as="geometry">
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
"""
        result = run_validator(edge)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("label has no opaque background", result.stderr)

    def test_edge_label_with_transparent_background_warns(self) -> None:
        for background in ("none", "transparent"):
            with self.subTest(background=background):
                edge = f"""\
        <mxCell id="e1" value="review" style="edgeStyle=orthogonalEdgeStyle;html=1;labelBackgroundColor={background};exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="mid" target="b">
          <mxGeometry x="0" y="-10" relative="1" as="geometry">
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
"""
                result = run_validator(edge)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("label has no opaque background", result.stderr)

    def test_unnecessary_dogleg_between_aligned_terminals_warns(self) -> None:
        shapes_and_edge = """\
        <mxCell id="below" value="Below" style="rounded=1;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="500" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="a" target="below">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="140" y="300" />
              <mxPoint x="140" y="460" />
            </Array>
          </mxGeometry>
        </mxCell>
"""
        result = run_validator(shapes_and_edge)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("adds a dogleg although its terminals align", result.stderr)

    def test_dogleg_around_blocking_component_is_clean(self) -> None:
        shapes_and_edge = """\
        <mxCell id="blocker" value="Blocker" style="rounded=1;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="330" width="120" height="80" as="geometry" />
        </mxCell>
        <mxCell id="below" value="Below" style="rounded=1;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="500" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="a" target="below">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="200" y="300" />
              <mxPoint x="200" y="460" />
            </Array>
          </mxGeometry>
        </mxCell>
"""
        result = run_validator(shapes_and_edge)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("adds a dogleg although its terminals align", result.stderr)


if __name__ == "__main__":
    unittest.main()
