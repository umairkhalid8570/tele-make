# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import api, fields, models


class RecognitionBadge(models.Model):
    _inherit = 'recognition.badge'

    survey_ids = fields.One2many('survey.survey', 'certification_badge_id', 'Survey Ids')
    survey_id = fields.Many2one('survey.survey', 'Survey', compute='_compute_survey_id', store=True)

    @api.depends('survey_ids.certification_badge_id')
    def _compute_survey_id(self):
        for badge in self:
            badge.survey_id = badge.survey_ids[0] if badge.survey_ids else None
