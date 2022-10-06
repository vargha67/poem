import os, sys, math, json
import pandas as pd



def find_images_supporting_pattern (image_concepts, pattern):

	df = image_concepts.copy()
	for attr in list(pattern.index): 
		if (attr not in meta_cols) and (pattern[attr] != -1):
			df = df[df[attr] == pattern[attr]]

	supporting_indices = list(df.index.values)
	return supporting_indices
    

def find_images_matching_pattern (image_concepts, pattern, supporting_indices=None): 

	if supporting_indices is None:
		supporting_indices = find_images_supporting_pattern(image_concepts, pattern)
	pattern_label = pattern['pred']

	matching_indices = []
	supporting_labels = list(image_concepts.iloc[supporting_indices]['pred'])

	for i,label in enumerate(supporting_labels):
		if label == pattern_label:
			matching_indices.append(supporting_indices[i])

	return matching_indices
    
    
def find_images_supporting_pattern_not_matching (image_concepts, pattern, supporting_indices=None, matching_indices=None):

	if supporting_indices is None:
		supporting_indices = find_images_supporting_pattern(image_concepts, pattern)
	if matching_indices is None:
		matching_indices = find_images_matching_pattern(image_concepts, pattern, supporting_indices)
    
	nonmatching_indices = sorted(list(set(supporting_indices) - set(matching_indices)))
	return nonmatching_indices
    
    
def find_images_matching_pattern_wrong_predicted (image_concepts, pattern, matching_indices=None):

	if matching_indices is None:
		matching_indices = find_images_matching_pattern(image_concepts, pattern)

	wrong_indices = []
	matching_concepts = image_concepts.iloc[matching_indices][['pred', 'label']]

	for i,row in matching_concepts.iterrows():
		if row['pred'] != row['label']:
			wrong_indices.append(i)

	return wrong_indices
    
    
def get_image_description (img_concepts, class_titles, target_concept=None, target_channel=None):
    
	desc = 'Predicted <em>{}</em>, Labeled <em>{}</em>'.format(class_titles[img_concepts['pred']], class_titles[img_concepts['label']])
	if target_concept is None: 
		concepts = []
		for attr in list(img_concepts.index):
			if (attr not in ['pred', 'label', 'id', 'file', 'path']) and (img_concepts[attr] == 1):
				concepts.append(attr)

		if len(concepts) > 0:
			desc += '<br/>Concepts: <em>' + ', '.join(concepts) + '</em>'
		else:
			desc += '<br/>No concepts activated'
	else:
		desc += '<br/>Concept <em>{}</em> highlighted'.format(target_concept)
		if target_channel != None:
			desc += ' (filter <em>' + str(target_channel) + '</em>)'

	return desc
    
    
def list_image_activation_images (image_fname, activations_path, target_concept=None):

	ind = image_fname.rfind('.')
	image_fname_raw = image_fname[:ind]

	activations_info = {}
	for fname in os.listdir(activations_path):
		if not fname.startswith(image_fname_raw + "_"): 
			continue

		ind = fname.rfind('.')
		ext = fname[ind:]
		if (target_concept != None) and (not fname.endswith(target_concept + ext)):
			continue

		ind = len(image_fname_raw + "_")
		ind2 = fname.rfind(ext)
		main_body = fname[ind:ind2]
		parts = main_body.split('_')
		if len(parts) != 2:
			print('Error: Name of image file {} does not include concept and channel parts: {}'.format(fname, parts), file=sys.stderr)
			continue

		channel = int(parts[0])
		concept = parts[1]
		if (target_concept != None) and (concept != target_concept):
			print('Error: Concept {} in name of file {} not matching the target concept {}'.format(concept, fname, target_concept), file=sys.stderr)
			continue

		full_path = os.path.join(activations_path, fname)
		if concept in activations_info: 
			activations_info[concept].append((channel, full_path))
		else:
			activations_info[concept] = [(channel, full_path)]

	return activations_info
    
    
def prepare_image_items_for_display (matching_image_concepts, class_titles, dataset_path=None, activations_path=None, target_concept=None):

	image_items = []
	for i, (ind, img_concepts) in enumerate(matching_image_concepts.iterrows()):
		img_item = {}
		img_label = img_concepts['label']
		img_fname = img_concepts['file']

		if target_concept is None:
			ctitle = class_titles[img_label]
			img_path = dataset_path + "/" + ctitle + "/" + img_fname
			if not os.path.exists(img_path):
				img_path = dataset_path + "/train/" + ctitle + "/" + img_fname
			img_item['path'] = img_path
			img_item['desc'] = get_image_description(img_concepts, class_titles)
			image_items.append(img_item)
		else:
			activations_info = list_image_activation_images(img_fname, activations_path, target_concept)

			if target_concept in activations_info:
				inf = activations_info[target_concept]
				item = inf[0]
				img_item['path'] = item[1]
				img_item['desc'] = get_image_description(img_concepts, class_titles, target_concept, target_channel=item[0])
				image_items.append(img_item)
			else:
				print('Error: Activations info for image {} does not include the target concept {}: {}'.format(img_fname, target_concept, activations_info), file=sys.stderr)
				continue

	return image_items
    

