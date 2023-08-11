# Must be present in PX4-Autopilot folder
# First run: `tmux new`, then launch the script

tmux new-session -d -s my_session -n window_1 "./Tools/simulation/sitl_multiple_run.sh 6 && ./Tools/simulation/jmavsim/jmavsim_run.sh -l"
tmux split-window -h -t my_session:window_1 "./Tools/simulation/jmavsim/jmavsim_run.sh -p 4561 -l"
tmux split-window -h -t my_session:window_1 "./Tools/simulation/jmavsim/jmavsim_run.sh -p 4562 -l"
tmux split-window -h -t my_session:window_1 "./Tools/simulation/jmavsim/jmavsim_run.sh -p 4563 -l"
tmux split-window -h -t my_session:window_1 "./Tools/simulation/jmavsim/jmavsim_run.sh -p 4564 -l"
tmux split-window -h -t my_session:window_1 "./Tools/simulation/jmavsim/jmavsim_run.sh -p 4565 -l"