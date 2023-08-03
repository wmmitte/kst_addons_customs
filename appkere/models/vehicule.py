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


class Localite(models.Model):
    _name = 'localite'
    _description = "Enregistrement d'une localite"

    name = fields.Char(string = 'Nom de la localité',required = True)
    description = fields.Text(string="Description")


class Service(models.Model):
    _name = 'service'
    _description = "Enregistrement d'un service"

    name = fields.Char(string = 'Nom du service',required = True)
    description = fields.Text(string="Description")


class Marque(models.Model):
    _name = 'marque'
    _description = "Enregistrement d'une marque de vehicule"

    name = fields.Char(string = 'Nom de la marque',required = True)
    description = fields.Text(string="Description")

class Assureur(models.Model):
    _name = 'assureur'
    _description = "Enregistrement d'un assureur"

    name = fields.Char(string = "Nom de l'assureur",required = True)
    description = fields.Text(string="Description")


class Vehicule(models.Model):
    _name = 'vehicule'
    _description = "Enregistrement d'un vehicule"

    marque_id = fields.Many2one("marque", string="Marque", required=True)
    chassis = fields.Char(string="N° Chassis", required=True)
    plaque = fields.Char(string="Plaque d'immatriculation", required=True)
    active = fields.Boolean(string="Etat", default=True)
    company_id = fields.Many2one('res.company', string="Structure", default=lambda self: self.env.user.company_id.id,readonly=True)
    
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s' % (rec.marque_id.name, rec.plaque)))
        return result
    
    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     if name:
    #         records = self.search(['|', ('marque_id', operator, name), ('plaque', operator, name)])
    #         return records.name_get()
    #     return self.search([('name', operator, name)] + args, limit=limit).name_get()
    