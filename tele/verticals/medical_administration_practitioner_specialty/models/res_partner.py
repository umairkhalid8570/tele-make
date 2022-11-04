# Copyright 2017 LasLabs Inc.

# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class ResPartner(models.Model):
    # FHIR Entity: PractitionerRole
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _inherit = "res.partner"

    specialty_ids = fields.Many2many("medical.specialty", string="Specialties")
