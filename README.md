Basespace Project Downloader
============================

Download fastq.gz files en-masse from a Project in Basespace

Step 1
------

Follow steps 1-5 from here to get a access\_token (you only need to do this once):

   [https://support.basespace.illumina.com/knowledgebase/articles/403618-python-run-downloader]

Your access token should look something like "ab637cf829938dedcc672798f382cd21".

Step 2
------

Go to Basespace, click Projects, and click the project you wish to download the FASTQ files from.
Your address bar should look like this:
    https://basespace.illumina.com/projects/18274645
    The final number (18274645) is your project id, take note of this.


Step 3
------
Run this script:
    `basespace_project_downloader.py -p <project_id> -a <access_token> -o <output_dir>`

For example (using the example parameters in the previous steps)
    `basespace_project_downloader.py -p 18274645 -a ab637cf829938dedcc672798f382cd21 -o .`
