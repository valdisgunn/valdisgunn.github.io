'''
	Script used to generate HTML game pages for the website, starting from the corresponding JSON files.
'''

import json
import os
import re
import sys

def json_to_html(data):

	# Load HTML template from file
	template_html = ''
	print("\nLoading HTML template...")
	with open('utilities/template.html', 'r', encoding='utf-8') as html_file:
		template_html = html_file.read()

	# Load the template json file
	template_data = {}
	with open('utilities/template.json', 'r', encoding='utf-8') as json_file:
		template_data = json.load(json_file)

	# Given an attribute value of the data, returns the value (either a key or a child of a key) 
	# 	and the name of the field where it was found (same given attribute name or name of the 
	# 	parent key where it was found), or None if the field is not found.
	def get_value_from_json(data, field_name):
		# Check if the field name is in the data
		if field_name in data:
			# Field name is in the data
			if field_name is None:
				return None, None
			return data[field_name], field_name
		else:
			# Check if the field name is in any sub-field of the data
			for key in data:
				if type(data[key]) is dict:
					if field_name in data[key]:
						return data[key][field_name], key
		return None, None

	# Replace text content
	print('> Replacing text content...')
	text_placeholders = re.findall(r'\{\{\{\{[\w-]+\}\}\}\}', template_html)
	for placeholder in text_placeholders:
		field_value = placeholder[4:-4]
		data_value = get_value_from_json(data, field_value)[0]
		if data_value is None:
			print(f'> Skipping placeholder {placeholder} as field {field_value} is not present in the data')
			continue
		field_value_str = str(data_value)
		html_text = field_value_str.replace('\n', '<br>').replace('\r', '')
		template_html = template_html.replace(placeholder, html_text)
		# print(f'> {placeholder} ==> {html_text}')
	# Replace ad-hoc content
	print('> Replacing ad-hoc content...')
	ad_hoc_placeholders = re.findall(r'\[\[\[\[[\w-]+\]\]\]\]', template_html)
	for placeholder in ad_hoc_placeholders:
		field_value = placeholder[4:-4]
		data_value = get_value_from_json(data, field_value)[0]
		if data_value is None:
			print(f'> Skipping placeholder {placeholder} as field {field_value} is not present in the data')
			continue
		# Check the field name to determine the type of content
		if field_value == 'features_text_list':
			# Get each text element from the list and create a new div HTML element for each to append to the parent element
			text_list = ''
			for text in data_value:
				text_list += f'<div>{text}</div>'
			template_html = template_html.replace(placeholder, text_list)
		elif ['screenshots', 'animated-gifs', 'key-art-logos', 'png-logos'].count(field_value) > 0:
			# For each element of the data, which is a json object with attributes 'src' and 'large' (bool), create a new div HTML element for each to append to the parent element
			images_list = ''
			image_row_html_start = '<div class="images-section-row">'
			image_row_single_html_start = '<div class="images-section-row single-image">'
			image_row_html_end = '</div>'
			added_in_row = 0
			for image,i in zip(data_value, range(len(data_value))):
				close_row = False
				if added_in_row == 0:
					if image['large']:
						images_list += image_row_single_html_start
					else:
						images_list += image_row_html_start
				alt_text = data["general"]["name"] + ' ' + field_value[:-1].capitalize() + ' ' + str(data[field_value].index(image) + 1)
				additional_attributes = ''
				if "additional_attributes" in image:
					for attr_text in image["additional_attributes"]:
						additional_attributes += attr_text + ' '
				img_name = image["src"].split('/')[-1].split('.')[0]
				images_list += f'<img src="{image["src"]}" alt="{alt_text}" {additional_attributes} title="{img_name}"/>'
				added_in_row += 1
				if added_in_row >= 2 or image['large']:
					close_row = True
				if close_row:
					images_list += image_row_html_end
					added_in_row = 0
			# images_list += image_row_html_end
			template_html = template_html.replace(placeholder, images_list)
		else:
			# Unknown field name
			print(f'> Unknown "list" field name: {field_value}')
	# Check if there are some placeholders that were not replaced
	print("\nChecking for missing placeholders...")
	remaining_text_placeholders = re.findall(r'\{\{\{\{[\w-]+\}\}\}\}', template_html)
	remaining_ad_hoc_placeholders = re.findall(r'\[\[\[\[[\w-]+\]\]\]\]', template_html)
	remaining_placeholders = remaining_text_placeholders + remaining_ad_hoc_placeholders
	hidden_parent_elements = []
	for placeholder in remaining_placeholders:
		print(f'> Placeholder {placeholder} was not replaced...')
		# Find the corresponding field name and check its parent
		field_value = get_value_from_json(data, placeholder[4:-4])[0]
		parent_name = get_value_from_json(template_data, placeholder[4:-4])[1]
		# print(f'  - Field value: {field_value} - Parent name: {parent_name}')
		# Hide the parent element if needed
		if data[parent_name] is None:
			# Elements IDs to hide if not present
			parent_elements_to_hide = [
				"trailer", 
				"screenshots", "animated-gifs", "key-art-logos", "png-logos",
				"all-images"
			]
			if parent_elements_to_hide.count(parent_name) > 0:
				# Find element with id equal to the parent name and hide it completely, by adding to its class attribute (if present on the same line, otherwise add class attribute) class "hidden"
				html_element = re.search(fr'<div id="{parent_name}".*?>', template_html)
				side_menu_anchor_element = re.search(fr'<div.*?href=["\']#{parent_name}["\']>.*?</div>', template_html)
				if html_element is not None and hidden_parent_elements.count(parent_name) == 0:
					# Hide the HTML element
					html_element = html_element.group()
					if 'class' in html_element:
						template_html = template_html.replace(html_element, html_element.replace('class="', 'class="hidden '))
					else:
						template_html = template_html.replace(html_element, html_element.replace('<div', '<div class="hidden"'))
					# Hide the side menu anchor element (add class "hidden" to the anchor element)
					if side_menu_anchor_element is not None:
						side_menu_anchor_element = side_menu_anchor_element.group()
						if 'class' in side_menu_anchor_element:
							template_html = template_html.replace(side_menu_anchor_element, side_menu_anchor_element.replace('class="', 'class="hidden '))
						else:
							template_html = template_html.replace(side_menu_anchor_element, side_menu_anchor_element.replace('<div', '<div class="hidden"'))
					# Add the parent element to the list of hidden elements
					hidden_parent_elements.append(parent_name)
				print(f'  - Hiding parent field element {parent_name}...')
			else:
				# Do not hide the parent, as there might be an error
				print(f'  - ERROR: Placeholder {placeholder} was not replaced and parent field element {parent_name} cannot be removed...')
		else:
			# Hide the single element in the line if only some of its child elements are missing
			if placeholder[0] == '{':
				# Search for each line that contains the "placeholder" text and hide it (disregard the parent element)
				template_html = re.sub(r'<div.*?' + placeholder + r'.*?</div>', '', template_html)
				print("  - Hiding placeholder element")
			else:
				# Do not hide the single element in the line if only some of its child elements are missing
				print(f'  - ERROR: Placeholder {placeholder} was not replaced and its inline field element cannot be removed...')
	print("DONE: checked for missing placeholders")

	# Return the HTML content
	return template_html

