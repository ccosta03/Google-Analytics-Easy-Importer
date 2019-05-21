#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple intro to using the Google Analytics API v3.

This application demonstrates how to use the python client library to access
Google Analytics data. The sample traverses the Management API to obtain the
authorized user's first profile ID. Then the sample uses this ID to
contstruct a Core Reporting API query to return the top 25 organic search
terms.

Before you begin, you must sigup for a new project in the Google APIs console:
https://code.google.com/apis/console

Then register the project to use OAuth2.0 for installed applications.

Finally you will need to add the client id, client secret, and redirect URL
into the client_secrets.json file that is in the same directory as this sample.

Sample Usage:

  $ python hello_analytics_api_v3.py

Also you can also get help on all the command-line flags the program
understands by running:

  $ python hello_analytics_api_v3.py --help
"""
from __future__ import print_function

__author__ = 'api.nickm@gmail.com (Nick Mihailovski)'
__author__ = 'cbernardocosta@gmail.com (Carlos Costa)'

import argparse
import sys
import pandas as pd
import csv
import os

from googleapiclient.errors import HttpError
from googleapiclient import sample_tools
from oauth2client.client import AccessTokenRefreshError

# GoogleAPI Connection
def fetcher(argv):
  return sample_tools.init(
      argv, 'analytics', 'v3', __doc__, __file__,
      scope='https://www.googleapis.com/auth/analytics.readonly')

# Main
def main():
  # Authenticate and construct service.
  service, flags = fetcher(sys.argv[0:0])

  # Try to make a request to the API. Print the results or handle errors.
  try:
    first_profile_id = sys.argv[1]
    
    if not first_profile_id:
      print('Could not find a valid profile for this user.')
    
    else:
      
      output = []
      lencheck = 0

      if(sys.argv[9] is not None):
        total_results = int(sys.argv[9])
        results = get_top_keywords(service, first_profile_id,'1', sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7],int(sys.argv[9]))
        lencheck = 1
      else:
        total_results = results.get('totalResults')
        results = get_top_keywords(service, first_profile_id,'1', sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7],10000)
      
      for header in results.get('columnHeaders'):
        output.append('%30s' % header.get('name'))

      results_final=[[i.strip() for i in output]]
  
      for i in results.get('rows'):
        results_final.append(i)

      results_total = results_final
      
      # Progress Report   
      print('GA Total Results: '+str(results.get('totalResults')))

      if(lencheck == 0):
        for i in range(1,total_results,10000)[1:]:
          aux = get_top_keywords(service, first_profile_id,str(i), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7],10000)
          for i in aux.get('rows'):
            results_total.append(i)
      else:
        for i in range(1,total_results,10000)[1:]:
          aux = get_top_keywords(service, first_profile_id,str(i), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7],int(sys.argv[9]))
          for i in aux.get('rows'):
            results_total.append(i)

      print('DataFrame Results: '+str(len(results_final) -1))

      reportname = sys.argv[8]
      reportname = str(reportname+'.csv')
      if(os.path.isfile(reportname)):
        os.remove(reportname)
      with open(reportname, "w") as f:
        writer = csv.writer(f)
        writer.writerows(results_total)


  except TypeError as error:
    # Handle errors in constructing a query.
    print(('There was an error in constructing your query : %s' % error))

  except HttpError as error:
    # Handle API errors.
    print(('Arg, there was an API error : %s : %s' %
           (error.resp.status, error._get_reason())))

  except AccessTokenRefreshError:
    # Handle Auth errors.
    print ('The credentials have been revoked or expired, please re-run '
           'the application to re-authorize')


def get_first_profile_id(service):
  """Traverses Management API to return the first profile id.

  This first queries the Accounts collection to get the first account ID.
  This ID is used to query the Webproperties collection to retrieve the first
  webproperty ID. And both account and webproperty IDs are used to query the
  Profile collection to get the first profile id.

  Args:
    service: The service object built by the Google API Python client library.

  Returns:
    A string with the first profile ID. None if a user does not have any
    accounts, webproperties, or profiles.
  """

  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    firstAccountId = accounts.get('items')[0].get('id')
    webproperties = service.management().webproperties().list(
        accountId=firstAccountId).execute()

    if webproperties.get('items'):
      firstWebpropertyId = webproperties.get('items')[0].get('id')
      profiles = service.management().profiles().list(
          accountId=firstAccountId,
          webPropertyId=firstWebpropertyId).execute()

      if profiles.get('items'):
        return profiles.get('items')[0].get('id')

  return None



def get_top_keywords(service, profile_id, bottom, sdate, edate, metrics, dim, sby, filters, mres):
  """Executes and returns data from the Core Reporting API.
  This queries the API for the top 25 organic search terms by visits.
  Args:
    service: The service object built by the Google API Python client library.
    profile_id: String The profile ID from which to retrieve analytics data.
  Returns:
    The response returned from the Core Reporting API.
  """

  if(filters == ''):
    return service.data().ga().get(
      ids='ga:' + profile_id,
      start_date=sdate,
      end_date=edate,
      metrics=metrics,
      dimensions=dim,
      sort=sby,
      start_index=bottom,
      max_results=mres).execute()
  else:
    return service.data().ga().get(
        ids='ga:' + profile_id,
        start_date=sdate,
        end_date=edate,
        metrics=metrics,
        dimensions=dim,
        sort=sby,
        filters=filters,
        start_index=bottom,
        max_results=mres).execute()
    
if __name__ == '__main__':
  main()
