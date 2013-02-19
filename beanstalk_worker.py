import sys
import os
import json

import beanstalkc
beanstalk = beanstalkc.Connection(host='localhost', port=11300)

def main():
    try:
        while True:
            job = beanstalk.reserve()
            job_info = json.loads(job.body)
            print "Received job: %s" % job_info['filename']
            job.delete()
    except KeyboardInterrupt:
        pass
    finally:
        beanstalk.close()

if __name__ == '__main__':
    main()