def main(game_identifier):

	# Load JSON data from file
	json_data = {}
	with open(f'json/{game_identifier}.json', 'r', encoding='utf-8') as json_file:
		json_data = json.load(json_file)

	# Generate HTML content
	html_content = json_to_html(json_data)

	# Save HTML content to file
	print('\nSaving HTML content...')
	# Check if an HTML page with the same name we are trying to create already exists, in this case, copy it to a new file in the "temp" folder
	if os.path.exists(game_identifier + '.html'):
		print(f'> File {game_identifier}.html already exists, moving it to "temp" folder to save a new one')
		counter = 1
		if not os.path.exists('temp'):
			os.makedirs('temp')
		while os.path.exists(f'temp/{game_identifier}_{counter}.html'):
			counter += 1
		os.rename(game_identifier + '.html', f'temp/{game_identifier}_{counter}.html')
	# Save HTML content to file
	with open(game_identifier + '.html', 'w', encoding='utf-8') as html_file:
		html_file.write(html_content)
	print(f'> HTML content saved to {game_identifier}.html')

# Script to launch with "python script.py game_identifier"
if __name__ == '__main__':
	if len(sys.argv) < 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help' or sys.argv[1] == '-help':
		print("\nUSAGE:")
		print("\t> python script.py main")
		print("\t  Updates the games in the main page (main.html) of the website (for when I add a new game to the list of my gaems on the website).")
		print("\t> python script.py <game_identifier>")
		print("\t  Generates the HTML page for the game with the given identifier.")
		sys.exit(1)
	game_identifier = sys.argv[1]
	main(game_identifier)