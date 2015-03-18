#! /usr/bin/env python
# ______________________________________________________________________
'''Refence code for common tasks I do on EC2 with boto...
'''
# ______________________________________________________________________

import time, datetime, pprint
import boto

import decimal, collections
import urllib2, json

# ______________________________________________________________________

PRIMARY_ZONE = u'us-east-1'

UBUNTU_RELEASE = 'prec'

EC2InstanceDataType = collections.namedtuple(
    'EC2InstanceDataType', ['instance_type', 'name', 'memory', 'cus',
                            'cores', 'storage', 'io', 'max_ips', 'linux_cost',
                            'windows_cost'])

d = decimal.Decimal

VERY_LOW = -1
LOW = 0
MODERATE = 1
HIGH = 2
VERY_HIGH = 3

network_performance_map = {
    u'Very Low' : VERY_LOW,
    u'Low' : LOW,
    u'Moderate' : MODERATE,
    u'High' : HIGH,
    u'10 Gigabit' : VERY_HIGH
}

# From http://www.ec2instances.info/
JSON_SRC = 'https://raw.githubusercontent.com/powdahound/ec2instances.info/master/www/instances.json'

# Cut and paste of AWS EC2 Linux instance prices on us-east-1 (2014.06.28):
us_east_linux_prices_str = '''
m3.medium	1	3	3.75	1 x 4 SSD	$0.070 per Hour
m3.large	2	6.5	7.5	1 x 32 SSD	$0.140 per Hour
m3.xlarge	4	13	15	2 x 40 SSD	$0.280 per Hour
m3.2xlarge	8	26	30	2 x 80 SSD	$0.560 per Hour
c3.large	2	7	3.75	2 x 16 SSD	$0.105 per Hour
c3.xlarge	4	14	7.5	2 x 40 SSD	$0.210 per Hour
c3.2xlarge	8	28	15	2 x 80 SSD	$0.420 per Hour
c3.4xlarge	16	55	30	2 x 160 SSD	$0.840 per Hour
c3.8xlarge	32	108	60	2 x 320 SSD	$1.680 per Hour
g2.2xlarge	8	26	15	60 SSD	$0.650 per Hour
r3.large	2	6.5	15	1 x 32 SSD	$0.175 per Hour
r3.xlarge	4	13	30.5	1 x 80 SSD	$0.350 per Hour
r3.2xlarge	8	26	61	1 x 160 SSD	$0.700 per Hour
r3.4xlarge	16	52	122	1 x 320 SSD	$1.400 per Hour
r3.8xlarge	32	104	244	2 x 320 SSD	$2.800 per Hour
i2.xlarge	4	14	30.5	1 x 800 SSD	$0.853 per Hour
i2.2xlarge	8	27	61	2 x 800 SSD	$1.705 per Hour
i2.4xlarge	16	53	122	4 x 800 SSD	$3.410 per Hour
i2.8xlarge	32	104	244	8 x 800 SSD	$6.820 per Hour
hs1.8xlarge	16	35	117	24 x 2048	$4.600 per Hour
t1.micro	1	Variable	0.615	EBS Only	$0.020 per Hour
m1.small	1	1	1.7	1 x 160	$0.044 per Hour
'''
us_east_linux_prices_list = [
    instance_ln.split("\t")
    for instance_ln in us_east_linux_prices_str.split("\n")
    if len(instance_ln) > 0]
us_east_linux_prices = dict(
    (unicode(instance_data[0]), d(instance_data[-1].split()[0][1:]))
    for instance_data in us_east_linux_prices_list)
ec2_data_json = urllib2.urlopen(JSON_SRC).read()
ec2_data = json.loads(ec2_data_json)

