#
# core.py
#
# Copyright (C) 2009 Tim Jones <me+deluge@prototim.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

import os
import shutil
import thread

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export

DEFAULT_PREFS = {
    "move_to": deluge.common.get_default_download_dir()
}

class Core(CorePluginBase):
    def enable(self):
        self.torrents_to_move = {}
        self.config = deluge.configmanager.ConfigManager("moveonremove.conf", DEFAULT_PREFS)
        component.get("EventManager").register_event_handler("PreTorrentRemovedEvent", self.on_pre_torrent_removed)
        component.get("EventManager").register_event_handler("TorrentRemovedEvent", self.on_torrent_removed)

    def disable(self):
        self.torrents_to_move.clear()
        component.get("EventManager").deregister_event_handler("PreTorrentRemovedEvent", self.on_pre_torrent_removed)
        component.get("EventManager").deregister_event_handler("TorrentRemovedEvent", self.on_torrent_removed)

    def update(self):
        pass

    def on_pre_torrent_removed(self, torrent_id):
        """Grab all the torrent information needed to delete later"""
        log.debug("MoveOnRemove: PreTorrentRemove " + torrent_id)

        info_keys = ["save_path", "move_on_completed", "move_on_completed_path", "name"]

        if not torrent_id in component.get("TorrentManager").torrents:
            log.error("MoveOnRemove: Cannot retrive torrent details")
            return

        info = component.get("TorrentManager").torrents[torrent_id].get_status(info_keys)
        store = { "path" : info["move_on_completed_path"] if info["move_on_completed"] else info["save_path"] }
        store["name"] = info["name"]

        """Get a list of files in the torrent, add the base directory(ies)"""
        store["files"] = []
        files = component.get("TorrentManager").torrents[torrent_id].get_files()
        for f in files:
            (head, tail) = os.path.split( f["path"])
            while head:
                (head, tail) = os.path.split(head)
            if not tail in store["files"]:
                store["files"].append(tail)

        self.torrents_to_move[torrent_id] = store

    def on_torrent_removed(self, torrent_id):
        """Verify settings before doing anything"""
        log.debug("MoveOnRemove: TorrentRemoved " + torrent_id)
        move_to_path = self.config["move_to"]

        if move_to_path == "":
            log.error("MoveOnRemove: No path specified. Move aborted")
            return

        if not os.path.isdir( move_to_path ):
            log.error("MoveOnRemove: Path '" + move_to_path + "' is invalid. Move aborted")
            return

        if not torrent_id in self.torrents_to_move:
            log.error("MoveOnRemove: Torrent '" + torrent_id + "' info not found. Move aborted")
            return

        info = self.torrents_to_move[torrent_id]

        if not os.path.exists( info["path"] ):
            log.error("MoveOnRemove: Cannot find '" + info["path"] + "'. Move aborted")
            return

        log.debug("MoveOnRemove: Moving '" + info["name"] + "' from '" + info["path"] + "' to '" + move_to_path + "'")
        thread.start_new_thread(Core._thread_move, (info["path"], move_to_path, info["files"]))

    @staticmethod
    def _thread_move( path, new_path, files ):
        for file in files:
            old_file_path = os.path.join(path, file)
            new_file_path = os.path.join(new_path, file)
            log.error("MoveOnRemove: '" + old_file_path + "' to '" + new_file_path + "'")

            if not os.path.exists(old_file_path):
                log.error("MoveOnRemove: Cannot find '" + old_file_path + "'. Skipping")
                continue

            if os.path.exists(new_file_path):
                log.error("MoveOnRemove: File '" + new_file_path + "' already exists. Skipping")
                continue

            try:
                if not os.path.exists(os.path.dirname(new_file_path)):
                    os.makedirs(os.path.dirname(new_file_path))
            except Exception, e:
                log.error("MoveOnRemove: Could not create path for '" + new_file_path + "' because " + str(e) + ". Skipping")
                continue

            try:
                shutil.move(old_file_path, new_file_path)
            except Exception, e:
                log.error("MoveOnRemove: Could not move '" + new_file_path + "' because " + str(e) + ". Skipping")
                continue

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config
