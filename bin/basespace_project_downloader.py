#!/usr/bin/env python
import os
import sys
import argparse
import json
import math
import subprocess
from urllib2 import Request, urlopen, URLError


base_url = "https://api.basespace.illumina.com/"

def parse_args():

    parser = argparse.ArgumentParser(prog='basespace_project_downloader.py')
    parser.add_argument('-p', dest='project_id', required=True,
                        help='Illumina project ID'),
    parser.add_argument('-a', dest='access_token', required=True,
                        help='Access token (default: read from stdin)'),
    parser.add_argument('-o', dest='output_dir', required=True,
                        help='Output directory')

    args = parser.parse_args()

    return args


def restrequest(rawrequest):
    request = Request(rawrequest)

    try:
        response = urlopen(request)
        json_string = response.read()
        json_obj = json.loads(json_string)

    except URLError, e:
        print 'Got an error code:', e
        sys.exit()

    return json_obj


def download_files(href, access_token, output_dir):

    if not os.path.isdir(output_dir):
        raise OSError(output_dir + " is not a directory")

    request = base_url + ("%s?access_token=%s&limit=1" % (href, access_token))
    json_obj = restrequest(request)

    total_file_count = json_obj["Response"]["TotalCount"]

    num_offsets = int(math.ceil(float(total_file_count)/1000.0))

    for index in xrange(num_offsets):
        offset = 1000*index
        request = base_url + ('%s?access_token=%s&limit=1000&Offset=%i' % (href, access_token, offset))
        json_obj = restrequest(request)

        for f_json_obj in json_obj['Response']['Items']:
            target_path = os.path.join(output_dir, f_json_obj["Path"])
            if os.path.exists(target_path):
                if os.path.getsize(target_path) == f_json_obj["Size"]:
                    print "        %s exists and is the same as BaseSpace's reported size (%i). Skipping...." % (target_path, f_json_obj["Size"])
                    continue
                print "        %s exists but is not of the correct size. (%i vs %i). Re-downloading..." % (target_path, os.path.getsize(target_path), f_json_obj["Size"])

            wget_url = base_url + ('%s?access_token=%s' % (f_json_obj["HrefContent"], access_token))


            print "        Downloading %s to %s....(%i bytes)\n" % (f_json_obj["Path"], target_path, f_json_obj["Size"])
            p = subprocess.Popen(["wget","-O", target_path, wget_url])
            p.wait()

            print "\n"
            if os.path.getsize(target_path) != f_json_obj["Size"]:
                raise Exception("Downloading error. %s incorrect size (%i vs %i)" % (target_path, os.path.getsize(target_path), f_json_obj["Size"]))


if __name__ == '__main__':

    args = parse_args()

    print "Querying Project: "

    request = base_url + ("v1pre3/projects/%s?access_token=%s" % (args.project_id, args.access_token))
    json_obj = restrequest(request)

    print "    Project found - " + json_obj["Response"]["Name"]

    print "Querying Project Samples: "
    request = base_url + ("%s?access_token=%s" % (json_obj["Response"]["HrefSamples"], args.access_token))
    json_obj = restrequest(request)

    sample_hrefs = []
    for sample_json in json_obj["Response"]["Items"]:
        print "    Sample found - %s (Experiment: %s)" % (sample_json["SampleId"], sample_json["ExperimentName"])
        sample_hrefs.append(sample_json["Href"])

    print "Querying Individual Samples: "
    for sample_href in sample_hrefs:
        request = base_url + ("%s?access_token=%s" % (sample_href, args.access_token))
        json_obj = restrequest(request)

        
        base_dir = args.output_dir
        if json_obj["Response"]["ExperimentName"]:
             base_dir = os.path.join(args.output_dir, json_obj["Response"]["ExperimentName"])
             if not os.path.exists(base_dir):
                 print "    Creating new directory for experiment: %s" % json_obj["Response"]["ExperimentName"]
                 os.mkdir(base_dir)
                

        sample_dir = os.path.join(base_dir, json_obj["Response"]["SampleId"])
        if not os.path.exists(sample_dir):
            print "    Creating new directory for sample: %s" % json_obj["Response"]["SampleId"]
            os.mkdir(sample_dir)

        if not os.path.isdir(sample_dir):
            raise OSError(sample_dir + " is not a directory")

        print "    Getting Files For Sample: %s" % json_obj["Response"]["SampleId"]

        download_files(json_obj["Response"]["HrefFiles"], args.access_token, sample_dir)
