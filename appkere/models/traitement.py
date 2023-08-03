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


#Faire un nouveau chauffeur
class Voyage(models.Model):
    _name = 'voyage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Enregistrement d'un voyage"

    name = fields.Char(string = 'N° Voyage',readonly = False)
    chauffeur_id = fields.Many2one("chauffeur",string = 'Chauffeur',required = True)
    localite_id = fields.Many2one("localite", string="Destination", required=True)
    vehicule_id = fields.Many2one("vehicule", string = 'Camion',required = True)
    date_depart = fields.Date(string="Date de départ", required=True)
    date_retour = fields.Date(string="Date de retour")
    montant = fields.Float(string="Frais de route", required=False)
    objet = fields.Text(string="Objet", required=True)
    observation = fields.Text(string="Observation", required=False)
    state = fields.Selection([('N', 'Nouveau'), ('E', 'En voyage'), ('R', 'De retour')], default='N', string="Etat")
    company_id = fields.Many2one('res.company', string="Structure", default=lambda self: self.env.user.company_id.id,readonly=True)

    
    def act_valider_voyage(self):
        annee = date.today()
        val_annee = annee.year
        for val in self:
            resultat = self.sudo().env['compteur.voyage'].search([('annee', '=', val_annee)])
            numero = 1
            if resultat:
                numero = resultat.nombre + 1
                resultat.nombre = numero
                numero = str(numero).zfill(3)
            else:
                self.env['compteur.voyage'].create({
                    'nombre': 1, 'annee': val_annee})
                numero = str(numero).zfill(3)
            val.name = str(val_annee) + "/" + str(numero)
            self.write({'state': 'E'})
        return self.create_rainbow_man("Voyage validé avec succès !")


    def create_rainbow_man(self, message):
        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'type': 'rainbow_man'
            }
        }
    
    def act_cloturer_voyage(self):
        self.write({'state': 'R'})


class CompteurVoyage(models.Model):
    _name = "compteur.voyage"

    annee = fields.Integer()
    nombre = fields.Integer()


class Depense(models.Model):
    _name = "depense"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Enregistrement d'une dépense"
    _rec_name = "vehicule_id"

    vehicule_id = fields.Many2one("vehicule", string="Camion", required=True)
    date = fields.Date("Date dépense", required=True)
    montant = fields.Float("Montant dépense", required=True)
    service = fields.Many2one("service", string="Nature dépense", required=True)
    state = fields.Selection([('N', 'Nouvelle'), ('V', 'Validée'), ('A', 'Annulée')], default='N', string="Etat")
    observation = fields.Text(string="Observation", required=False)

    @api.constrains('montant')
    def _check_montant(self):
        if self.montant <= 0:
            raise ValidationError(_("Le montant de la dépense doit être supérieur à zéro (0)."))
        else:
            print("Ok")
    
    def act_valider_depense(self):
        for val in self:
            val.write({'state': 'V'})
        return self.create_rainbow_man("Dépense enregistrée avec succès !")
    
    def create_rainbow_man(self, message):
        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'type': 'rainbow_man'
            }
        }
    
    def act_annuler_depense(self):
        for val in self:
            val.write({'state': 'A'})


class Recette(models.Model):
    _name = "recette"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Enregistrement d'une recette"

    vehicule_id = fields.Many2one("vehicule", string="Camion", required=True)
    date = fields.Date("Date de la recette", required=True)
    montant = fields.Float("Montant recette", required=True)
    objet = fields.Text(string="Objet recette", required=True)
    state = fields.Selection([('N', 'Nouvelle'), ('V', 'Validée'), ('A', 'Annulée')], default='N', string="Etat")
    observation = fields.Text(string="Observation", required=False)

    @api.constrains('montant')
    def _check_montant(self):
        if self.montant <= 0:
            raise ValidationError(_("Le montant de la recette doit être supérieur à zéro (0)."))
        else:
            print("Ok")

    def act_valider_recette(self):
        for val in self:
            val.write({'state': 'V'})
        return self.create_rainbow_man("Recette enregistrée avec succès !")
    
    def create_rainbow_man(self, message):
        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'type': 'rainbow_man'
            }
        }
    
    def act_annuler_recette(self):
        for val in self:
            val.write({'state': 'A'})


class Assurance(models.Model):
    _name = 'assurance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Enregistrement d'une assurance"

    vehicule_id = fields.Many2one("vehicule", string="Camion", required=True)
    date_deb = fields.Date("Date début", required=True)
    date_fin = fields.Date("Date expiration", required=True)
    montant = fields.Float("Montant assurance", required=True)
    montant_mois = fields.Float("Montant Mois", compute="_calcul_mois")
    assureur_id = fields.Many2one("assureur",string="Assureur", required=True)
    mois = fields.Integer("Nombre de mois", required=True, default=12)
    state = fields.Selection([('N', 'Nouvelle'), ('V', 'Validée')], default='N', string="Etat")
    assurance_ids = fields.One2many("assurance.line", "assurance_id", string="Observation", required=False)

    def act_valider_assurance(self):
        for val in self:
            val.write({'state': 'V'})
        return self.create_rainbow_man("Assurance enregistrée avec succès !")
    
    def create_rainbow_man(self, message):
        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'type': 'rainbow_man'
            }
        }
    
    @api.depends('montant', 'mois')
    def _calcul_mois(self):
        for x in self:
            x.montant_mois = round(x.montant / x.mois)

    
class AssuranceLine(models.Model):
    _name = 'assurance.line'

    assurance_id = fields.Many2one("assurance", string="Assurance")
    date_deb = fields.Date("Date début", required=True)
    date_fin = fields.Date("Date fin", required=True)
    montant = fields.Float("Montant", required=True)


# class VisiteTechnique(models.Model):
#     _name = 'visite.technique'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = "Enregistrement d'une visite technique"

#     vehicule_id = fields.Many2one("vehicule", string="Camion", required=True)
#     date_deb = fields.Date("Date début", required=True)
#     date_fin = fields.Date("Date expiration", required=True)
#     montant = fields.Float("Montant visite", required=True)
#     mois = fields.Integer("Nombre de mois", required=True, default=12)
#     state = fields.Selection([('N', 'Nouvelle'), ('V', 'Validée')], default='N', string="Etat")
#     assurance_ids = fields.One2many("assurance.line", "assurance_id", string="Observation", required=False)
