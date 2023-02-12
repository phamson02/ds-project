#! /bin/bash

# logging date and time of  script execution
echo "================"
echo "($(date)) executing kaggle notebook: $1"

# change working directory to place where notebooks will be pulled and from where they will be pushed
cd $HOME/ds-project/kaggle_scheduler/

# from kaggle pull notebook provided as 1st argument of script to working directory and generate metadata file
kaggle kernels pull $1 -m

# since end of 2022-12 generated metadata are setting internet access of notebook to disable
# even though original downloaded notebook is internet enabled
# if you need to correct it, add following command to Stream EDitor below: 's!internet": false!internet": true!g

# correct wrong references to other notebooks used as resources in metadata file
# by removing "code/" and "datasets/" prefixes from resource names
# original pulled file is preserved under kernel-metadata.json.YYYY-mm-dd.OLD filename
sed -i.$(date +%F).OLD 's!code/!!g;s!datasets/!!g' kernel-metadata.json

# push notebook back to kaggle for execution
kaggle kernels push

# logging date and time of notebook execution and its status
echo "($(date)) kaggle notebook: $1 executed"
kaggle kernels status $1
echo "================"
echo