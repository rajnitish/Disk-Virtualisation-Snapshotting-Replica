from Configure import *
from Frameworks.VirtualisationFramework import *

def section3_1Test():
    Disk_create(1, 100)
    Disk_create(2, 200)
    DB_write(1, 5, "Five")
    DB_write(2, 10, "Ten")
    dP.printDisks()
    print "Reading disk 2 : ", DB_read(2, 10)
    print "Reading disk 1 : ", DB_read(1, 5)
    print "Writing to disk 1 : ", DB_write(1, 5, "Six")
    print "Reading disk 1 : ", DB_read(1,5)
    print "Deleting disk 2 : ", Disk_delete(2)
    dP.printDisks()
    print "Deleting disk 1 : ", Disk_delete(1)
    dP.printDisks()

def test_frag_1():
    Disk_create(1, 50)
    Disk_create(2, 50)
    Disk_create(3, 160)
    Disk_create(4, 100)
    DB_write(3, 5, "3 ka Five")
    dP.printDisks()
    print "Deleting 3 :"
    Disk_delete(3)
    Disk_create(5, 200)
    DB_write(5, 10, "5 ka Ten")
    DB_write(5, 190, "5 ka 190")
    dP.printDisks()

def test_frag_2():
    Disk_create(1, 50)
    Disk_create(2, 50)
    Disk_create(3, 150)
    Disk_create(4, 50)
    DB_write(3, 5, "3 ka Five")
    dP.printDisks()
    print "Deleting 3 :"
    Disk_delete(3)
    Disk_create(5, 200)
    DB_write(5, 5, "5 ka Five")
    dP.printDisks()

print "---------- BASIC TEST : -------------"
section3_1Test()
# print "---------- FRAG TEST 1 : -------------"
# test_frag_1()
# print "---------- FRAG TEST 2 : -------------"
# test_frag_2()