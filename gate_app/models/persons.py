from odoo import models, fields, api


class persons(models.Model):
    _name = "security.gate.persons"
    _description = "Persons"
    _rec_name = 'driver_name'
    driver_name = fields.Char(string="Driver Name", required=True)
    driver_id = fields.Many2one('security.gate.persons.line', string="National ID", size=14, required=True)
    car_number = fields.Char(string="Car Number")
    person_id = fields.Image(string=" ID Image")
    person_down = fields.Image(string="Download", related='person_id')

    gate_line_field = fields.Many2one('security.gate', string="Gate Line Field")

    @api.onchange('driver_id')
    def _onchange_driver(self):
        driver_info = self.driver_id
        name = driver_info.driver_name
        car_number = driver_info.car_number
        person_id = driver_info.person_id
        if name:
            self.driver_name = name
            self.car_number = car_number
            self.person_id = person_id

    @api.constrains('driver_name')
    def _save_driver(self):
        driver_info = self.driver_id
        # name = driver_info.driver_name    
        for pers in self:
            for per in driver_info:
                if not per.driver_name:
                    per.write({'driver_name': pers.driver_name,
                               'car_number': pers.car_number,
                               'person_id': pers.person_id})


class personsLine(models.Model):
    _name = "security.gate.persons.line"
    _description = "Persons Lines"
    _rec_name = 'driver_id'
    _sql_constraints = [('name_drive_id_unique', 'unique(driver_id)', 'Person already exists!')]

    driver_name = fields.Char(string="Driver Name", required=True)
    driver_id = fields.Char(string="Driver Id", format='none', size=14, required=True)
    person_id = fields.Image(string=" ID Image  ")
    person_down = fields.Image(string="Download", related='person_id')
    car_number = fields.Char(string="Car Number")