def extract_class_titles (dataset):
	ctitles = {}
	name_parts = dataset.split('_')
	if len(name_parts) <= 1:
		return ctitles
	
	for i,p in enumerate(name_parts[1:]):
		ctitles[i] = p
		
	return ctitles
	
	
def compute_pattern_score (row, concept_cols):

	sup = row['support']
	conf = row['confidence']
	size = 0

	for col in concept_cols:
		if row[col] != -1:
			size += 1

	score = (sup * conf) / size
	return score
    

def load_patterns(dataset, model, rule_methods, exp_min_support=None, ids_min_support=None, cart_min_samples_leaf=None, remove_inactivated_patterns=True, use_class_titles=False):

	result_path = "data/results/" + model + "_" + dataset
	
	if not os.path.exists(result_path):
		print("Directory {} of the dataset and model results not found!".format(result_path), file=sys.stderr)
		return None
	
	all_patterns_list = []
	
	if "exp" in rule_methods: 
		path = result_path + "/exp_patterns" + ('_' + str(exp_min_support) if (exp_min_support != None) else '') + ".csv"
		if not os.path.exists(path):
			print("Patterns file {} not found!".format(path), file=sys.stderr)
			return None
		
		exp_patterns = pd.read_csv(path)
		exp_patterns['method'] = 'Exp'
		all_patterns_list.append(exp_patterns)
		
	if "ids" in rule_methods:
		path = result_path + "/ids_patterns" + ('_' + str(ids_min_support) if (ids_min_support != None) else '') + ".csv"
		if not os.path.exists(path):
			print("Patterns file {} not found!".format(path), file=sys.stderr)
			return None
			
		ids_patterns = pd.read_csv(path)
		ids_patterns['method'] = 'IDS'
		all_patterns_list.append(ids_patterns)
		
	if "cart" in rule_methods:
		path = result_path + "/cart_patterns" + ('_' + str(cart_min_samples_leaf) if (cart_min_samples_leaf != None) else '') + ".csv"
		if not os.path.exists(path):
			print("Patterns file {} not found!".format(path), file=sys.stderr)
			return None
		
		cart_patterns = pd.read_csv(path)
		cart_patterns['method'] = 'CART'
		all_patterns_list.append(cart_patterns)

	all_patterns = pd.concat(all_patterns_list, ignore_index=True)
	class_titles = extract_class_titles(dataset)
	
	patterns_to_remove = []
	exp_patterns_count = 0

	for i,pattern in all_patterns.iterrows():
		if remove_inactivated_patterns:
			# Removing patterns with "no" features, because they're not very accurate and useful: 
			to_remove = False
			for attr in list(pattern.index): 
				pattern_value = pattern[attr]
				if (attr not in meta_cols) and (pattern_value == 0):
					to_remove = True
					break
					
			if to_remove:
				patterns_to_remove.append(i)
				continue

		if pattern['method'] != 'Exp':
		    continue

		# Using only the specified maximum number of Exp patterns: 
		#exp_patterns_count += 1
		#if exp_patterns_count > exp_num_patterns:
		#	patterns_to_remove.append(i)
		#	continue

		# Handling those patterns by Exp Tables which have confidence lower than 0.5 and need to be inverted to be meaningful and useful: 
#		pred = pattern['pred']
#		conf = pattern['confidence']
#		if conf < 0.5:
#			new_pred = pred
#			new_conf = conf
#			classes = list(class_titles.keys())
#			if len(classes) == 2:
#				new_pred = 1 if pred == 0 else 0
#				new_conf = 1.0 - conf
#			else:
#				# Need to find the new prediction and accurate confidence value, as there may be more than one other classes in this case: 
#				pattern_cp = pattern.copy(deep=True)
#				for c in classes:
#					if pred == c:
#						continue
#					pattern_cp['pred'] = c
#					supporting_indices = find_images_supporting_pattern(image_concepts, pattern_cp)
#					matching_indices = find_images_matching_pattern(image_concepts, pattern_cp, supporting_indices)
#					temp_conf = len(matching_indices) / len(supporting_indices)
#					if temp_conf > new_conf:
#						new_pred = c
#						new_conf = temp_conf
#		
#			all_patterns.loc[i, 'pred'] = new_pred
#			all_patterns.loc[i, 'confidence'] = new_conf

	if len(patterns_to_remove) > 0:
		all_patterns.drop(patterns_to_remove, axis=0, inplace=True)
	
	all_patterns['support'] = all_patterns['support'].round(2)
	all_patterns['confidence'] = all_patterns['confidence'].round(2)
	all_patterns['accuracy'] = all_patterns['accuracy'].round(2)
	
	if use_class_titles:
		all_patterns['pred'] = all_patterns.apply(lambda p: class_titles[p['pred']], axis=1)

	concept_cols = list(set(all_patterns.columns) - set(meta_cols))
	all_patterns['score'] = all_patterns.apply(lambda p: compute_pattern_score(p, concept_cols), axis=1)
	
	group_cols = list(set(all_patterns.columns) - set(['method']))
	all_patterns_grouped = all_patterns.groupby(group_cols, as_index=False)
	all_patterns = all_patterns_grouped.agg({'method': lambda p: ', '.join(p.unique())})
	#print('group_cols: {}'.format(group_cols), file=sys.stderr)
	#print('all_patterns_grouped.groups.keys(): {}'.format(all_patterns_grouped.groups.keys()), file=sys.stderr)
	
	all_patterns.sort_values(by=['score', 'confidence', 'support', 'accuracy', 'method'], ascending=False, inplace=True)
	all_patterns.reset_index(drop=True, inplace=True)
	all_patterns.insert(loc=0, column='index', value=(all_patterns.index + 1))
	all_patterns['score'] = all_patterns['score'].round(2)
	
	#all_patterns.to_csv('all_patterns.csv')
	
	return all_patterns	
	
	
