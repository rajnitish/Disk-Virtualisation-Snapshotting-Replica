from Configure import *
from Frameworks.SnapshotingFramework import *

def section3_3_snapshot_ReplicaTest():
	Disk_create(1, 100)
	Disk_create(2, 80)
	Disk_create(3, 50)
	DB_write_replica(2, 10, "Ten")

	# Write in disk 1
	for i in xrange(0, 10):
		DB_write_replica(1, i, "1 ka " + str(i))

	# Write in disk 3
	for i in xrange(5, 15):
		DB_write_replica(3, i, "3 ka " + str(i))

	print "Reading 1 ka 5", DB_read_replica(1, 5)

	# Checkpoints for disk 1 & 3
	check1_1 = checkPoint(1)
	check3_1 = checkPoint(3)

	# Write in disk 3
	for i in xrange(11, 20):
		DB_write_replica(3, i, "After check1 : 3 ka " + str(i))

	# Read from disk 3
	for i in xrange(5,20):
		print "Reading 3 ka " + str(i), DB_read_replica(3, i)

	# Checkpoint for disk 3
	check3_2 = checkPoint(3)

	print "Deleting 1 :"
	Disk_delete(1)

	print "Rolling back 3 .............."
	rollBack(3, check3_1)

	print dP.printPatchList(dP.unoccupied)
	# Read from disk 3
	for i in xrange(5, 15):
		print "Reading 3 ka " + str(i), DB_read_replica(3, i)

section3_3_snapshot_ReplicaTest()