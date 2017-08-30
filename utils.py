from ipaddress import ip_address

class PrivateIPs(object):
    def __contains__(self, address):
        ip = ip_address(unicode(address))
        return ip.is_private
