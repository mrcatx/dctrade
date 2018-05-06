account=$1
verCode=$2
echo "$account $verCode"
cmd="docker exec -it dckdj2 python /code/exec_login.py $account $verCode"
echo $cmd
eval "$cmd"