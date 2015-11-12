import os
import logging
import shutil

CONF_HOSTAPD_KARMA = 'hostapd-karma.conf'

class HostAPDKarma(object):

    _instance = None
    
    def __init__(self):
        
        mana_dir = os.path.dirname(os.path.realpath(__file__))
        self.mana_dir = mana_dir
        self.conf_dir = '%s/conf' % mana_dir
        self.cert_dir = '%s/cert' % mana_dir
        self.hostapd_path = '%s/hostapd' % mana_dir

    @staticmethod
    def get_instance():
        
        if HostAPD._instance is None:
            HostAPD._instance = HostAPD()
        return HostAPD._instance

    def start(self):

        # kill existing hostapd instances
        os.system('killall hostapd')

        # spawn hostapd background process
        os.system('%s %s &' % (self.hostapd_path, self.conf))
        time.sleep(2)

    def stop(self):

        bash_command('killall hostapd')
        time.sleep(2)

    def configure_karma(self,
            phy,
            essid='Seems legit',
            bssid='00:11:22:33:44:00',
            channel=6):

        conf = '%s/%s' % (self.conf_dir, CONF_HOSTAPD_KARMA)

        # make backup of existing configuration file
        shutil.copy(conf, '%s.hostapd-mana.bak' % conf)

        with open(conf, 'w') as fd:

            fd.write('\n'.join([
                'interface=%s' % phy,
                'bssid=%s' % bssid,
                'driver=nl80211',
                'ssid=%s' % essid,
                'channel=%d' % channel,
                '# Prevent dissasociations',
                'disassoc_low_ack=0',
                'ap_max_inactivity=3000',
                '# Both open and shared auth',
                'auth_algs=3',
                '# no SSID cloaking',
                '#ignore_broadcast_ssid=0',
                '# -1 = log all messages',
                'logger_syslog=-1',
                'logger_stdout=-1',
                '# 2 = informational messages',
                'logger_syslog_level=2',
                'logger_stdout_level=2',
                'ctrl_interface=/var/run/hostapd',
                'ctrl_interface_group=0',
                '# 0 = accept unless in deny list',
                '#macaddr_acl=0',
                '# only used if you want to do filter by MAC address',
                '#accept_mac_file=/etc/hostapd/hostapd.accept',
                '#deny_mac_file=/etc/hostapd/hostapd.deny',
                '# Enable karma mode',
                'enable_karma=1',
                '# Limit karma to responding only to the device probing (0), or not (1)',
                'karma_loud=0',
                '# Black and white listing',
                '# 0 = white',
                '# 1 = black',
                '#karma_black_white=1',
            ]))

        self.conf = conf

    def restore(self):

        shutil.copy('%s.hostapd-mana.bak' % self.conf, self.conf)
