fedfile = 
fedfilenew = 
bashCommand = "cp %s"%fedfile
import subprocess
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
