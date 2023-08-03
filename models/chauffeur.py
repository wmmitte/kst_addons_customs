from odoo import fields,api,models,tools,_
import string
from datetime import datetime,date
import pdb,re
import calendar
from calendar import monthrange
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import html


#Faire un nouveau chauffeur
class Chauffeur(models.Model):
    _name = 'chauffeur'
    _description = "Enregistrement d'un chauffeur"

    name = fields.Char(string = 'Nom et Prénom (s)',required = True)
    adresse = fields.Text(string="Adresse", readonly=False)
    telephone = fields.Char(string = 'Téléphone',required = True)
    cnib = fields.Char(string="Réf. CNIB")
    date_naissance = fields.Date(string="Date et lieu de naissance")
    permis = fields.Char(string="N° Permis", required=True)
    photo = fields.Binary(string="Photo")
    active = fields.Boolean(string="Etat", default=True)
    company_id = fields.Many2one('res.company', string="Structure", default=lambda self: self.env.user.company_id.id,readonly=True)
