import copy
import tempfile
import unittest
from pathlib import Path

from pcim_oids import apply_oids, read_entities, render_attributes, render_requirement_table, valid_oid


class OidTests(unittest.TestCase):
    def setUp(self):
        self.root = "1.3.6.1.4.1.19376.1.6.2.7"
        self.entities = [{"type": "profile", "id": "PCIM", "oid": self.root,
                          "registryAnchor": "pcim-oid-profile", "anchor": "pcim-profile"}]
        self.req = {"id": "PCIMR0100", "anchor": "pcimr0100", "level": "shall",
                    "type": "tech_feature", "scope": {key: [] for key in
                    ("actors", "transactions", "options", "useCases")}}
        self.source = "[[pcim-profile]]\n= Profile\n"

    def test_normalizes_number_and_preserves_identity_after_section_move(self):
        a, b = copy.deepcopy(self.req), copy.deepcopy(self.req)
        apply_oids([a], self.entities, self.source)
        apply_oids([b], self.entities, "= New section\n" + self.source)
        self.assertEqual(a["oid"], self.root + ".10.100")
        self.assertEqual(a, b)
        self.assertIn(a["oid"], render_requirement_table([a]))
        self.assertIn(":pcim-oid-pcimr0100: " + a["oid"], render_attributes([a], self.entities))
        self.assertEqual(a["uri"], "urn:oid:" + a["oid"])
        self.assertEqual(a["allocationStatus"], "proposed")

    def test_duplicate_requirement_oid_fails(self):
        with self.assertRaisesRegex(ValueError, "Duplicate OID"):
            apply_oids([copy.deepcopy(self.req), copy.deepcopy(self.req)], self.entities, self.source)

    def test_entity_requirement_collision_fails(self):
        entity = {"type": "actor", "id": "collision", "oid": self.root + ".10.100",
                  "registryAnchor": "pcim-oid-collision", "anchor": "collision"}
        with self.assertRaisesRegex(ValueError, "Duplicate OID"):
            apply_oids([self.req], self.entities + [entity], self.source + "[[collision]]")

    def test_unknown_scope_and_definition_fail(self):
        self.req["scope"]["actors"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "unknown actor"):
            apply_oids([self.req], self.entities, self.source)
        with self.assertRaisesRegex(ValueError, "Unknown entity definition"):
            apply_oids([], self.entities, "")

    def test_oid_syntax(self):
        for bad in ("pending", "1.03.6", "3.1", "1.40.1", "1..2", "1.2.-1"):
            self.assertFalse(valid_oid(bad), bad)
        self.assertTrue(valid_oid(self.root))

    def test_real_registry_and_reject_unresolved_allocation(self):
        root = Path(__file__).resolve().parents[3]
        path = root / "asciidoc/pcim_oid_entities.adoc"
        entries = read_entities(path)
        self.assertEqual(len(entries), 13)
        self.assertEqual(sum(e["allocationStatus"] == "proposed" for e in entries), 9)
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "registry.adoc"
            bad.write_text(path.read_text().replace("|proposed", "|unresolved", 1))
            with self.assertRaisesRegex(ValueError, "Invalid OID registry entry"):
                read_entities(bad)


if __name__ == "__main__":
    unittest.main()
