import docker 
import sys

client = docker.from_env()

def spinContainer(website):
    try:
        container = client.containers.run('visiblev8/vv8-base:latest',
                              command=[f"/opt/chromium.org/chromium/chrome --no-sandbox --timeout=300000 --headless=new --virtual-time-budget=120000 --user-data-dir=/tmp --disable-dev-shm-usage {website}; tar -cvzf {website}.tar.gz vv8-*.log;rm vv8-*;mv {website}.tar.gz /data/{website}.tar.gz"],
                              volumes=["/home/panos/CodingProjects/visiblev8/experiment/logs/:/data"],entrypoint=["/bin/bash", "-c"], tty=True, stderr=True, remove=True)
        container.stop(timeout=300)
    except Exception as e:
        print(e)

if(__name__=="__main__"):
    i=0
    try:
        websites_file = sys.argv[1]

        with open(websites_file) as fp:
            for website in fp:
                print(i)
                if(i>7900 and i <=10000):
                    spinContainer(website.splitlines()[0])
                i+=1
    except Exception as e:
        print(e)