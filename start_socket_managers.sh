gnome-terminal --geometry 160x10+100+0 --title "Wall 1" -- python3 ~/socket_manager/socket_manager.py -td 10.18.88.101:4001 -cp 4101 -cts LF -hts LF
gnome-terminal --geometry 160x10+100+200 --title "Wall 2" -- python3 ~/socket_manager/socket_manager.py -td 10.18.88.102:4001 -cp 4102 -cts LF -hts LF
gnome-terminal --geometry 160x10+100+400 --title "Wall 3" -- python3 ~/socket_manager/socket_manager.py -td 10.18.88.103:4001 -cp 4103 -cts LF -hts LF
gnome-terminal --geometry 160x10+100+600 --title "FHCal " -- python3 ~/socket_manager/socket_manager.py -td 10.18.88.134:4001 -cp 4134 -cts LF -hts LF
gnome-terminal --geometry 160x10+100+800 --title "Hodoscope" -- python3 ~/socket_manager/socket_manager.py -td 10.18.88.48:4001 -cp 4048 -cts LF -hts LF
# gnome-terminal --geometry 160x10+100+100 --title "VETO" -- python3 ~/socket_manager/socket_manager.py -td 10.18.88.104:4001 -cp 4104 -cts LF -hts LF

