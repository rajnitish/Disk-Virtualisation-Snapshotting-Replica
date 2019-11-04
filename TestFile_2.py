from Configure import *
from Frameworks.VirtualisationFramework import *

def section3_1_ReplicaTest():
	Disk_create(1, 50)
	Disk_create(2, 50)
	Disk_create(3, 150)
	Disk_create(4, 100)
	
	# Write in disk 3
	for i in xrange(0, 30):
		DB_write_replica(3, i, "3 ka " + str(i))

	# Read from disk 3
	for i in xrange(0, 30):
		print "Reading 3 ka " + str(i), DB_read_replica(3, i)
		if (i%3 == 0):
			dP.printDisks()

	Disk_delete(2)
	print dP.printPatchList(dP.unoccupied)

	print ("-------------------------------------------------------")
	Disk_create(5,100)
	
	# Write in disk 5
	for i in xrange(0, 30):
		DB_write_replica(5, i, "5 ka " + str(i))

	# Read from disk 5
	for i in xrange(0, 30):
		print "Reading 5 ka " + str(i), DB_read_replica(5, i)
		if (i%3 == 0):
			dP.printDisks()
			print dP.printPatchList(dP.unoccupied)

	print dP.printPatchList(dP.unoccupied)

	print ("-------------------------------------------------------")
	Disk_create(6,55)

	# Write in disk 6
	for i in xrange(0, 20):
		DB_write_replica(6, i, "6 ka " + str(i))

	# Read from disk 6
	for i in xrange(0, 20):
		print "Reading 6 ka " + str(i), DB_read_replica(6, i)
		if (i%3 == 0):
			dP.printDisks()

	print dP.printPatchList(dP.unoccupied)

section3_1_ReplicaTest()