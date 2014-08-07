# -*- encoding: utf-8 -*-
# __author__ = cysnake4713@gmail.com
# #############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Tianv Sales Module',
    'version': '0.1',
    'author': 'cysnake4713',
    'maintainer': 'cysnake4713@gmail.com',
    'website': 'http://www.odoosoft.com',
    'description': u"""
Tianv Sales Module
""",
    'depends': ['base_override', 'mail'],
    'category': 'Sales',
    'demo_xml': [],
    'data': [
        'security/base_security.xml',
        'security/ir.model.access.csv',

        'views/partner_view.xml',
        'views/partner_menu.xml',

    ],
    'qweb': [
    ],
    'installable': True,
}