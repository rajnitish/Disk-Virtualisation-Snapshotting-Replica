import PartitioningFramework as dP
import random


def Block_write(block_no, write_data):
	dP.PB_write(block_no, write_data)

def Block_read(block_no):
	dP.PB_read(block_no)

def Disk_create(id, num_blocks):
	if (dP.virtualDiskSize - dP.usedBlocks < num_blocks) or dP.diskMap.has_key(id):
		raise Exception("Error : Either not enough space or disk id already there")
	else:
		createPatch(id, num_blocks)

def createPatch(id, num_blocks):
	if not dP.diskMap.has_key(id):
		dP.diskMap[id] = dP.Disk(id, num_blocks)
	
	disk = dP.diskMap[id]
	l = [(n,i) for n,i in enumerate(dP.unoccupied) if i.num >= num_blocks]
	
	if (len(l)==0):
		p = dP.Patch(dP.unoccupied[-1].blockNo, dP.unoccupied[-1].num)
		(disk.patches).append(p)
		dP.unoccupied.pop()
		dP.usedBlocks += p.num 
		createPatch(id,num_blocks-p.num)
	else:
		index = (l[0])[0]
		patchBlockNo = l[0][1].blkNo
		patchNum = l[0][1].num
		(disk.patches).append(dP.Patch(patchBlockNo,num_blocks))
		if (patchNum == num_blocks):
			dP.unoccupied.pop(index)
		else:
			currentvalue = patchNum - num_blocks
			while index > 0 and dP.unoccupied[index-1].num > currentvalue:
				dP.unoccupied[index].blockNo = dP.unoccupied[index-1].blockNo
				dP.unoccupied[index].num = dP.unoccupied[index-1].num
				index -= 1
			dP.unoccupied[index].blockNo = patchBlockNo + num_blocks
			dP.unoccupied[index].num = currentvalue
		dP.usedBlocks += num_blocks

def getVirtualDiskNo(diskPatches, block_no):
	total_blocks = 0
	i = 0
	while (diskPatches[i].num + total_blocks < block_no+1):
		total_blocks += diskPatches[i].num
		i += 1
	return diskPatches[i].blkNo + block_no - total_blocks

def DB_read(id, block_no):
	if not dP.diskMap.has_key(id):
		raise Exception("Error : Invalid disk id")
	
	disk = dP.diskMap[id]
	if disk.numBlocks < block_no+1:
		raise Exception("Error : Invalid block number")
	
	disk.commandList.append(("readDiskBlock", block_no))
	print "Reading disk block..."
	# path no known.
	print "Virtual disk no : ", getVirtualDiskNo(disk.patches, block_no)
	return dP.PB_read(getVirtualDiskNo(disk.patches, block_no))

def DB_write(id, block_no, write_data):
	if not dP.diskMap.has_key(id):
		raise Exception("Error : Invalid disk id")

	disk = dP.diskMap[id]
	if disk.numBlocks < block_no+1:
		raise Exception("Error : Invalid block number")
	disk.commandList.append(("writeDiskBlock", block_no, write_data))
	
	print "Finding disk block..."
	print "Virtual disk no : ", getVirtualDiskNo(disk.patches, block_no)
	dP.PB_write(getVirtualDiskNo(disk.patches, block_no), write_data)
	print "Written disk block..."
	
	
