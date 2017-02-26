import os, sys, argparse
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import NetstringReceiver


class GridQueryService(object):
    def query(self, hash_type, hash_value):
        print "this is the query service. Type is %s and value is %s" % (hash_type, hash_value)
        return '{"query_result":"%s"}' % hash_value

class GridQueryProtocol(NetstringReceiver):
    def stringReceived(self, request):
        print >>sys.stderr, request
        if '.' not in request: 
            self.transport.loseConnection() 
            return
        hash_type, hash_value = request.split('.')
        self.formRequestReceived(hash_type, hash_value)
        
    def formRequestReceived(self, hash_type, hash_value):
        found_flag = self.factory.query(hash_type, hash_value)
        if found_flag: self.sendString(str(found_flag))
        self.transport.loseConnection()

class GridQueryFactory(ServerFactory):
    protocol = GridQueryProtocol

    def __init__(self, service):
        self.service = service

    def query(self, hash_type, hash_value):
        return self.service.query(hash_type, hash_value)

def main(options):
    grid_query_service = GridQueryService()
    grid_query_factory = GridQueryFactory(grid_query_service)
    from twisted.internet import reactor
    port = reactor.listenTCP(int(options.port), grid_query_factory, interface=options.host)
    print "Serving GRID query service on %s" % str(port.getHost())
    reactor.run()

def _showBanner():
    if os.name == "nt": os.system("cls")
    elif os.name == "posix": os.system("clear")
    print "**************************************"
    print "*   GRID DeCentralized Server v1.0   *"
    print "**************************************" 

if __name__ == "__main__":
    _showBanner()
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="server host/ip")
    parser.add_argument("port", help="server port number to listen to")
    options = parser.parse_args()
    main(options)

