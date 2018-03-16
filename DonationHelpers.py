import datetime
# DonationHelpers.py implements helper functions for manipulating the item table

# Functions:
# addDonation()
# deleteDonation()
# editDonation()
# addItemByManual()
# addItemByBarcode()
# getProviderPending()
# getProviderComplete()
# getReceiverPending()
# getReceiverComplete()
# viewDonationItems()
# claimDonation()
# unclaimDonation()
# completeDonation()
# addBarcode()
# existBarcode() 
# existItem() 
# existDonation() 

# Function addDonation()
# Purpose: Creates a new donation in donation table
# Syntax: addDonation(<connection>, <provider>, <receiver>)
# Returns: donation.id if donation is successfully created, else -1
# Note: receiver should be None unless receiver is known in advance
def addDonation(db, provider, receiver):
	
	c = db.cursor()
	now = datetime.datetime.now().replace(microsecond=0)
	
	if receiver is None:	
		# If no receiver specified
		c.execute('''INSERT INTO donations(provider, created, completed) VALUES(?,?,?)''', (provider, now, 0))
	else:	
		# If receiver specified
		c.execute('''INSERT INTO donations(provider, receiver, created, completed) VALUES(?,?,?,?)''', (provider, receiver, now, 0))
	result = c.lastrowid
	db.commit()
	c.close()

	if result is not None:	# Per https://www.python.org/dev/peps/pep-0249/#lastrowid no insert returns None
		return result
	else: 
		return -1

# Function deleteDonation()
# Purpose: Removes a donation and all associated items from the database
# Syntax: deleteDonation(<connection>, <donation_id>)
# Returns 0 if successful, 1 on error
def deleteDonation(db, did):

	c = db.cursor()

	# Delete donation and items
	c.execute('''DELETE FROM donations WHERE id = ?''', (did,))
	c.execute('''DELETE FROM items WHERE did = ?''', (did,))

	# Confirm donation deletion
	c.execute('''SELECT * FROM donations WHERE id = ?''', (did,))
	result = c.fetchall()
	success = True if len(result) is 0 else False
	# Confirm item deletion
	c.execute('''SELECT * FROM items WHERE did = ?''', (did,))
	result = c.fetchall()
	success = True if success and len(result) is 0 else False

	c.close()
	return success

# Function editDonation()
# Purpose: Updates an item in a donation to count if count > 0 or deletes item f count is 0
# Syntax: editDonation(<connection>, <donation_id>, <item_id>, <count>)
def editDonation(db, did, iid, count):
	
	# Fail if item doesn't exist as part of donation
	c = db.cursor()
	c.execute('''SELECT * FROM items WHERE id = ? AND did = ?''', (iid, did))
	item = c.fetchone()
	if item is None: return False

	# If count arg isn't zero, build update count expression/args
	if count is not 0:
		SQLquery = "UPDATE items SET count = ? WHERE id = ? AND did = ?"
		SQLargs = (count, iid, did)
	# If count arg is zero, build delete item expression/args
	else:
		SQLquery = "DELETE FROM items WHERE id = ? and DID = ?"
		SQLargs = (iid, did)

	# Execute expression and check for success
	c.execute(SQLquery, SQLargs)
	c.execute('''SELECT * FROM items WHERE id = ? AND did = ?''', (iid, did))
	result = c.fetchone()
	c.close()
	newCount = result[4] if result is not None else 0

	if (count is 0 and result is None) or (count is not 0 and newCount is count):
		return True
	else:
		return False


# Function addItemByManual()
# Purpose: add a new item to the items table without barcode
# Syntax: addItemByManual(<connection>, <donation_id>, <title>, <count>, <unit_type>)
# Returns: item.id if item is successfully created, else -1
# Note: Fails if invalid donation_id
def addItemByManual(db, did, title, count, unit):

	if not existDonation(db, did):
		return -1

	# Test for matching item in table
	c = db.cursor()
	c.execute('''SELECT id, count FROM items WHERE did=? AND title=? AND units=?''', (did, title, unit))
	result = c.fetchone()

	# Item in table: add count to existing item
	if result is not None: 
		newCount = result[1] + count
		c.execute('''UPDATE items SET count = ? WHERE id = ?''', (newCount, result[0]))

	# Item not in table: add new item to table
	else:
		c.execute('''INSERT INTO items(did, title, count, units) VALUES(?,?,?,?)''', (did, title, count, unit))

	result = c.lastrowid
	db.commit()
	c.close()

	if result is not None:	# Per https://www.python.org/dev/peps/pep-0249/#lastrowid no insert returns None
		return result
	else: 
		return -1


