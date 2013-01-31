import subprocess

print "Starting robot"
print "Warning user"
subprocess.Popen(["espeak","The robot is not powered!"])
print "Done warning the user"
print "Executing more important code...."

