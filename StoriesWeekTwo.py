import datetime, random
from Schema import createSchema
from UserHelpers import existUser, validUser, writeUser, changePassword
from DonationHelpers import addDonation, deleteDonation, editDonation, addItemByManual, addItemByBarcode, getProviderPending, getReceiverPending, getReceiverComplete, getUnclaimed, getDonationItems, claimDonation, unclaimDonation, completeDonation, existDonation, existItem, existBarcode, addBarcode

# FUNCTIONS:
# printDonation
# printDonationItems(db, did) - Print a donation's contents
# addDonationRandom(db, pid, rid, items, minCount, maxCount) - Add a random donation
# editDonationRandom(db, did, dFlag): - Update/Delete a random item in a donation


# USER STORY: 'AS A PROVIDER, I CAN EDIT MY PENDING DONATION PACKAGES'
def storyProviderEditPending(db, test, story, items, pid):
	printHeader(story) 

	# Add five randomized donations and print the contents of the first
	dids = [] 
	for i in range (5):	dids.append(addDonationRandom(db, pid, None, items, 5, 7))
	did = dids[0]
	print('DONATION {0} ITEMS'.format(did).center(80))
	itemList = getDonationItems(db, did)	
	printDonationItems(itemList)
	print('')

	# Update a random item count in first donation and print result
	iid = editDonationRandom(db, test, did, False)
	if iid < 1:
		print('ITEM EDIT FAILED: MODIFY COUNT'.center(80))
	else:
		print('DONATION {0} ITEMS (modified item {1} count)'.format(did, iid).center(80))
		itemList = getDonationItems(db, did)	
		printDonationItems(itemList)
	print('')

	# Delete a random item in first donation and print result
	iid = editDonationRandom(db, test, did, True) # Delete a random item
	if iid < 1:
		print('ITEM EDIT FAILED: DELETE ITEM'.center(80))
	else:
		print('DONATION {0} ITEMS (deleted item {1})'.format(did, iid).center(80))
		itemList = getDonationItems(db, did)	
		printDonationItems(itemList)


# USER STORY: 'AS A PROVIDER, I CAN DELETE A PENDING PACKAGE'
def storyProviderDeletePending(db, test, story, items, pid):
	printHeader(story)
	
	# Record test, initializing key if necessary
	testFunc = 'getProviderPending'
	if testFunc in test.keys(): test[testFunc][0] += 1 # Increment test count
	else: test[testFunc] = [1, 0] # Initialize to one test

	# Add and print five randomized donations,
	dids = [] 
	for i in range (5):	dids.append(addDonationRandom(db, pid, None, items, 5, 7))
	did = dids[0]
	print('PENDING DONATION PACKAGES'.center(80))
	dList = getProviderPending(db, pid)
	if dList != testGPPending(db, pid): test[testFunc][1] += 1 # record failure
	printDonation(dList)

	# Choose one donation at random and print contents
	did = dList[random.randint(0, len(dList)-1)][0]
	itemList = getDonationItems(db, did)
	print('')
	print('DONATION {0} ITEMS'.format(did).center(80))
	printDonationItems(itemList)
	print('')

	# Record test, initializing key if necessary
	testFunc = 'deleteDonation'
	if testFunc in test.keys(): test[testFunc][0] += 1 # Increment test count
	else: test[testFunc] = [1, 0] # Initialize to one test

	# Attempt to delete donation chosen in previous block, print results
	if not deleteDonation(db, did): 
		test[testFunc][1] += 1 # Record failure
		print('FAILED TO REMOVE DONATION {0}'.format(did).center(80))
	else:  
		print('DELETED DONATION {0}'.format(did).center(80))
	testFunc = 'getProviderPending' # Reset testFunc for new test
	test[testFunc][0] += 1 # Increment test count
	dList = getProviderPending(db, pid)
	if dList != testGPPending(db, pid): test[testFunc][1] += 1 # record failure
	printDonation(dList)
	itemList = getDonationItems(db, did)
	print('')
	print('DONATION {0} ITEMS'.format(did).center(80))
	printDonationItems(itemList)


# USER STORY: AS A RECEIVER, I CAN SEE UNCLAIMED DONATION PACKAGES'
def storyReceiverSeeUnclaimed(db, test, story):
	printHeader(stories[3])
	print('UNCLAIMED DONATION PACKAGES'.center(80))
	dList = getUnclaimed(db)
	printDonation(dList)


