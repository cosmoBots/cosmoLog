#echo "Waiting 15 seconds until network is stable"
#sleep 15
ifconfig
echo "Waiting 10 seconds before launching processes, if you need to interrupt, do it now!!"
sleep 10
python3 TempSens.py &
echo "Lanzado TempSens"
python3 PressSens.py &
echo "Lanzado PressSens"
