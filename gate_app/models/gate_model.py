from odoo import models, fields, api
import logging
from datetime import date
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

timezone_plus = 2


class SecurityGate(models.Model):
    _name = "security.gate"
    _description = "Security Gate"
    _rec_name = 'customer_name'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _logger = logging.getLogger(__name__)

    gate_line = fields.One2many('security.gate.lines', 'gate_id', string='Gate Lines')

    persons = fields.One2many('security.gate.persons', 'gate_line_field', string="Person Name")

    customer_name = fields.Many2one('res.partner', string="Customer Name" )

    source_invoices = fields.Many2many("security.gate.lines", string="Source Invoices", compute='_default_invoice')
    source_delivery = fields.Many2many('security.gate.lines', string='Source Delivery', compute='_default_delivery')

    type = fields.Selection([('visit', 'Visit'),
                             ('sales', 'Sales'),
                             ('maintenance', 'Maintenance'),
                             ('worker', 'New Worker'),
                             ('supplies', 'Factory supplies'),
                             ('material', 'Materials')], default='sales')

    visit_date = fields.Date(string="Date")
    today = fields.Date(string="today", default=date.today())

    in_time = fields.Float(string="IN")
    out_time = fields.Float(string="OUT")

    note = fields.Html(string='Notes', help="this field for notes")

    person_id = fields.Image(related="persons.person_id")
    license_image = fields.Image(string="License Image")

    empty = fields.Boolean(string='empty', default=False, compute='_empty_record', store=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', default='draft')

    def action_confirm(self):
        self.state = 'done'

    def now_in(self):
        dt = datetime.now()
        inT = timezone_plus + dt.hour + dt.minute / 60.0
        self.in_time = inT

    def now_out(self):
        dt = datetime.now()
        outT = timezone_plus + dt.hour + dt.minute / 60.0
        self.out_time = outT

    @api.onchange('persons')
    def person_unique(self):
        """ Function to make only person per gate lines """
        exist_person = []
        for line in self.persons:
            if line.driver_id.id in exist_person:
                raise ValidationError('Person should be one per line.')
            exist_person.append(line.driver_id.id)

    @api.constrains('persons')
    def _save_driver(self):
        """ Function To Save Driver """
        driver_info = self.persons
        # name = driver_info.driver_name    
        for per in driver_info:
            if not per.driver_id.driver_name:
                per.write({'driver_name': per.driver_name, 'car_number': per.car_number})

    @api.depends('customer_name')
    def _default_delivery(self):
        """ Function to get Source Delivery"""
        for record in self:
            gatelines = record.env['security.gate.lines'].search(
                [('gate_id', '=', record.id), ('type_inter', '=', 'deliv')])
            if gatelines:
                for lines in gatelines:
                    record.source_delivery = [(4, lines.id)]
            else:
                record.source_delivery = False

    def _default_invoice(self):
        """ Function to get Source Invoices"""
        for record in self:
            gatelines = record.env['security.gate.lines'].search(
                [('gate_id', '=', record.id), ('type_inter', '=', 'inv')])
            if gatelines:
                for lines in gatelines:
                    record.source_invoices = [(4, lines.id)]
            else:
                record.source_invoices = False

    @api.depends('gate_line')
    def _empty_record(self):
        """Function to make """
        for record in self:
            gatelines = record.env['security.gate.lines'].search([('gate_id', '=', record.id)])
            self._logger.exception("-----Gate Lines---- %s", gatelines)
            if gatelines:
                record.empty = True
            else:
                record.empty = False


class SecurityGateLine(models.Model):
    _name = "security.gate.lines"
    _description = "Security Gate Lines "
    _sql_constraints = [('name_company_uniq', 'unique(name)', 'Delivery address already exists!')]

    name = fields.Char(string='Name')
    type_inter = fields.Char('type_inter')
    sec_confirm = fields.Boolean('Security Confirmation')
    note = fields.Text(string='Notes', help="this field for notes")
    gate_id = fields.Many2one('security.gate', string="Gate Reference")


class intersType(models.Model):
    _name = "inter_model"
    _description = "inter_model"
    name = fields.Char(string="Name")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status')
    origin = fields.Char(string="origin", )
    date = fields.Date(string="date")
