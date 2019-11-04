class Block:
	blkInfo = ''
	replica = -1

class Disk:
	id = 0
	numBlocks = 0
	commandList = []
	checkPointMap = []
	patches = []

	def __init__(self,idname,noB):
		self.id = idname
		self.numBlocks = noB
		self.patches = []
		self.commandList = [("createDisk", idname, noB)]
		self.checkPointMap = []

class Patch:
	blkNo = 0
	num = 0

	def __init__(self,block,noB):
		self.blkNo = block
		self.num = noB

sizeA = 200
sizeB = 300
virtualDiskSize = sizeA + sizeB
diskA = [Block() for i in xrange(sizeA)]
diskB = [Block() for i in xrange(sizeB)]
disks = [diskA, diskB]
usedBlocks = 0
diskMap = {}
p = Patch(0,virtualDiskSize)
unoccupied = [p]
virtualToPhy = {}

total_blocks = 0
for i in xrange(0,len(disks)):
	for j in xrange(0,len(disks[i])):
		virtualToPhy[total_blocks + j] = (i, j)
	total_blocks += len(disks[i])

#Writing to Physical block
def PB_write(blkNo, blkInfo):
	disks[virtualToPhy[blkNo][0]][virtualToPhy[blkNo][1]].blkInfo = blkInfo

def PB_read(blkNo):
	# print virtualToPhy[blkNo]
	return disks[virtualToPhy[blkNo][0]][virtualToPhy[blkNo][1]].blkInfo

def getBlockReplica(blkNo):
	return disks[virtualToPhy[blkNo][0]][virtualToPhy[blkNo][1]].replica

def setBlockReplica(blkNo, replica_blkNo_virt):
	disks[virtualToPhy[blkNo][0]][virtualToPhy[blkNo][1]].replica = replica_blkNo_virt

def printDisks():
	count = 0
	for i in disks:
		print "\nDisk No. " + str(count)
		count += 1
		for j in i:
			print "Data : " + j.blkInfo + ", Replica : " + str(j.replica)

def printPatchList(plist):
	for p in plist:
		print "Block no : " + str(p.blkNo) + ", num : " + str(p.num)

def mergePatches(patches_list):
	patches_new = []
	current_patch = patches_list[0]
	for i in xrange(1,len(patches_list)):
		p = patches_list[i]
		if p.blkNo == (current_patch.blkNo + current_patch.num):
			current_patch.num += p.num
		else:
			patches_new.append(current_patch)
			current_patch = p
	patches_new.append(current_patch)
	patches_list = patches_new
	return patches_new