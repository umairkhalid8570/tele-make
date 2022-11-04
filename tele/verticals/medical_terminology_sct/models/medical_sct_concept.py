
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class MedicalSCTConcept(models.Model):
    """
    Medical SNOMED CT concept
    (https://www.hl7.org/fhir/codesystem-snomedct.html)
    It has been defined following the code system entity with the following
    information:
    - url: http://snomed.info/sct
    - identifier: urn:ietf:rfc:3986 / urn:oid:2.16.840.1.113883.6.96
    - name: SNOMED_CT
    - publisher: IHTSDO
    """

    _name = "medical.sct.concept"
    _inherit = "medical.abstract.concept.multiparent"
    _description = "Medical SCT Concept"

    parent_ids = fields.Many2many(
        comodel_name="medical.sct.concept", relation="medical_sct_concept_is_a"
    )
    child_ids = fields.Many2many(comodel_name="medical.sct.concept")
    full_parent_ids = fields.Many2many(comodel_name="medical.sct.concept")
    full_child_ids = fields.Many2many(comodel_name="medical.sct.concept")

    def check_property(self, name, codes):
        for parent in self.parent_ids:
            if parent[name] or parent.code in codes:
                return True
