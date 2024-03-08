#/bin/bash

# Get all website domains from the list
function get_websites(){
    while IFS="," read -r rec_column1 rec_column2
    do
        echo $rec_column2;
    done < tranco_25G99.csv
}

if [ ! websites.txt ]; then
    touch websites.txt
fi
counter=1
# for each website, replace it with its placeholder in the kubernetes template and add it in the jobs folder
for i in $(get_websites)
do
  cleared_website=$(echo $i | sed 's/\r//');
  printf "%s\n" $cleared_website >> websites.txt
  
  ((counter++))
  if [[ $counter -gt 10000 ]]; then
    break
  fi
done