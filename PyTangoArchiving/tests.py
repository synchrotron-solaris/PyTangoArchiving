import unittest

import PyTangoArchiving,traceback,time,re,fandango

class EvalReader(PyTangoArchiving.Reader):
  def get_attribute_values(self,attribute,start_date,stop_date=None,asHistoryBuffer=False,N=0):
    print 'get_attribute_values(%s)'%attribute
    is_eval = expandEvalAttribute(attribute)
    if stop_date is None: stop_date=time.time()
    if is_eval:
      getId = lambda s: s.strip('{}').replace('/','_').replace('-','_')
      attribute = attribute.replace('eval://','')
      attributes = is_eval
      for a in attributes:
       attribute = attribute.replace(a,' %s '%getId(a))
      resolution = max((1,(stop_date-start_date)/(10*1080)))
      vals = dict((k,fandango.arrays.filter_array(v,window=resolution)) for k,v in self.get_attributes_values([a.strip('{}') for a in attributes],start_date,stop_date).items())
      cvals = self.correlate_values(vals,resolution=resolution,rule=(lambda t1,t2,tt:t2))
      nvals = []
      for i,t in enumerate(cvals.values()[0]):
       try:
        vars = dict((getId(k),v[i][1]) for k,v in cvals.items())
        if None in vars.values():
         v= None
        else:
         v = eval(attribute,vars)
       except:
        traceback.print_exc()
        v = None
       nvals.append((t[0],v))
      return nvals
    else:
     return PyTangoArchiving.Reader.get_attribute_values(self,attribute,start_date,stop_date)
     
     
 #eval://{sr/di/dcct/averagecurrent}*{fe04/vc/vgct-01/state}+2

# contact_points=192.168.130.245,192.168.130.246
# user=cassandra
# password=cassandra
# keyspace=hdb
# port=9042
# libname=libhdb++cassandra.so
# local_dc=machine-hdbpp-dc1
def get_hdbpp():

     from PyTangoArchiving.hdbpp import HDBpp

     return HDBpp(backend="cassandra", db_name="hdb", host=["192.168.130.245", "192.168.130.246"], user="cassandra",
                  passwd="cassandra", port="9042")


class CassandraPyTangoArchivingTest(unittest.TestCase):

    def simply_tab_cheack(self, value_to_check):

        self.assertEqual(type(value_to_check), list)
        self.assertGreater(value_to_check.__len__(), 0)

    def test_get_all_managers(self):

        managers = get_hdbpp().get_all_managers()
        self.simply_tab_cheack(managers)
        print("Managers: %s" % managers)

    def test_get_all_archivers(self):

        archivers = get_hdbpp().get_all_archivers()
        self.simply_tab_cheack(archivers)
        print("Archivers: %s" % archivers)

    def test_get_archived_attributes(self):

        archived_attributes = get_hdbpp().get_archived_attributes()
        self.simply_tab_cheack(archived_attributes)
        print("Archive Attribute: %s" % archived_attributes)

    def test_get_attribute_names(self):

        attribute_name = get_hdbpp().get_attribute_names()
        self.simply_tab_cheack(attribute_name)
        print("Name Attribute: %s" % attribute_name)

    def test_get_attributes_IDs(self):

        attribute_ids = get_hdbpp().get_attribute_ID('alarm/rad/i_rad_pyalarm01/lastupdate')
        self.simply_tab_cheack(attribute_ids)
        print("Test one attribute ids %s" % attribute_ids)

    def test_get_attribute_values(self):
        # '2013-03-20 10:00', '2013-03-20 11:00'
        values = get_hdbpp().get_attribute_values("r1-all/dia/r1-all-dia-bim1/beamcurrent", start_date='2018-07-26 3:00',
                                                  stop_date="2018-07-26 15:00")
        self.simply_tab_cheack(values)
        print "Extract attribute: %s" % values

    def test_reader(self):

        import PyTangoArchiving as pta

        rd = pta.Reader(schema="hdbpp")
        attribute = rd.get_attributes()
        self.simply_tab_cheack(attribute)
        print "Reader extract attributes: %s" % attribute
        attribute_value = rd.get_attribute_values('r1-all/dia/r1-all-dia-bim1/beamcurrent', start_date='2018-07-26 3:00',
                                                  stop_date="2018-07-26 15:00")
        self.simply_tab_cheack(attribute_value)
        print "Reader extract attributes: %s" % attribute_value


if __name__ == '__main__':

    unittest.main()
