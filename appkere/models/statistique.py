from odoo import fields,api,models,tools,_
import string
from datetime import datetime,date
import pdb,re
import calendar
from calendar import monthrange
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import html
from num2words import num2words


class Analyse(models.Model):
    _name = "analyse"

    date_debut = fields.Date("Date de début", required=True)
    date_fin = fields.Date("Date de fin", required=True)
    vehicule_id = fields.Many2one("vehicule", "Camion", required=True)
    depense = fields.Float("Total dépense", readonly=True)
    recette = fields.Float("Total recette", readonly=True)
    benefice = fields.Float("Bénéfice", compute='_calcul_benefice')
    analyse_ids = fields.One2many("analyse.line","analyse_id", readonly=True)

    @api.constrains('date_debut', 'date_fin')
    def _check_date(self):
        if self.date_debut > self.date_fin:
            raise ValidationError(_("Le date de début ne doit pas être supérieure à la date de fin."))
        else:
            print("Ok")
    
    def afficher(self):
        for va in self:
            va.analyse_ids.unlink()
            lines = va.env['depense'].search([('vehicule_id.id', '=', self.vehicule_id.id)])
            for li in lines:
                self.sudo().env['analyse.line'].create({
                    'date': li.date,
                    'service_id': li.service.id,
                    'montant': li.montant,
                    'analyse_id': self.id
                })
        

        mnt = self.env['assurance'].search([('date_deb', '>=', self.date_debut), ('date_fin', '<=', self.date_fin), ('state', '=', 'V')])
        mnt_mois = mnt.montant_mois
        camion = int(self.vehicule_id.id)
        depenses = self.env['depense'].search(
            [('vehicule_id.id', '=', camion), ('date', '>=', self.date_debut),
            ('date', '<=', self.date_fin), ('state', '=', 'V')])
        montant_depense = 0
        for d in depenses:
            montant_depense = montant_depense + d.montant
            self.depense = montant_depense + mnt_mois
        
        recettes = self.env['recette'].search(
            [('vehicule_id.id', '=', camion), ('date', '>=', self.date_debut),
            ('date', '<=', self.date_fin), ('state', '=', 'V')])
        montant_recette = 0
        for r in recettes:
            montant_recette = montant_recette + r.montant
            self.recette = montant_recette
            
    def _calcul_benefice(self):
        for vals in self:
            vals.benefice = vals.recette - vals.depense


class AnalyseLine(models.Model):
    _name = "analyse.line"

    analyse_id = fields.Many2one("analyse", "Analyse", ondelete='cascade')
    date = fields.Date("Date")
    service_id = fields.Many2one("service", "Nature dépense")
    montant = fields.Float("Montant dépense")