# Function addItemByBarcode()
# Purpose: add a new item to the items table using barcode
# Syntax: addItemByBarcode(<connection>, <donation_id>, <barcode>, <count>)
# Returns: item.id if item is successfully created, else -1
# Note: Fails if invalid donation_id or barcode. Defaults to 1 if arg count < 1 for autoscan.
def addItemByBarcode(db, did, code, count):

	if not existDonation(db, did):
		return -1

	if not existBarcode(db, code):
		return -1

	# Permit negative count for quick scanning: 1 code == 1 count
	if count < 1:
		count = 1

	# Get barcode data
	c = db.cursor()
	c.execute('''SELECT title, units FROM barcodes WHERE code = ?''', (code,))
	codeData = c.fetchone()

	# Test for matching item in table
	c.execute('''SELECT id, count FROM items WHERE did=? AND title=? AND units=?''', (did, codeData[0], codeData[1]))
	result = c.fetchone()

	# Item in table: add count to existing item
	if result is not None: 
		newCount = result[1] + count
		c.execute('''UPDATE items SET count = ?, barcode = ? WHERE id = ?''', (newCount, code, result[0]))

	# Item not in table: add new item to table
	else:
		c.execute('''INSERT INTO items(did, barcode, title, count, units) VALUES(?,?,?,?,?)''', (did, code, codeData[0], count, codeData[1]))

	result = c.lastrowid
	db.commit()
	c.close()

	if result is not None:	# Per https://www.python.org/dev/peps/pep-0249/#lastrowid no insert returns None
		return result
	else: 
		return -1

# Function _getDonations gets donations as defined by the two-bit string types.
# types LSD is pending(0)/completed(1) | types MSD is provider(0)/receiver(1)
def _getDonations(db, uid, types):

	# Decode types bit string
	role = 'receiver' if (0b10 & types == 0b10) else 'provider'
	status = 'completed' if (0b1 & types == 0b1) else 'pending'

	# Build SQL query
	SQLquery = 'SELECT * FROM donations WHERE'
	SQLquery = ''.join([SQLquery, ' receiver = ?']) if role is 'receiver' else ''.join([SQLquery, ' provider = ?'])
	SQLquery = ''.join([SQLquery, ' AND completed != 0']) if status == 'completed' else ''.join([SQLquery, ' AND completed = 0'])
	
	# Get and return rows
	c = db.cursor()
	c.execute(SQLquery, (uid,))
	result = c.fetchall()
	c.close()
	return result


# Function getProviderPending returns all pending donations by provider
def getProviderPending(db, uid):
	return _getDonations(db, uid, 0)


# Function getProviderComplete returns all completed donations by provider
def getProviderComplete(db, uid):
	return _getDonations(db, uid, 1)


# Function getReceiverPending returns all pending donations by receiver
def getReceiverPending(db, uid):
	return _getDonations(db, uid, 2)


# Function getReceiverComplete returns all completed donations by provider
def getReceiverComplete(db, uid):
	return _getDonations(db, uid, 3)


# Function getUnclaimed returns all unclaimed packages
def getUnclaimed(db):
	return _getDonations(db, 'pending', 2)


# Function getDonationItems()
# Purpose: returns a list of items by donation id
# Syntax: getDonationItems(<connection>, <donation_id>)
# Returns: A list of all matching items, or an empty list if none found.
def getDonationItems(db, did):

	c = db.cursor()
	c.execute('''SELECT * from items WHERE did = ?''', (did,))
	result = c.fetchall()
	c.close()
	return result