def load_images_info (dataset, model, rule_methods, pattern_index, mode, target_concept=None, exp_min_support=None, ids_min_support=None, cart_min_samples_leaf=None):
	
	result_path = "data/results/" + model + "_" + dataset
	dataset_path = "data/datasets/" + dataset
	activations_path = result_path + "/activation_images"
	image_concepts_path = result_path + "/image_concepts.csv"
	
	if (not os.path.exists(dataset_path)) or (not os.path.exists(activations_path) or (not os.path.exists(image_concepts_path))):
		print("Either the dataset path {} or the activations path {} or the image concepts path {} not found!".format(dataset_path, activations_path, image_concepts_path), file=sys.stderr)
		return None
		
	patterns = load_patterns(dataset, model, rule_methods, exp_min_support, ids_min_support, cart_min_samples_leaf)
	if patterns is None:
		return None
	
	pattern = patterns.loc[patterns['index'] == pattern_index].iloc[0]
	if pattern is None:
		print("No pattern with index {} found among the patterns from dataset {}, model {}, and rule methods {}!".format(pattern_index, dataset, model, rule_methods), file=sys.stderr)
		return None
		
	image_concepts = pd.read_csv(image_concepts_path)
	class_titles = extract_class_titles(dataset)
		
	matched_indices = []
	if mode == 'matching':
		matched_indices = find_images_matching_pattern(image_concepts, pattern)
	
	elif mode == 'nonmatching':
		matched_indices = find_images_supporting_pattern_not_matching(image_concepts, pattern)
	
	elif mode == 'wrong':
		matched_indices = find_images_matching_pattern_wrong_predicted(image_concepts, pattern)

	matched_image_concepts = image_concepts.iloc[matched_indices].iloc[:max_images]
	image_items = prepare_image_items_for_display(matched_image_concepts, class_titles, dataset_path, activations_path, target_concept)
	
	return image_items



# Main routine: 

max_images = 50
meta_cols = ['index', 'pred', 'support', 'confidence', 'accuracy', 'method', 'score']

params = sys.argv
if len(params) < 2:
	print('Arguments not enough! {}'.format(params), file=sys.stderr)
	sys.stderr.flush()
	exit()
	
function_name = params[1]
result = None

if function_name == "load_patterns":
	if len(params) < 8:
		print('Arguments not enough for loading patterns! {}'.format(params), file=sys.stderr)
		sys.stderr.flush()
		exit()

	dataset = params[2]
	model = params[3]
	rule_methods_str = params[4]
	rule_methods = rule_methods_str.split(",")
	
	#exp_num_patterns = int(params[5]) if int(params[5]) != -1 else None
	exp_min_support = float(params[5]) if float(params[5]) != -1 else None
	ids_min_support = float(params[6]) if float(params[6]) != -1 else None
	cart_min_samples_leaf = float(params[7]) if float(params[7]) != -1 else None
	
	patterns = load_patterns(dataset, model, rule_methods, exp_min_support, ids_min_support, cart_min_samples_leaf, remove_inactivated_patterns=True, use_class_titles=True)
	if patterns is not None:
		result = patterns.to_json(orient='records')
		
elif function_name == "load_images_info":
	if len(params) < 10:
		print('Arguments not enough for loading images info! {}'.format(params), file=sys.stderr)
		sys.stderr.flush()
		exit()

	dataset = params[2]
	model = params[3]
	rule_methods_str = params[4]
	rule_methods = rule_methods_str.split(",")
	
	#exp_num_patterns = int(params[5]) if int(params[5]) != -1 else None
	exp_min_support = float(params[5]) if float(params[5]) != -1 else None
	ids_min_support = float(params[6]) if float(params[6]) != -1 else None
	cart_min_samples_leaf = float(params[7]) if float(params[7]) != -1 else None
	
	pattern_index = int(params[8])
	mode = params[9]
	target_concept = params[10] if len(params) == 11 else None
	
	image_items = load_images_info(dataset, model, rule_methods, pattern_index, mode, target_concept, exp_min_support, ids_min_support, cart_min_samples_leaf)
	if image_items is not None:
		result = json.dumps(image_items)

if result is None:
	sys.stderr.flush()
	exit()

print(result)
sys.stdout.flush()



