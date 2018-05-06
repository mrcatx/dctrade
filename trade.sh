account=$1
echo $account
cmd="docker exec dckdj2 python /code/exec_trade.py $account"
echo $cmd
eval "$cmd"