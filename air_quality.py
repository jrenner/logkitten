__author__ = 'Jon Renner'
__email__ = 'rennerjc@gmail.com'

# Air quality SOAP Client for Taiwan

import SOAPpy

#url = 'http://taqm.epa.gov.tw/taqm'
try:
    url = 'http://taqm.epa.gov.tw/taqm/DataService.asmx'
    namespace = 'http://taqm.epa.gov.tw/taqm'
    server = SOAPpy.SOAPProxy(url, namespace)
    args = {'returnDataType':'csv'}
    action = 'http://taqm.epa.gov.tw/taqm/SiteList'
    x = server.SiteList(returnDataType="csv")
    print x
except SOAPpy.Types.faultType, e:
    print "FAULT"
    print e.__repr__()
print "FINISHED"
#server.CurrentHourlyPSI_OneSite('csv', 1)