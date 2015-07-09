
tmpfile=`mktemp`
mvn -q dependency:list -DoutputFile=$tmpfile -DappendOutput=true
sort -u $tmpfile | grep "^ *.*:.*:.*:.*"| sed "s/^ *//" | awk 'BEGIN {IFS=":"; FS=":"; OFS=":"} {print $1,$2,$4}' | while read line; do
    wresp=`./listings.sh check w $line`
    bresp=`./listings.sh check b $line`
    if echo $wresp | grep -q "is whitelistd"; then
        wl=true
    elif echo $wresp | grep -q "is NOT whitelisted"; then
        wl=false
    else
        echo "Error communicating with Black&White list service"
        break
    fi
    if echo $bresp | grep -q "is blacklisted"; then
        bl=true
    elif echo $bresp | grep -q "is NOT blacklisted"; then
        bl=false
    else
        echo "Error communicating with Black&White list service"
        break
    fi
    if $wl && $bl; then
        echo "Both lists: $line"
    elif $wl; then
        echo "White list: $line"
    elif $bl; then
        echo "Black list: $line"
    else
        echo "None list:  $line"
    fi
done
rm $tmpfile

