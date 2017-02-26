import os, argparse
from twisted.internet import defer
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import NetstringReceiver


class QueryNetProtocol(NetstringReceiver):
    def connectionMade(self):
        self.sendRequest(self.factory.hash_type, self.factory.hash_value)

    def sendRequest(self, hash_type, hash_value):
        self.sendString(hash_type + '.' + hash_value)

    def stringReceived(self, s):
        self.transport.loseConnection()
        self.responseReceived(s)

    def responseReceived(self, response):
        self.factory.handleResponse(response)


class QueryNetFactory(ClientFactory):
    protocol = QueryNetProtocol

    def __init__(self, hash_type, hash_value):
        self.hash_type = hash_type
        self.hash_value = hash_value
        self.deferred = defer.Deferred()

    def handleResponse(self, response):
        d, self.deferred = self.deferred, None
        d.callback(response)

    def clientConnectionLost(self, _, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)

    clientConnectionFailed = clientConnectionLost


class QueryProxy(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def query(self, hash_type, hash_value):
        factory = QueryNetFactory(hash_type, hash_value)
        from twisted.internet import reactor
        reactor.connectTCP(self.host, self.port, factory)
        return factory.deferred


def main(options):
    from twisted.internet import reactor

    host = options.host
    port = int(options.port)
    sha1 = options.sha1
    proxy = QueryProxy(host, port)

    def query_ok(response):
        print "The result of the query is : %s" % response

    def query_failed(err):
        print "Problem in query : %s" % err

    def query_done(_):
        reactor.stop()

    d = proxy.query('sha1', sha1)
    d.addCallbacks(query_ok, query_failed)
    d.addBoth(query_done)
    reactor.run()


def _showBanner():
    if os.name == "nt":
        os.system("cls")
    elif os.name == "posix":
        os.system("clear")
    print "**************************************"
    print "*   GRID DeCentralized Client v1.0   *"
    print "**************************************"


if __name__ == "__main__":
    _showBanner()
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="server host/ip")
    parser.add_argument("port", help="server port number to listen to")
    parser.add_argument("--sha1", help="sha1 value to be queried")
    options = parser.parse_args()
    main(options)
