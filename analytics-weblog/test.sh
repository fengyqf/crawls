#!/usr/bin/env bash

while getopts "t:dh" arg
do
    case $arg in
        t)
            logtype_name=$OPTARG
            ;;
        h)
            output_header="Y"
            ;;
        d)
            dbg=1
            ;;
        ?)
    esac
done
shift $((OPTIND-1))
log_filepath=$@


f_time=`stat -c %Y $log_filepath`
f_size=`stat -c %s $log_filepath`
f_name=$log_filepath

echo "$log_filepath $f_size $f_time"


cache_db_file="cache_file.cache"


awk -v f_time="$f_time" -v f_size="$f_size" -v f_name="$f_name"  \
    'BEGIN{
        #标记变量 文件是否变更过
        f_changed=0
        to_renew_cache=0
        found_in_cache=0
        #cache
        #append
    }
    {
        if($1==f_name || $2!=f_size || $3!=f_time){
            found_in_cache=1
        }
    }
    END{
        if(to_renew_cache==1 || found_in_cache==0 || 1==1 ){
            for(i=1;i<=NR;i++){
                if(cache[i]!=""){
                    print cache[i] > cache_db_file
                }
            }
        }
        if(f_changed==1){
            print "Yes"
        }else{
            print "No"
        }
    }' $cache_db_file


'
        }else{
            cache[NR]=sprintf("%s %s %s\n",$1,$2,$3)

            if($2!=$f_size || $3!=$f_time){
                f_changed=1
                to_renew_cache=1
            }

'