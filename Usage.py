def gapi_generator(ids, sdate, edate, metrics, dimensions, sortby, filters, reportname,maxresults=None):
    
    ############# Arguments ############
    # ids = Provider ID from GA
    # sdate = Start Date
    # edate = End Date
    # metrics = Metrics from GA
    # dimensions = Dimensions from GA
    # sortby = Sort metric
    # filters = Filters to apply, if none simply leave '' as input
    # report name = CSV File Name
    # maxresults = Maximum number of results to export when query is too big or looking for top10/20/etc, should be a string
    ####################################
    
    import time
    import pandas
    import re
    import subprocess
    
    start = time.time()
    
    if maxresults is not None:
        args = "' '".join(["'"+ids,sdate,edate,metrics,dimensions,sortby,filters,reportname,maxresults+"'"])
    else:    
        args = "' '".join(["'"+ids,sdate,edate,metrics,dimensions,sortby,filters,reportname+"'"])
    
    cmd = "python hello_analytics_api_v3.py "+args
    prt = str(subprocess.check_output(cmd,shell=True))
    prt = re.sub(r'\\n' , '\n', prt) 
    prt = prt.replace("b'",'').replace("'",'').split('\n')
    for i in prt[0:len(prt)-1]:
        print(i)
    df = pd.read_csv(reportname+'.csv')
    end = time.time()
    print('Runtime (sec): '+str(round(end - start,0)))
    print('\n')
    print(df.head(5).to_string())
    return df

# Running Example
df = gapi_generator('ExampleID',
          'ExampleStartDate',
          'ExampleEndDate',
          'ExampleMetrics',
          'ExampleDimensions',
          'ExampleSort',
          'ExampleFilters',
         'ExampleReportName',
         'NumberOfResults')
