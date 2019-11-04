from Configure import *
from Frameworks.SnapshotingFramework import *

def section3_3_snapshot_Test():
	Disk_create(1, 100)
	Disk_create(2, 200)
	Disk_create(3, 50)
	DB_write(2, 10, "Ten")

	# Write in disk 1
	for i in xrange(0, 10):
		DB_write(1, i, "1 ka " + str(i))

	# Write in disk 3
	for i in xrange(5, 15):
		DB_write(3, i, "3 ka " + str(i))

	print "Reading 1 ka 5", DB_read(1, 5)

	# Checkpoints for disk 1 & 3
	check1_1 = checkPoint(1)
	check3_1 = checkPoint(3)

	# Write in disk 3
	for i in xrange(11, 20):
		DB_write(3, i, "After check1 : 3 ka " + str(i))

	# Read from disk 3
	for i in xrange(5,20):
		print "Reading 3 ka " + str(i), DB_read(3, i)

	# Checkpoint for disk 3
	check3_2 = checkPoint(3)

	print "Deleting 1 :"
	Disk_delete(1)

	print "Rolling back 3 .............."
	rollBack(3, check3_1)

	# Read from disk 3
	for i in xrange(0, 20):
		print "Reading 3 ka " + str(i), DB_read(3, i)

section3_3_snapshot_Test()