# USER STORY: AS A RECEIVER, I CAN SEE MY PENDING DONATION PACKAGES
def storyReceiverSeePending(db, test, story, rid):
	printHeader(story)

	# Get random indices for half of unclaimed donations
	dList = getUnclaimed(db)
	indices = []
	for i in range (len(dList)//2):
		while True:
			newIndex = random.randint(0, len(dList)-1)
			if newIndex not in indices:
				indices.append(newIndex)
				break

	# Record test, initializing key if necessary
	testFunc = 'claimDonation'
	if testFunc in test.keys(): test[testFunc][0] += 1 # Increment test count
	else: test[testFunc] = [1, 0] # Initialize to one test

	# Claim donations and build string
	claim = 'CLAIMING DONATION PACKAGES'
	indices.sort()
	for d in indices : 
		if d is not indices[0]: claim += ','
		claim += ' {0}'.format(dList[d][0])	
		if not claimDonation(db, dList[d][0], rid): test[testFunc][1] += 1 # Record failure
	print('{0}'.format(claim).center(80))
	print('')
	
	# Record test, initializing key if necessary
	testFunc = 'getReceiverPending'
	if testFunc in test.keys(): test[testFunc][0] += 1 # Increment test count
	else: test[testFunc] = [1, 0] # Initialize to one test

	# Print all claimed donations
	print('PENDING DONATION PACKAGES'.center(80))
	dList = getReceiverPending(db, rid)
	if dList != testGRPending(db, rid): test[testFunc][1] += 1 # record failure
	printDonation(dList)
	

# USER STORY: AS A RECEIVER, I CAN CANCEL MY CLAIM TO PICK UP A DONATION PACKAGE
def	storyReceiverCancelClaim(db, test, story, rid):
	printHeader(story)
	
	# Record test, initializing key if necessary
	testFunc = 'unclaimDonation'
	if testFunc in test.keys(): test[testFunc][0] += 1 # Increment test count
	else: test[testFunc] = [1, 0] # Initialize to one test
	
	# Record test, initializing key if necessary
	testFunc = 'getReceiverPending'
	if testFunc in test.keys(): test[testFunc][0] += 1 # Increment test count
	else: test[testFunc] = [1, 0] # Initialize to one test

	# Get all claimed, cancel one, print result
	dList = getReceiverPending(db, rid)
	if dList != testGRPending(db, rid): test[testFunc][1] += 1 # record failure
	targetIndex = random.randint(0, len(dList)-1)
	target = dList[targetIndex]
	print('CANCELING CLAIM TO DONATION PACKAGE {0}'.format(target[0]).center(80))
	if not unclaimDonation(db, target[0], rid): test[testFunc][1] += 1 # Record failure

	# Print updated list of claimed donations
	print('')
	print('PENDING DONATION PACKAGES'.center(80))
	test[testFunc][0] += 1 # record test
	dList = getReceiverPending(db, rid)
	if dList != testGRPending(db, rid): test[testFunc][1] += 1 # record failure
	printDonation(dList)
	

# USER STORY: AS A RECEIVER, I CAN SEE MY PAST DONATION PACKAGES
def storyReceiverSeePast(db, test, story, rid):
	printHeader(story)
		
	# Record test, initializing key if necessary
	testFunc = 'getReceiverComplete'
	if testFunc in test.keys(): test[testFunc][0] += 1 # Increment test count
	else: test[testFunc] = [1, 0] # Initialize to one test

	# Print empty past donation list
	print('PAST DONATION PACKAGES'.center(80))
	dList = getReceiverComplete(db, rid)
	if dList != testGRComplete(db, rid): test[testFunc][1] += 1 # record failure
	printDonation(dList)	
	print('')
	
	# Record test, initializing key if necessary
	testFunc = 'getReceiverPending'
	if testFunc in test.keys(): test[testFunc][0] += 1 # Increment test count
	else: test[testFunc] = [1, 0] # Initialize to one test

	# Complete a random claimed donation	
	dList = getReceiverPending(db, rid)
	if dList != testGRPending(db, rid): test[testFunc][1] += 1 # record failure
	targetIndex = random.randint(0, len(dList)-1)
	target = dList[targetIndex][0]
	print('COMPLETING DONATION {0}'.format(target).center(80))
	completeDonation(db, target)
	print('')

	# Print nonempty past donation list
	print('PAST DONATION PACKAGES'.center(80))
	test[testFunc][0] += 1 # Increment test count
	dList = getReceiverComplete(db, rid)
	if dList != testGRComplete(db, rid): test[testFunc][1] += 1 # record failure
	printDonation(dList)
	print('')


# INITIALIZATION
# populate users fills the users table
def populateUsers(db, parents, users, perms, pwd):

	# Build user table against params
	for ppid, uid, perm, wd in zip(parents, users, perms, pwd):
		writeUser(db, ppid, uid, perm, wd)


# Syntax: printDonation(<donation_list>)	
def	printDonation(donations):

	labels = ['did','provider','receiver','created','completed']
	columns = [7, 13, 13, 25, 25]

	if donations is []:
		print('No donations found.')
	for i in range (len(labels)): print('{0}'.format(labels[i]).ljust(columns[i]), end='')
	print('')
	for i in donations:
		for j in range(len(i)):
			print('{0}'.format(i[j]).ljust(columns[j]), end='')
		print('')					


# Function printDonationItems sends a donation's contents to standard output
def	printDonationItems(items):

	labels = ['iid','did','barcode','title','count','units']	
	columns = [7, 7, 20, 25, 10, 10]

	if items is []:
		print('No donation found.')
	else:
		for i in range (len(labels)): print('{0}'.format(labels[i]).ljust(columns[i]), end='')
		print('')
		for i in items:
			for j in range(len(i)):
				print('{0}'.format(i[j]).ljust(columns[j]), end='')
			print('')					



# Function: addDonationRandom creates a randomized donation with item count in [low, high]
# Syntax: addDonationRandom(<connection>, <provider_id>, <receiver_id|None>, <item_list>, <low>, <high>) 
# Returns donation id
def addDonationRandom(db, pid, rid, items, minCount, maxCount):

	did = addDonation(db, pid, rid) #Add an empty donation

	# Ensure count args are in bounds
	if minCount < 1 : minCount = 1
	if maxCount > len(items) : maxCount = len(items)

	# Generate random number of items in arg range
	count = random.randint(minCount, maxCount)

	# Choose $count unique items from item list
	indexList = []
	chosenItems = []
	for i in range(count):
		while True:
			index = random.randint(0, len(items)-1)
			if index not in indexList: break		
		indexList.append(index)
		aList = items[index][:]
		aList.append(random.randint(1, 50))
		aList.append(did)
		aTuple = tuple(aList)
		chosenItems.append(aTuple)

	c = db.cursor()
	c.executemany('''INSERT INTO items(barcode, title, units, count, did) VALUES(?,?,?,?,?)''', chosenItems) 
	db.commit()
	c.close()
	return did


# Function: editDonationRandom edits a random item in parameter donation
# Syntax: editDonationRandom(<connection>, <test_dict>, <donation_id>, <delete_flag>)
# Returns: affected item id if successful, else -1
# Note: if deleteflag is True, item is deleted. Otherwise count is updated.
def editDonationRandom(db, test, did, dFlag): # Update a random item
	
	items = getDonationItems(db, did)
	target = items[random.randrange(0, len(items))]
	iid = target[0]
	
	# Record test, initializing key if necessary
	testFunc = 'editDonation'
	if testFunc in test.keys(): test[testFunc][0] += 1 # Increment test count
	else: test[testFunc] = [1, 0]

	if dFlag:
		result = editDonation(db, did, iid, 0)	
	else:
		icount = target[4]
		while True:
			newCount = random.randint(1, 50)
			if newCount is not icount: break
		result = editDonation(db, did, iid, newCount)	
	if result:
		return iid
	else:
		test[testFunc][1] += 1 # Record failure
		return -1


def printHeader(header):
	eq = "=" * 80
	print('\n{0}'.format(eq))
	print('{0}'.format(header).center(80))
	print('{0}\n'.format(eq))


def printResults(test):
	for key in test:
		if test[key][0] > 0:
			if test[key][1] > 0:
				print('FAIL: {0} failed {1} of {2} tests.'.format(key, test[key][1], test[key][0]))
			else:
				print('PASS: {0} passed all tests'.format(key))


# Tests for donation getter functions
def testGPPending(db, uid):
	c = db.cursor()
	c.execute('''SELECT * FROM donations where provider = ? AND completed = ?''', (uid, 0))
	result = c.fetchall()
	c.close()
	return result

def testGRPending(db, uid):
	c = db.cursor()
	c.execute('''SELECT * FROM donations where receiver = ? AND completed = ?''', (uid, 0))
	result = c.fetchall()
	c.close()
	return result

def testGRComplete(db, uid):
	c = db.cursor()
	c.execute('''SELECT * FROM donations where receiver = ? AND completed != ?''', (uid, 0))
	result = c.fetchall()
	c.close()
	return result


if __name__ == '__main__':

	random.seed() #Randomize RNG

	# key is function, value is [test_count, failure_count]
	test = dict() # For test results

	# Headers
	stories = [
		'FUNCTION TEST RESULTS',
		'AS A PROVIDER, I CAN EDIT MY PENDING DONATION PACKAGES',
		'AS A PROVIDER, I CAN DELETE A PENDING PACKAGE',
		'AS A RECEIVER, I CAN SEE UNCLAIMED DONATION PACKAGES',
		'AS A RECEIVER, I CAN SEE MY PENDING DONATION PACKAGES',
		'AS A RECEIVER, I CAN CANCEL MY CLAIM TO PICK UP A DONATION PACKAGE',
		'AS A RECEIVER, I CAN SEE MY PAST DONATION PACKAGES',
	]

	# Initialization values for users table
	parents = ['admin','admin','admin','P_Org','P_Org','R_Org','R_Org'] # Parent IDs
	users = ['admin','P_Org','R_Org','P_Usr_1','P_Usr_2','R_Usr_1','R_Usr_2'] # User IDs
	perms = [0b1111,0b110,0b101,0b10,0b10,0b1,0b1] # Permission bits
	pwds = ['admin','123456','Password','hunter2','iloveyou','monkey','letmein'] # Passwords

	# Intialization values item and barcodes
	items = [
		["945141", "Alfalfa, Sprouts", "oz"],
		["37013", "Artichoke", "each"],
		["01153", "Arugula, Baby", "lb"],
		["40808", "Asparagus, Greens", "lb"],
		["30793", "Asparagus, Purple", "lb"],
		["45292", "Beans, Lima", "lb"],
		["45391", "Beets, Bunch", "each"],
		["945455", "Bok Choy", "lb"],
		["845472", "Broccoli", "lb"],
		["45506", "Brussels Sprouts", "lb"],
		["079893402826", "Kale", "lb"],
		["011535501924", "Carrots Bunch", "bunch"],
		["33206", "Cauliflower", "each"],
		["40709", "Celery, Bunch", "each"],
		["021130285006", "Chard, Rainbow", "lb"],
		["33985", "Chick Peas", "lb"],
		["033383675008", "Mushrooms", "lb"],
		["033383605005", "Onions, Green", "each"],
		["946759", "Peas, Black-Eyed", "lb"],
		["846745", "Peas, Green", "lb"],
		["3128", "Potato, Purple", "each"],
		["4073", "Potato, Red", "each"],
		["4725", "Potato, Russet", "each"],
		["33329", "Spinach, Baby", "lb"],
		["31431", "Squash, Acorn", "each"],
		["848121", "Turnip, White", "lb"],
		["40952", "Turnip, Yellow", "lb"],
		["48279", "Yams", "each"]
	]

	# SET-UP: Generate tables & populate users table
	db = createSchema()
	populateUsers(db, parents, users, perms, pwds)

	# STORY: Provider can edit pending
	storyProviderEditPending(db, test, stories[1], items, 'P_Usr_1')

	# STORY: Provider can delete pending
	storyProviderDeletePending(db, test, stories[2], items, 'P_Usr_2')

	# STORY: Receiver can see unclaimed donations
	storyReceiverSeeUnclaimed(db, test, stories[3])

	# STORY: Receiver can see pending donations
	storyReceiverSeePending(db, test, stories[4], 'R_Usr_1')
	
	# STORY:Receiver can cancel claims
	storyReceiverCancelClaim(db, test, stories[5], 'R_Usr_1')

	# STORY: Receiver can see past donations
	storyReceiverSeePast(db, test, stories[6], 'R_Usr_1')

	# RESULTS: Print test results
	printHeader(stories[0])
	printResults(test)

	# Shut It Down
	db.close()
