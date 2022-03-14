#!/bin/bash
if [ -z "$1" ]; then
	echo -n "Please enter a tag: "
	read tag
else
	tag=$1
fi	


SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

folder=${SCRIPT_DIR##*/}

echo "creating image dahny/$folder:$tag"

cd $SCRIPT_DIR
#mvn install
docker build -t dahny/$folder:$tag .
docker push dahny/$folder:$tag 
