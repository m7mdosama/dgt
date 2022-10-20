from odoo import models, fields, api
import logging


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _logger = logging.getLogger(__name__)

    def action_confirm(self):
        """ Function To create Gate Information When Customer Delivery is Created """
        res = super(SaleOrder, self).action_confirm()
        gatelines = self.sudo(1).env['security.gate.lines']
        gate = self.sudo(1).env['security.gate']
        if self.picking_ids:
            for rec in self.picking_ids:
                delivery_date = rec.scheduled_date
                delivery_name = rec.name
                cust_exist_ondate = gate.search(
                    [('visit_date', '=', delivery_date), ('customer_name', '=', self.partner_id.id)])
                " If Customer Exists then create Gate lines Only else Create Gate and Gate Lines"
                if cust_exist_ondate:
                    gatelines.create({
                        'name': delivery_name,
                        'gate_id': cust_exist_ondate.id,
                        'type_inter': 'deliv',

                    })
                    gate.search([('empty', '=', False)]).unlink()
                else:
                    last_id = gate.create({'customer_name': self.partner_id.id, 'visit_date': delivery_date})
                    gatelines.create({
                        'name': delivery_name,
                        'gate_id': last_id.id,
                        'type_inter': 'deliv',
                    })
                    gate.search([('empty', '=', False)]).unlink()

        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _logger = logging.getLogger(__name__)
    sec_confirm = fields.Boolean('Security Confirmation')

    def action_cancel(self):
        """ Function To delete Delivery When its Canceled"""
        res = super(StockPicking, self).action_cancel()
        gatelines = self.sudo(1).env['security.gate.lines']
        delivery_name = self.name
        self._logger.exception("---------delivery_name---- %s", delivery_name)
        gatelines.search([('name', '=', delivery_name)]).unlink()
        return res

    @api.constrains('scheduled_date')
    def _onchange_date(self):
        gatelines = self.sudo(1).env['security.gate.lines']
        gate = self.sudo(1).env['security.gate']
        if self.scheduled_date:
            delivery_date = self.scheduled_date
            delivery_name = self.name
            cust_exist_ondate = gate.search(
                [('visit_date', '=', delivery_date), ('customer_name', '=', self.partner_id.id)])
            if cust_exist_ondate:
                gatelines.search([('name', '=', delivery_name), ('type_inter', '=', 'deliv')]).write(
                    {'gate_id': cust_exist_ondate.id, })
            elif not cust_exist_ondate:
                last_id = gate.create({'customer_name': self.partner_id.id, 'visit_date': delivery_date})
                gatelines.search([('name', '=', delivery_name), ('type_inter', '=', 'deliv')]).write(
                    {'gate_id': last_id.id})
                gate.search([('empty', '=', False)]).unlink()
