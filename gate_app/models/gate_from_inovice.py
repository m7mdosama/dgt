from odoo import models, fields, api

import logging


class AccountMove(models.Model):
    _inherit = "account.move"
    _logger = logging.getLogger(__name__)

    def action_post(self):
        """ Function To create Gate Information When Customer Invoice is Created """
        res = super(AccountMove, self).action_post()
        invoice_date = self.invoice_date
        invoice_cust = self.partner_id.id
        invoice_name = self.name
        gatelines = self.sudo(1).env['security.gate.lines']
        gate = self.sudo(1).env['security.gate']

        cust_exist_ondate = gate.search([('visit_date', '=', invoice_date), ('customer_name', '=', invoice_cust)])
        " If Customer Exists then create Gate lines Only else Create Gate and Gate Lines"
        if cust_exist_ondate:
            find_gatelines = gatelines.search([('name', '=', invoice_name), ('type_inter', '=', 'inv')])
            if find_gatelines:
                gatelines.search([('name', '=', invoice_name), ('type_inter', '=', 'inv')]).write(
                    {'gate_id': cust_exist_ondate.id, })
            else:
                gatelines.create({'name': invoice_name, 'gate_id': cust_exist_ondate.id, 'type_inter': 'inv', })
            gate.search([('empty', '=', False)]).unlink()

        elif not cust_exist_ondate:
            find_gatelines = gatelines.search([('name', '=', invoice_name), ('type_inter', '=', 'inv')])

            last_id = gate.create({'customer_name': self.partner_id.id, 'visit_date': invoice_date})
            self._logger.exception("---------last_id---- %s", dir(last_id))

            if find_gatelines:
                gatelines.search([('name', '=', invoice_name), ('type_inter', '=', 'inv')]).write(
                    {'gate_id': last_id.id, })
            else:
                gatelines.create({'name': invoice_name, 'gate_id': last_id.id, 'type_inter': 'inv', })
            gate.search([('empty', '=', False)]).unlink()
        return res

    def button_draft(self):
        """ Function To create Gate Information When Customer Invoice is Created """
        res = super(AccountMove, self).button_draft()
        gatelines = self.sudo(1).env['security.gate.lines']
        gate = self.sudo(1).env['security.gate']

        invoice_name = self.name
        self._logger.exception("------------------==========------------------confirmation---- %s", invoice_name)
        gatelines.search([('name', '=', invoice_name)]).unlink()
        gate.search([('empty', '=', False)]).unlink()
        return res
