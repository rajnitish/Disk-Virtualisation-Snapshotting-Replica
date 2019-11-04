import PartitioningFramework as dP
import random

def Block_write(blkNo, blkInfo):
	dP.PB_write(blkNo, blkInfo)

def Block_read(blkNo):
	dP.PB_read(blkNo)

def Disk_create(id, numBlocks):
	if (dP.virtualDiskSize - dP.usedBlocks < numBlocks) or dP.diskMap.has_key(id):
		raise Exception("Error caught ::DiskID already present or no more space")
	else:
		Patch_create(id, numBlocks)


def Patch_create(id, numBlocks):
	if not dP.diskMap.has_key(id):
		dP.diskMap[id] = dP.Disk(id, numBlocks)

	disk = dP.diskMap[id]
	l = [(n,i) for n,i in enumerate(dP.unoccupied) if i.num >= numBlocks]
	
	if (len(l)==0):
		p = dP.Patch(dP.unoccupied[-1].blkNo, dP.unoccupied[-1].num)
		(disk.patches).append(p)
		dP.unoccupied.pop()
		dP.usedBlocks += p.num 
		Patch_create(id,numBlocks-p.num)
	else:
		index = (l[0])[0]
		patchblkNo = l[0][1].blkNo
		patchNum = l[0][1].num
		(disk.patches).append(dP.Patch(patchblkNo,numBlocks))
		if (patchNum == numBlocks):
			dP.unoccupied.pop(index)
		else:
			currentvalue = patchNum - numBlocks
			while index > 0 and dP.unoccupied[index-1].num > currentvalue:
				dP.unoccupied[index].blkNo = dP.unoccupied[index-1].blkNo
				dP.unoccupied[index].num = dP.unoccupied[index-1].num
				index -= 1
			dP.unoccupied[index].blkNo = patchblkNo + numBlocks
			dP.unoccupied[index].num = currentvalue
		dP.usedBlocks += numBlocks

def getVirtualDiskNo(diskPatches, blkNo):
	total_blocks = 0
	i = 0
	while (diskPatches[i].num + total_blocks < blkNo+1):
		total_blocks += diskPatches[i].num
		i += 1
	return diskPatches[i].blkNo + blkNo - total_blocks

def DB_read(id, blkNo):
	if not dP.diskMap.has_key(id):
		raise Exception("Error : Invalid disk id")
	
	disk = dP.diskMap[id]
	if disk.numBlocks < blkNo+1:
		raise Exception("Error : Invalid block number")
	
	print "Reading disk block..."
	# path no known.
	print "Virtual disk no : ", getVirtualDiskNo(disk.patches, blkNo)
	return dP.PB_read(getVirtualDiskNo(disk.patches, blkNo))

def DB_write(id, blkNo, blkInfo):
	if not dP.diskMap.has_key(id):
		raise Exception("Error : Invalid disk id")
	
	disk = dP.diskMap[id]
	if disk.numBlocks < blkNo+1:
		raise Exception("Error : Invalid block number")
	
	print "Finding disk block..."
	print "Virtual disk no : ", getVirtualDiskNo(disk.patches, blkNo)
	dP.PB_write(getVirtualDiskNo(disk.patches, blkNo), blkInfo)
	print "Written disk block..."

def DB_read_replica(id, blkNo):
	if not dP.diskMap.has_key(id):
		raise Exception("Error : Disk does not exist")

	disk = dP.diskMap[id]
	if disk.numBlocks < blkNo+1:
		raise Exception("Error : Invalid block number")
	
	# random no in 1 to 100.
	print "Reading disk block..."
	if random.randint(1, 100) < 10:
		# assuming replica always exists : ERROR?
		print "Read error!"
		if (len(dP.unoccupied)==0):
			raise Exception("Error : Replica cannot be made")
		else:
			newReplicablkNo = dP.unoccupied[0].blkNo
			if (dP.unoccupied[0].num == 1):
				dP.unoccupied.pop(0)
			else:
				dP.unoccupied[0].num -= 1
				dP.unoccupied[0].blkNo += 1
			dP.usedBlocks += 1

			patches_new = []
			virt_original = getVirtualDiskNo(disk.patches, blkNo)
			virt_replica = dP.getBlockReplica(virt_original)
			virt_new_replica = newReplicablkNo

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
		ans = dP.PB_read(getVirtualDiskNo(disk.patches, blkNo))
	return ans	

def DB_write_replica(id, blkNo, blkInfo):
	if not dP.diskMap.has_key(id):
		raise Exception("Error : Disk does not exist")

	disk = dP.diskMap[id]
	if disk.numBlocks < blkNo+1:
		raise Exception("Error : Invalid block number")

	print "Finding disk block..."
	virtual_blkNo = getVirtualDiskNo(disk.patches, blkNo)
	dP.PB_write(virtual_blkNo, blkInfo)
	delta = disk.numBlocks/2
	block_replica_disk = (blkNo + delta) if blkNo < delta else (blkNo - delta)
	virtual_replica_blkNo = getVirtualDiskNo(disk.patches, block_replica_disk)
	curr_replica = dP.getBlockReplica(virtual_blkNo)
	if curr_replica == -1 or curr_replica != virtual_replica_blkNo:
		dP.setBlockReplica(virtual_blkNo, virtual_replica_blkNo)
		dP.setBlockReplica(virtual_replica_blkNo, virtual_blkNo)

	print "Virtual replica block no : ", str(dP.getBlockReplica(virtual_blkNo))
	dP.PB_write(dP.getBlockReplica(virtual_blkNo), blkInfo)
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