# Function claimDonation()
# Purpose: assign a receiver to an unclaimed donation
# Syntax: claimDonation(<connection>, <donation_id>, <recevier_uid>)
# Returns: On successful update to donation receiver field returns True, else False
def claimDonation(db, did, rid):

	final = False
	c = db.cursor()
	c.execute('''SELECT receiver, completed FROM donations WHERE id = ?''', (did,))
	result = c.fetchone()

	if result is not None:
		if (result[0] == 'pending') and (result[1] == 0):
			c.execute('''UPDATE donations SET receiver = ? WHERE id = ?''', (rid, did))
			c.execute('''SELECT receiver FROM donations WHERE id = ?''', (did,))
			result = c.fetchone()
			if result is not None:
				if result[0] == rid:
					final = True
	db.commit
	c.close()
	return final


# Function unclaimDonation()
# Purpose: remove a receiver from a claimed donation
# Syntax: unclaimDonation(<connection>, <donation_id>, <recevier_uid>)
# Returns: On successful update to donation receiver field returns True, else False
def unclaimDonation(db, did, rid):


	final = False
	c = db.cursor()
	c.execute('''SELECT receiver, completed FROM donations WHERE id = ?''', (did,))
	result = c.fetchone()

	if result is not None:
		if (result[0] == rid) and (result[1] == 0):
			c.execute('''UPDATE donations SET receiver = ? WHERE id = ?''', ('pending', did))
			c.execute('''SELECT receiver FROM donations WHERE id = ?''', (did,))
			result = c.fetchone()
			if result is not None:
				if result[0] == 'pending':
					final = True
	db.commit
	c.close()
	return final


# Function completeDonation()
# Purpose: Update completed field for a donation to current datetime
# Syntax: completeDonation(<connection>, <donation_id>)
# Returns: On successful update returns True, else False
def completeDonation(db, did):

	final = False
	c = db.cursor()
	c.execute('''SELECT completed FROM donations WHERE id = ?''', (did,))
	result = c.fetchone()

	if result is not None:
		if result[0] is 0:
			now = datetime.datetime.now().replace(microsecond=0)
			c.execute('''UPDATE donations SET completed = ? WHERE id = ?''', (now, did))
			c.execute('''SELECT completed FROM donations WHERE id = ?''', (did,))
			result = c.fetchone()
			if result is not None:
				if result[0] is now: final = True
	db.commit
	c.close()
	return final


# Function addBarcode()
# Purpose: insert a new barcode entry into the barcodes table
# Syntax: addBarcode(<connection>, <barcode>, <title>, <units>)
# Returns: True if item inserted, else False
def addBarcode(db, code, title, units):

	# Check for existing barcode
	c = db.cursor()
	c.execute('''SELECT * FROM barcodes WHERE code = ?''', (code,))
	if c.fetchone() is not None:
		c.close()
		return False

	# Add barcode 
	c.execute('''INSERT into barcodes(code, title, units) VALUES(?,?,?)''', (code, title, units))
	
	# Test success
	c.execute('''SELECT * FROM barcodes WHERE code = ?''', (code,))
	result = c.fetchone()
	db.commit
	c.close()

	if result is not None:
		return True
	else:
		return False


# Function existBarcode() 
# Purpose: Check for barcode in barcode table
# Syntax: existBarcode(<connection>, <barcode_to_check>)
# Returns: True if barcode exists / False if barcode does not exist
# Note: code is unique column, so 0 and 1 are only lengths possible
def existBarcode(db, code):
	
	c = db.cursor()
	c.execute('''SELECT code FROM barcodes WHERE code=?''', (code,))
	result = c.fetchone()
	c.close()

	if result is not None:
		return True
	else:
		return False


# Function existItem() 
# Purpose: Check for item in items table
# Syntax: existItem(<connection>, <item_id_to_check>)
# Returns: True if item exists / False if item does not exist
# Note: id is primary key, so 0 and 1 are only lengths possible
def existItem(db, iid):
	
	c = db.cursor()
	c.execute('''SELECT id FROM items WHERE id=?''', (iid,))
	result = c.fetchone()
	c.close()

	if result is not None:
		return True
	else:
		return False


# Function existDonation() 
# Purpose: Check for donation in donations table
# Syntax: existDonation(<connection>, <donation_id_to_check>)
# Returns: True if donation exists / False if donation does not exist
# Note: id is primary key, so 0 and 1 are only lengths possible
def existDonation(db, did):
	
	c = db.cursor()
	c.execute('''SELECT id FROM donations WHERE id=?''', (did,))
	result = c.fetchone()
	c.close()

	if result is not None:
		return True
	else:
		return False