def ec2_data_to_ec2_instance_data_type(vm):
    ECU = vm[u'ECU']
    family = vm[u'family']
    instance_type = vm[u'instance_type']
    memory = vm[u'memory']
    network_performance = vm[u'network_performance']
    pricing = vm[u'pricing'][PRIMARY_ZONE]
    storage = vm[u'storage']
    vCPU = vm[u'vCPU']
    vpc = vm[u'vpc']
    if PRIMARY_ZONE == u'us-east-1' and instance_type in us_east_linux_prices:
        linux_price = us_east_linux_prices[instance_type]
    else:
        linux_price = d(pricing[u'linux'])
    return EC2InstanceDataType(
        instance_type,
        "%s: %s" % (str(family), str(instance_type)),
        memory,
        0 if not ECU else ECU,
        vCPU,
        # Elides a bit of information, but whatevs...
        0 if not storage else storage[u'devices'] * storage[u'size'],
        network_performance_map.get(network_performance),
        vpc[u'ips_per_eni'],
        linux_price,
        d(pricing[u'mswin']))

instance_data = set([ec2_data_to_ec2_instance_data_type(vm)
                     for vm in ec2_data])

spot_instance_max_price_map = dict(
    (inst.instance_type, str(inst.linux_cost - d('0.001')))
    for inst in instance_data)

dur = lambda x: pprint.pprint([xx for xx in dir(x) if not xx.startswith('__')])
ddur = lambda x: pprint.pprint(
    None if not hasattr(x, '__dict__') else
    dict((item[0], item[1])
         for item in x.__dict__.items() if not item[0].startswith('__')))

ec2 = boto.connect_ec2()

# ______________________________________________________________________

ubuntu_aws_id = '099720109477'
ubuntu_ebs_images = ec2.get_all_images(
    owners=[ubuntu_aws_id],
    filters={
        'architecture' : 'x86_64',
        'image-type'   : 'machine',
        'name'         : '*images/*%s*%04d????' % (
            UBUNTU_RELEASE,
            datetime.datetime.now().year,),
        })
ubuntu_ebs_image_map = dict((image.name, image) for image in ubuntu_ebs_images)

most_recent_ubuntu_image = (
    ubuntu_ebs_image_map[max(ubuntu_ebs_image_map)]
    if ubuntu_ebs_image_map else None)

# ______________________________________________________________________

def get_spot_instance(**kws):
    request = ec2.request_spot_instances(**kws)[0]
    while request.state == u'open':
        time.sleep(5)
        request = ec2.get_all_spot_instance_requests([request.id])[0]
        print time.ctime(), request.id, request.state, request.status
    res = ec2.get_all_instances([request.instance_id])[0]
    instance = res.instances[0]
    print instance.public_dns_name
    instance.add_tag('Name', 'Spot (%s)' % time.ctime())
    instance.update()
    return instance

# ______________________________________________________________________

def get_resized_ubuntu_spot_instance(new_size, **kws):
    return get_resized_spot_instance(most_recent_ubuntu_image, new_size, **kws)

# ______________________________________________________________________

def get_resized_spot_instance(image, new_size, **kws):
    import copy
    dev = '/dev/sda1'
    block_device_map = copy.deepcopy(image.block_device_mapping)
    assert new_size >= block_device_map[dev].size
    block_device_map[dev].size = new_size
    kws.update(block_device_map=block_device_map,
               image_id=image.id)
    return get_spot_instance(**kws)

# ______________________________________________________________________

__OR___ = '''

request = ec2.request_spot_instances(price=price, instance_type=instance_type, image_id=ami, count=1, key_name=KEY_NAME, security_groups=[''])[0]

while request.state == u'open':
  time.sleep(5)
  request = ec2.get_all_spot_instance_requests([request.id])[0]
  print time.ctime(), request.id, request.state, request.status

# ...
res = ec2.get_all_instances([request.instance_id])[0]
instance = res.instances[0]
print instance.public_dns_name
instance.add_tag('Name', 'Spotty (%s)' % time.ctime())
instance.update()
'''

# ______________________________________________________________________
# End of ec2_reference.py