def DB_read_replica(id, block_no):
	if not dP.diskMap.has_key(id):
		raise Exception("Error : Disk does not exist")

	disk = dP.diskMap[id]
	if disk.numBlocks < block_no+1:
		raise Exception("Error : Invalid block number")
	
	disk.commandList.append(("readDiskBlock", block_no))
	# random no in 1 to 100.
	print "Reading disk block..."
	if random.randint(1, 100) < 10:
		# assuming replica always exists : ERROR?
		print "Read error!"
		if (len(dP.unoccupied)==0):
			raise Exception("Error : Replica cannot be made")
		else:
			newReplicaBlockNo = dP.unoccupied[0].blkNo
			if (dP.unoccupied[0].num == 1):
				dP.unoccupied.pop(0)
			else:
				dP.unoccupied[0].num -= 1
				dP.unoccupied[0].blkNo += 1
			dP.usedBlocks += 1

			patches_new = []
			virt_original = getVirtualDiskNo(disk.patches, block_no)
			virt_replica = dP.getBlockReplica(virt_original)
			virt_new_replica = newReplicaBlockNo

			dP.setBlockReplica(virt_replica, virt_new_replica)
			dP.setBlockReplica(virt_new_replica, virt_replica)
			ans = dP.PB_read(virt_replica)
			Block_write(virt_new_replica, ans)
			
			newOriginal = dP.Patch(virt_replica, 1)
			newReplica = dP.Patch(virt_new_replica,1)
			for p in disk.patches:
				if ((virt_replica < p.blkNo or virt_replica >= (p.blkNo + p.num)) and (virt_original < p.blkNo or virt_original >= (p.blkNo + p.num))):
					patches_new.append(p)

				elif ((virt_original < p.blkNo or virt_original > (p.blkNo+p.num)) and p.blkNo <= virt_replica and virt_replica < p.blkNo+p.num):
					# only replica in this patch.
					if virt_replica > p.blkNo:
						left_patch = dP.Patch(p.blkNo, virt_replica - p.blkNo)
						patches_new.append(left_patch)
					patches_new.append(newReplica)
					if virt_replica < (p.blkNo + p.num - 1):
						right_patch = dP.Patch(virt_replica+1, p.num - (virt_replica - p.blkNo + 1))
						patches_new.append(right_patch)

				elif ((virt_replica > p.blkNo+p.num or virt_replica < p.blkNo) and p.blkNo <= virt_original and virt_original < p.blkNo+p.num):
					# only original in this patch.
					if virt_original > p.blkNo:
						left_patch = dP.Patch(p.blkNo, virt_original - p.blkNo)
						patches_new.append(left_patch)
					patches_new.append(newOriginal)
					if virt_original < (p.blkNo + p.num - 1):
						right_patch = dP.Patch(virt_original+1, p.num - (virt_original - p.blkNo + 1))
						patches_new.append(right_patch)

				else:
					if virt_original > p.blkNo:
						left_patch = dP.Patch(p.blkNo, virt_original - p.blkNo)
						patches_new.append(left_patch)
					patches_new.append(newOriginal)
					if virt_original < virt_replica-1:
						mid_patch = dP.Patch(virt_original+1, virt_replica - virt_original - 1)
						patches_new.append(mid_patch)
					patches_new.append(newReplica)
					if virt_replica < (p.blkNo + p.num - 1):
						right_patch = dP.Patch(virt_replica+1, p.num - (virt_replica - p.blkNo + 1))
						patches_new.append(right_patch)

			disk.patches = dP.mergePatches(patches_new)
			print "New patches : "
			for i in disk.patches:
				print str(i.blkNo) + " " + str(i.num)
	else:
		print "Old patches : "
		for i in disk.patches:
			print str(i.blkNo) + " " + str(i.num)
		ans = dP.PB_read(getVirtualDiskNo(disk.patches, block_no))
	return ans	

def DB_write_replica(id, block_no, write_data):
	if not dP.diskMap.has_key(id):
		raise Exception("Error : Disk does not exist")

	disk = dP.diskMap[id]
	if disk.numBlocks < block_no+1:
		raise Exception("Error : Invalid block number")
	disk.commandList.append(("writeDiskBlock", block_no, write_data))
	print "Finding disk block..."
	virtual_block_no = getVirtualDiskNo(disk.patches, block_no)
	dP.PB_write(virtual_block_no, write_data)
	delta = disk.numBlocks/2
	block_replica_disk = (block_no + delta) if block_no < delta else (block_no - delta)
	virtual_replica_block_no = getVirtualDiskNo(disk.patches, block_replica_disk)
	curr_replica = dP.getBlockReplica(virtual_block_no)
	if curr_replica == -1 or curr_replica != virtual_replica_block_no:
		dP.setBlockReplica(virtual_block_no, virtual_replica_block_no)
		dP.setBlockReplica(virtual_replica_block_no, virtual_block_no)

	print "Virtual replica block no : ", str(dP.getBlockReplica(virtual_block_no))
	dP.PB_write(dP.getBlockReplica(virtual_block_no), write_data)
	print "Written disk block..."

def Disk_delete(id):
	if not dP.diskMap.has_key(id):
		raise Exception("Error : Invalid disk id")

	disk = dP.diskMap[id]
	unoccupied = dP.unoccupied + disk.patches
	unoccupied_sorted_index = sorted(unoccupied, key=lambda x: x.blkNo)
	unoccupied_new = dP.mergePatches(unoccupied_sorted_index)
	dP.unoccupied = sorted(unoccupied_new, key=lambda x: x.num)
	dP.usedBlocks -= disk.numBlocks
	dP.diskMap.pop(id)
	print "Deleted disk..."

def checkPoint(disk_id):
	disk = dP.diskMap[disk_id]
	disk.checkPointMap.append(len(disk.commandList))
	return len(disk.checkPointMap)-1

def rollBack(disk_id, checkpoint_id):
	# save checkpoint to command List
	if not dP.diskMap.has_key(disk_id):
		raise Exception("Error : Invalid disk id")
	
	disk = dP.diskMap[disk_id]
	checkpoints = disk.checkPointMap[:(checkpoint_id)] # excluding the current one
	commands = disk.commandList[:(disk.checkPointMap[checkpoint_id])]
	
	# delete disk from diskMap
	Disk_delete(disk_id)
	# create new disk, exec all cmds
	for cmd in commands:
		if cmd[0] == "createDisk":
			Disk_create(cmd[1], cmd[2])
			disk = dP.diskMap[disk_id]
		elif cmd[0] == "readDiskBlock":
			x = readDiskBlock(disk_id, cmd[1])
		else:
			DB_write(disk_id, cmd[1], cmd[2])
	disk.checkPointMap = checkpoints
	disk.commandList = commands

	print disk.commandList
	print disk.checkPointMap
	
