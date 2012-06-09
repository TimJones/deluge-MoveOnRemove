/*
Script: moveonremove.js
    The client-side javascript code for the MoveOnRemove plugin.

Copyright:
    (C) Tim Jones 2009 <me+deluge@prototim.com>
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, write to:
        The Free Software Foundation, Inc.,
        51 Franklin Street, Fifth Floor
        Boston, MA  02110-1301, USA.

    In addition, as a special exception, the copyright holders give
    permission to link the code of portions of this program with the OpenSSL
    library.
    You must obey the GNU General Public License in all respects for all of
    the code used other than OpenSSL. If you modify file(s) with this
    exception, you may extend this exception to your version of the file(s),
    but you are not obligated to do so. If you do not wish to do so, delete
    this exception statement from your version. If you delete this exception
    statement from all source files in the program, then also delete it here.
*/

Ext.ns('Deluge.ux');
Ext.ns('Deluge.ux.preferences');

Deluge.ux.preferences.MoveOnRemovePage = Ext.extend(Ext.Panel, {

	title: _('MoveOnRemove'),
	layout: 'fit',
	border: false,

	initComponent: function() {
		Deluge.ux.preferences.MoveOnRemovePage.superclass.initComponent.call(this);

		this.form = this.add({
			xtype: 'form',
			layout: 'form',
			border: false,
			autoHeight: true
		});

		this.moveTo = this.form.add({
			xtype: 'textfield',
			fieldLabel: _('Move to'),
			name: 'txt_move_to',
			width: 210
		});
	}
});

Deluge.plugins.MoveOnRemovePlugin = Ext.extend(Deluge.Plugin, {

	name: 'MoveOnRemove',

	onDisable: function() {
		deluge.preferences.removePage(this.prefsPage);
	},

	onEnable: function() {
		this.prefsPage = deluge.preferences.addPage(new Deluge.ux.preferences.MoveOnRemovePage());
	}
});
Deluge.registerPlugin('MoveOnRemove', Deluge.plugins.MoveOnRemovePlugin);
