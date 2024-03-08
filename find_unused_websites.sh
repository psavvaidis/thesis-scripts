full_list="./10Kwebsites.txt"
processed_ws=()
ws=()
missing=()

echo "Start parsing 10K list"
# IFS=$IFS,
# Clear the file
for line in $(cat $full_list)
do
    # for word in $line; do split_line
    split_line=(${line//,/ })
    word=${split_line[1]}
    
    ws+=($word)
done
echo "Parsing ended"
echo "Starting checking logs folder"
for file in $(ls ./logs)
do
    filename=${file%".tar.gz"}
    processed_ws+=($filename)
done
echo "Check done"
echo ${processed_ws[@]} | sed 's/ /\
/g' > processed_ws.txt


echo Total: ${#ws[@]} Processed: ${#processed_ws[@]} Missing: ${#missing[@]}