from google.cloud import monitoring
from googleapiclient import discovery
import google.auth
import os
import csv
import json
from pprint import pprint


project_root = os.path.abspath(os.path.join(__file__ ,"../.."))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = project_root + os.path.sep + "google-credentials.json"

credentials, project = google.auth.default()

resource_manager = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
compute = discovery.build('compute', 'v1', credentials=credentials)

instance_metrics = {'cpu utilization': 'instance/cpu/utilization',  # concatenates with compute api base url
                        'disk read bytes': 'instance/disk/read_bytes_count',
                        'disk read operations': 'instance/disk/read_ops_count',
                        'disk write bytes': 'instance/disk/write_bytes_count',
                        'disk write operations': 'instance/disk/write_ops_count',
                        'received bytes': 'instance/network/received_bytes_count',
                        'received packets': 'instance/network/received_packets_count',
                        'sent bytes': 'instance/network/sent_bytes_count',
                        'sent packets': 'instance/network/sent_packets_count'}


def get_monitoring_client(project):
    return monitoring.Client(project=project, credentials=credentials)


def main():
    data = {} # TODO dump project list back into data dict
    data['projects'] = api_call(resource_manager.projects(), 'projects', [])
    print "Found %d projects" % len(data['projects'])
    for project in data['projects']:  # for each project in the list of project dictionaries :
        project['instances'] = []  # add another key : value pair into project dictionary
        project_id = project['projectId']

        all_zones = api_call(compute.zones(), 'items', {'project': project_id})
        print "Found %d zones" % len(all_zones)
        for zone in all_zones:  # for each zone in list of zone dictionaries :
            zone_name = zone['name']
            current_instances = api_call(compute.instances(), 'items', {'project': project_id, 'zone': zone_name})

            if current_instances is not None and len(current_instances) > 0:
                pprint(compute.disks().list(project=project_id, zone=zone_name).execute())
                project['instances'].extend(current_instances)
                #for item in compute.disks().list(project=project_id, zone=zone_name).execute()['items']:
                #    print item['name']+' '+item['sizeGb']
                #pprint(current_instances)
        print "Found %d instances" % len(project['instances'])
        project['metrics'] = {}
        for key in instance_metrics:  # TODO Associate metrics with respective instance
            project['metrics'][key] = monitoring_call(project_id, key)
    to_csv([{'ya':'yahoo','yay':'yep'},{'good':'sick','great':'i know','sure':'really'},{'good':'cool','great':'i know','sure':'really'}])
    print read_csv()
    print get_ram('model-2')


def api_call(base, key, args): # generic method for pulling relevant data from api response
    export = []
    if args:
        request = base.list(**args)
    else:
        request = base.list()

    while request is not None:
        response = request.execute()
        if key in response:
            export.extend(response[key])
        request = base.list_next(previous_request=request, previous_response=response)
    return export


def monitoring_call(project_id, metric):
    client = get_monitoring_client(project_id)
    METRIC = 'compute.googleapis.com/' + instance_metrics[metric]
    query = client.query(METRIC, minutes=5)
    return query.as_dataframe()

def to_csv(dict):
    #file = open('test.csv','w')
    #for item in dict:
    #    file.write(','.join(item))
    #    file.write('\n')
    #file.close()
    with open('mycsvfile.csv', 'wb') as f:
        for item in dict:
            w = csv.DictWriter(f, item.keys())
            w.writerow(item)
    f.close()

def read_csv():
    with open('mycsvfile.csv', 'rb') as f:
        reader = csv.reader(f)
        lst=(list(reader))
    f.close()
    return lst

def get_cpus(model):
    with open('models.csv', 'rb') as f:
        reader = csv.reader(f)
        lst=(list(reader))
    f.close()
    for row in lst:
        if row[0] == model:
            return row[1]

def get_ram(model):
    with open('models.csv', 'rb') as f:
        reader = csv.reader(f)
        lst=(list(reader))
    f.close()
    for row in lst:
        if row[0] == model:
            return row[2]

#def get_disk(project_id, zone, instance):


if __name__ == '__main__':
    main()