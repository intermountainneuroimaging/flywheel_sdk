import os
import flywheel
import logging
import sys
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('main')

# import custom helper functions, need to first add path to system envrionment... 
#      do that using current directory inside jupyter notebooks, 
#      or __file__ attribute in script
try:
    absolute_path = os.path.abspath(__file__)
    sys.path.insert(0, Path(absolute_path).parts[0:-2])
except NameError:
    sys.path.insert(0, os.path.dirname(os.getcwd()))
    
from _helper_functions import gears
from _helper_functions import fileIO, utils


# set default permissions
os.umask(0o002);

# get flywheel client
fw = flywheel.Client('')


if __name__ == "__main__":
    
    # locate *jobs* completed within the lookback window
    lookback = 30
    created_by = gears.get_x_days_ago(lookback).strftime('%Y-%m-%d')
    all_jobs = fw.jobs.find(f'created>{created_by}')
    
    # get unique list of sessions with jobs run in lookback window
    all_sids=[]
    for job in all_jobs:
        try: 
            fw.get(job.destination["id"])
        except:
            continue
        all_sids.append(fw.get(job.destination["id"]).parents["session"])
    filtered_session_ids = list(set(all_sids))

    #Loop through sessions and see which ones apply for the gear rule to kick off
    for sid in filtered_session_ids:
        try:
            log.info("checking workflow: %s/%s/%s",fw.get_project(fw.get_session(sid).parents["project"]).label, fw.get_session(sid).subject.label, fw.get_session(sid).label)
            gears.run_auto_download(sid, template_file_name="gears_template1.json")
        except Exception as e:
            log.warning(e)


    