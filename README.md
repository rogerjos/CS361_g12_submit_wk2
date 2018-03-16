The demonstration for week two user stories is in StoriesWeekTwo.py and requires Python 3 to run.

To run, place Schema.py, UserHelpers.py, DonationHelpers.py, and StoriesWeekTwo.py into a directory and run with "Python3 StoriesWeekTwo.py"



		Module Contents:

Schema.py contains a sqlite3 implementation of the following tables:
	users(pid, perms, uid, hash)
	donations(id, provider, receiver, created, completed)
	items(id, did, barcode, title, count, units)
	barcodes(code, title, units)

UserHelpers.py contains the following user-level functions: 
	validUser() tests a uid/pwd pair for validity
	changePassword() changes a user's password if the old password is known
	writeUser() writes to user table, creating or updating record if sufficient permissions
	existUser() tests for a user's existence
	isAdmin() / isOrg() / isProvider() / isReceiver() return T/F based on uid permissions

DonationHelpers.py contains the following donation-level functions:
	addDonation() adds a new donation to the donation table
	deleteDonation() removes a donation from the donation table and all associated items from item table
	editDonation() changes the count of an item in a donation or deletes the item
	addItemByManual() adds an item by user-supplied values
	addItemByBarcode() adds an item by barcode values
	getProviderPending() gets all incomplete donations from provider
	getProviderComplete() gets all complete donations from provider
	getReceiverPending() gets all incomplete donations to receiver
	getReceiverComplete() gets all complete donations to receiver
	getUnclaimed() gets all incomplete donations with no receiver
	getDonationItems() gets all items in a donation
	claimDonation() adds a receiver to a donation
	unclaimDonation() removes a receiver from a donation
	completeDonation() adds a completion datetime to a pending donation
	addBarcode() adds a bar code to the bard code table
	existBarcode() / existItem() / existDonation() 

StoriesWeekTwo.py contains the following testing and demonstration functions:
	storyProviderEditPending() demonstrates provider editing donation packages
	def storyProviderDeletePending() demonstrates provider deleting pending packages
	def storyReceiverSeeUnclaimed() demonstrates receiver viewing unclaimed packages
	def storyReceiverSeePending() demonstrates receiver viewing their own claimed packages
	def	storyReceiverCancelClaim() demonstrates receiver canceling their claim to a pending package
	def storyReceiverSeePast() demonstrates receiver viewing their own complete packages
	def populateUsers() builds user table
	def	printDonation() prints a donation list 
	def	printDonationItems() prints an item list
	def addDonationRandom() adds a randomized donation for testing
	def editDonationRandom() edits a random item for testing
	def printHeader() prints a decriptive header
	def printResults() prints test results
	def testGPPending() tests getProviderPending()
	def testGRPending() tests GetReceiverPending()
	def testGRComplete() tests GetReceiverComplete()
