
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class ResPartner(models.Model):
    # FHIR Entity: Location (https://www.hl7.org/fhir/location.html)
    _inherit = "res.partner"

    stock_location_id = fields.Many2one(comodel_name="stock.location")

    stock_picking_type_id = fields.Many2one(comodel_name="stock.picking.type")
