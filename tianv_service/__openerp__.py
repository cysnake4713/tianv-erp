# -*- encoding: utf-8 -*-
# __author__ = cysnake4713@gmail.com
# #############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Tianv Service Module',
    'version': '0.1',
    'author': 'cysnake4713',
    'maintainer': 'odoosoft@gmail.com',
    'website': 'http://www.odoosoft.com',
    'description': u"""
Tianv Service Module
""",
    'depends': ['base_override', 'tianv_sale', 'analytic', 'sale'],
    'category': 'Service',
    'demo_xml': [],
    'data': [
        'data/uom.xml',
        'data/service_cron.xml',
        'security/base_security.xml',
        'data/product.category.csv',
        'security/ir.model.access.csv',
        #
        'views/service_menu.xml',
        'views/service_view.xml',


    ],
    'qweb': [
    ],
    'installable': True,
}