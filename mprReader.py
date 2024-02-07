import pandas as pd
from galvani.BioLogic import MPRfile

def sanitize_labels(label):
	return label.split('/')[0].lower().lstrip('-').translate(dict.fromkeys(map(ord, " ,|()-"),'_')).rstrip('_')

def mprReader(filename, cycle=0):
	# Import data using MPRfile and flatten 
	mpr = MPRfile(filename)
	data = mpr.data
	data.flatten()

	# produce Pandas dataframe
	x = []
	for row in data:
		x.append(list(row))
	df = pd.DataFrame(x,columns=['Flags', 'time', 'control', 'Eve', 'I', 'cycle_number', '(Q-Q0)/C', 'I_Range', 'Ecv'])

	df_reduced = df.loc[df['cycle_number'] == cycle]
	return df_reduced

def mprReader_full(filename):
	# Import data using MPRfile and flatten
	"""
	mpr = MPRfile(filename)
	data = mpr.data
	data.flatten()

	# produce Pandas dataframe
	x = []
	for row in data:
		x.append(list(row))
	df = pd.DataFrame(x,columns=['Flags', 'time', 'control', 'Eve', 'I', 'cycle_number', '(Q-Q0)/C', 'I_Range', 'Ecv'])
	"""
	mpr = MPRfile(filename)
	df = pd.DataFrame(mpr.data)
	df.columns = [sanitize_labels(label) for label in df.columns]

	return df

