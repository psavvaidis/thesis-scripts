import docker 
import sys

client = docker.from_env()

def spinContainer(website):
    try:
        container = client.containers.run('extendedvv8:latest',
                              command=[f"source .venv/bin/activate; python3 /data/watch_logs.py {website}; tar -cvzf {website}.tar.gz *;mv {website}.tar.gz /data/{website}.tar.gz;"],
                              volumes=["/media/Storage/logs/:/data"], entrypoint=["/bin/bash", "-c"], tty=True, stderr=True, auto_remove=True)
        # container.stop()
    except Exception as e:
        print(e)

if(__name__=="__main__"):
    i=0
    try:
        # spinContainer("airbnb.com")
        websites_file = sys.argv[1]
        
        with open(websites_file) as fp:
            for website in fp:
                print(i)
                if(i>8750 and i <=10000):
                    spinContainer(website.splitlines()[0])
                i+=1
    except Exception as e:
        print(e)
